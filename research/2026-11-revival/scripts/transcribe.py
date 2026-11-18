"""Transcribe the Skyborne voice files on fal.ai, with a hard spend cap (report 5).

Usage, with FAL_KEY in the environment:
  python3 -I transcribe.py <listener> <ledger.jsonl> <out.jsonl> <budget_usd> <file.ogg> [...]
  python3 -I transcribe.py <listener> <ledger.jsonl> <out.jsonl> <budget_usd> @<list.txt>   (one path a line)
listener: wizper (Whisper v3), scribe (ElevenLabs Scribe v2), gemini-pro or gemini-flash (through fal's
audio router). The language models get a blind prompt: it never says what a line is for or which words to
expect.

Every call is appended to the ledger, and a call is refused when the ledger total plus that listener's
estimate would pass the budget. The router reports each call's cost. Wizper and Scribe are logged at fal's
listed price as an upper bound: Wizper at $0.00111 a second of wall time (upload included), Scribe at a
whole minute ($0.008) per call. Rejected requests (HTTP 4xx) are logged at $0, because fal bills only
completed ones; any other failure is logged at the listener's estimate. A call can cost more than its
estimate (a slow Wizper call), so the ledger can pass the budget by that overrun. Run listeners in parallel
only with headroom under the cap: each process checks the ledger before its own call.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROUTER_MODELS = {"gemini-pro": "google/gemini-3.1-pro-preview", "gemini-flash": "google/gemini-3.8-flash"}
ESTIMATE = {"gemini-pro": 0.05, "gemini-flash": 0.01, "scribe": 0.008, "wizper": 0.006}
_UPLOADED = {}  # local path -> fal file URL, so each process uploads a file once

PROMPT = """You are a phonetician transcribing a short game voice recording. The speaker may be speaking English, or a
constructed fantasy language that is not any real language. Do not translate and do not guess meanings.

Return only JSON with these keys:
"speech": true or false (false for pure grunts, laughs, sighs, breaths or effort sounds),
"language": "english", "non-english", "mixed" or "none",
"english_text": the exact English words if any English is spoken, else "",
"ipa": a narrow IPA transcription of everything spoken (non-English parts especially), else "",
"romanized": the non-English parts spelled with plain Latin letters, a e i o u for vowels, sh, th, dh, kh for those
sounds, and an apostrophe where a clear break or glottal stop separates parts of a word; "" if none,
"syllables": the romanized form split into syllables with hyphens,
"confidence": "high", "medium" or "low" for the non-English transcription,
"notes": anything uncertain (for example which consonant it could also be)."""


def _request(url, payload):
    return urllib.request.Request(url, data=json.dumps(payload).encode(), headers={
        "Authorization": "Key " + os.environ["FAL_KEY"], "Content-Type": "application/json"})


def upload(path):
    """Upload a file to fal storage once. fal reads the audio format from the URL's extension and rejects
    data URIs (it sees them as .bin)."""
    if path not in _UPLOADED:
        initiate = _request("https://rest.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3",
                            {"content_type": "audio/ogg", "file_name": os.path.basename(path)})
        with urllib.request.urlopen(initiate, timeout=60) as r:
            target = json.load(r)
        with open(path, "rb") as f:
            put = urllib.request.Request(target["upload_url"], data=f.read(), method="PUT",
                                         headers={"Content-Type": "audio/ogg"})
        urllib.request.urlopen(put, timeout=60).close()
        _UPLOADED[path] = target["file_url"]
    return _UPLOADED[path]


def post(endpoint, payload):
    try:
        with urllib.request.urlopen(_request("https://fal.run/" + endpoint, payload), timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]!r}") from e


def spent(ledger):
    if not os.path.exists(ledger):
        return 0.0
    with open(ledger, encoding="utf-8") as f:
        return sum(json.loads(line)["cost"] for line in f if line.strip())


def call(listener, path):
    """Return (output text, cost in USD, how the cost was found, wall seconds)."""
    t0 = time.time()
    if listener in ROUTER_MODELS:
        # The router refuses reasoning=False for these models.
        res = post("openrouter/router/audio", {"model": ROUTER_MODELS[listener], "prompt": PROMPT,
                                               "audio_url": upload(path), "temperature": 0,
                                               "max_tokens": 4000, "reasoning": True})
        cost = (res.get("usage") or {}).get("cost")
        if cost is None:
            return res.get("output", ""), ESTIMATE[listener], "estimate (no usage.cost)", time.time() - t0
        return res.get("output", ""), float(cost), "router usage.cost", time.time() - t0
    if listener == "scribe":
        res = post("fal-ai/elevenlabs/speech-to-text/scribe-v2", {"audio_url": upload(path), "tag_audio_events": True})
        text = json.dumps({"text": res.get("text"), "language": res.get("language_code")}, ensure_ascii=False)
        return text, 0.008, "listed price, one minute per call", time.time() - t0
    if listener == "wizper":
        res = post("fal-ai/wizper", {"audio_url": upload(path), "task": "transcribe", "version": "3"})
        wall = time.time() - t0
        text = json.dumps({"text": res.get("text"), "languages": res.get("languages")}, ensure_ascii=False)
        return text, round(0.00111 * wall, 5), "listed price x wall seconds", wall
    raise SystemExit("unknown listener: " + listener)


def main():
    if len(sys.argv) < 6:
        raise SystemExit(__doc__)
    listener, ledger, out, budget, *files = sys.argv[1:]
    if listener not in ESTIMATE:
        raise SystemExit("unknown listener: " + listener)
    if not os.environ.get("FAL_KEY"):
        # Without it every call fails locally and would be logged at its estimate: spend that never happened.
        raise SystemExit("FAL_KEY is not set")
    budget = float(budget)
    if len(files) == 1 and files[0].startswith("@"):
        with open(files[0][1:], encoding="utf-8") as f:
            files = [line.strip() for line in f if line.strip()]
    missing = [p for p in files if not os.path.isfile(p)]
    if missing:
        raise SystemExit(f"missing files: {missing[:3]}")
    for path in files:
        total = spent(ledger)
        if total + ESTIMATE[listener] > budget:
            print(f"STOP: ledger ${total:.4f} + estimate ${ESTIMATE[listener]} would pass ${budget}")
            break
        t0 = time.time()
        try:
            text, cost, basis, wall = call(listener, path)
        except Exception as e:  # keep going; an unclear failure is logged at its estimate
            rejected = str(e).startswith("HTTP 4")
            text, wall = f"ERROR {e}", time.time() - t0
            cost, basis = (0.0, "rejected (HTTP 4xx)") if rejected else (ESTIMATE[listener], "estimate (error)")
        with open(ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps({"listener": listener, "file": os.path.basename(path), "cost": cost, "basis": basis}) + "\n")
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps({"listener": listener, "file": path, "output": text, "cost": cost,
                                "wall": round(wall, 2)}, ensure_ascii=False) + "\n")
        print(f"{os.path.basename(path)} ${cost:.5f} total ${spent(ledger):.4f}")


if __name__ == "__main__":
    main()
