"""research/2026-11-revival/scripts/transcribe.py: the spend cap, the cost of each call, and the key.

No request leaves the machine: urllib.request.urlopen is replaced by a fake that answers by URL.
"""
import contextlib
import io
import itertools
import json
import os
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research", "2026-11-revival", "scripts"))
import transcribe  # noqa: E402

KEY = "test-key-not-a-real-fal-key"
INITIATE_URL = "https://rest.fal.ai/storage/upload/initiate"
PUT_URL = "https://upload.example/put"
WIZPER_URL = "https://fal.run/fal-ai/wizper"
SCRIBE_URL = "https://fal.run/fal-ai/elevenlabs/speech-to-text/scribe-v2"
ROUTER_URL = "https://fal.run/openrouter/router/audio"
UPLOAD = {INITIATE_URL: {"upload_url": PUT_URL, "file_url": "https://cdn.example/line.ogg"}, PUT_URL: {}}
SCRIBE = dict(UPLOAD, **{SCRIBE_URL: {"text": "Banu Allah", "language_code": "eng"}})


class FakeFal:
    """Stands in for urlopen: records every request and answers it by URL prefix."""

    def __init__(self, answers):
        self.answers = answers
        self.requests = []

    def __call__(self, request, timeout=None):
        self.requests.append(request)
        for prefix, answer in self.answers.items():
            if request.full_url.startswith(prefix):
                if isinstance(answer, Exception):
                    raise answer
                return io.BytesIO(json.dumps(answer).encode())
        raise AssertionError("unexpected request to " + request.full_url)


class TestTranscribe(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.ledger = os.path.join(tmp.name, "ledger.jsonl")
        self.out = os.path.join(tmp.name, "out.jsonl")
        self.files = []
        for i in range(3):
            path = os.path.join(tmp.name, f"line_{i}.ogg")
            with open(path, "wb") as fh:
                fh.write(b"OggS")
            self.files.append(path)
        transcribe._UPLOADED.clear()
        env = mock.patch.dict(os.environ, {"FAL_KEY": KEY})
        env.start()
        self.addCleanup(env.stop)

    def run_main(self, listener, budget, files, answers):
        fal = FakeFal(answers)
        argv = ["transcribe.py", listener, self.ledger, self.out, str(budget), *files]
        with mock.patch.object(transcribe.urllib.request, "urlopen", fal), mock.patch.object(sys, "argv", argv), \
                contextlib.redirect_stdout(io.StringIO()):
            transcribe.main()
        return fal

    def rows(self, path):
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def test_no_call_when_the_ledger_and_the_estimate_would_pass_the_budget(self):
        with open(self.ledger, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"listener": "gemini-pro", "file": "x.ogg", "cost": 2.995, "basis": "router"}) + "\n")
        fal = self.run_main("scribe", 3, self.files, SCRIBE)
        self.assertEqual((fal.requests, len(self.rows(self.ledger)), self.rows(self.out)), ([], 1, []))

    def test_calls_stop_once_the_next_estimate_would_pass_the_budget(self):
        self.run_main("scribe", 0.02, self.files, SCRIBE)  # $0.008 a call: two fit under $0.02, a third would not
        self.assertEqual([r["cost"] for r in self.rows(self.ledger)], [0.008, 0.008])
        self.assertEqual(len(self.rows(self.out)), 2)

    def test_rejected_request_costs_nothing_and_other_failures_their_estimate(self):
        rejected = urllib.error.HTTPError(WIZPER_URL, 422, "Unprocessable Entity", {}, io.BytesIO(b'{"detail": 1}'))
        self.run_main("wizper", 3, self.files[:1], dict(UPLOAD, **{WIZPER_URL: rejected}))
        self.run_main("wizper", 3, self.files[1:2], dict(UPLOAD, **{WIZPER_URL: urllib.error.URLError("timed out")}))
        self.assertEqual([(r["cost"], r["basis"]) for r in self.rows(self.ledger)],
                         [(0.0, "rejected (HTTP 4xx)"), (transcribe.ESTIMATE["wizper"], "estimate (error)")])
        self.assertTrue(all(r["output"].startswith("ERROR") for r in self.rows(self.out)))

    def test_router_cost_is_the_reported_one_or_else_the_estimate(self):
        self.run_main("gemini-pro", 3, self.files[:1], dict(UPLOAD, **{ROUTER_URL: {"output": "{}", "usage": {"cost": 0.0123}}}))
        self.run_main("gemini-flash", 3, self.files[1:2], dict(UPLOAD, **{ROUTER_URL: {"output": "{}"}}))
        self.assertEqual([(r["cost"], r["basis"]) for r in self.rows(self.ledger)],
                         [(0.0123, "router usage.cost"), (transcribe.ESTIMATE["gemini-flash"], "estimate (no usage.cost)")])

    def test_wizper_costs_its_wall_time_and_keeps_the_detected_languages(self):
        clock = itertools.count(100.0, 2.0)  # each reading of the clock is 2 s after the last
        answer = {"text": "Banu Allah.", "chunks": [], "languages": ["en"]}
        with mock.patch.object(transcribe.time, "time", lambda: next(clock)):
            self.run_main("wizper", 3, self.files[:1], dict(UPLOAD, **{WIZPER_URL: answer}))
        [row] = self.rows(self.ledger)
        self.assertEqual((row["cost"], row["basis"]), (0.00222, "listed price x wall seconds"))
        self.assertEqual(json.loads(self.rows(self.out)[0]["output"]), {"text": "Banu Allah.", "languages": ["en"]})

    def test_refuses_to_start_without_a_key(self):
        with mock.patch.dict(os.environ):
            del os.environ["FAL_KEY"]
            with self.assertRaises(SystemExit):
                self.run_main("scribe", 3, self.files, SCRIBE)
        self.assertEqual(self.rows(self.ledger), [])

    def test_key_goes_only_to_fal_and_is_written_nowhere(self):
        fal = self.run_main("scribe", 3, self.files[:1], SCRIBE)
        sent = {urllib.parse.urlsplit(r.full_url).hostname: r.get_header("Authorization") for r in fal.requests}
        self.assertEqual(sent, {"rest.fal.ai": "Key " + KEY, "upload.example": None, "fal.run": "Key " + KEY})
        for path in (self.ledger, self.out):
            with open(path, encoding="utf-8") as fh:
                self.assertNotIn(KEY, fh.read())

    def test_each_file_is_uploaded_once(self):
        fal = FakeFal(SCRIBE)
        with mock.patch.object(transcribe.urllib.request, "urlopen", fal):
            transcribe.call("scribe", self.files[0])
            transcribe.call("scribe", self.files[0])
        self.assertEqual([r.full_url.startswith(INITIATE_URL) for r in fal.requests].count(True), 1)


if __name__ == "__main__":
    unittest.main()
