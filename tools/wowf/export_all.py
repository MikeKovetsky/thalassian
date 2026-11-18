#!/usr/bin/env python3
"""Turn the raw client files pulled into .wowf-extract/raw/ into readable dumps.

  python3 -I tools/wowf/export_all.py --base .wowf-extract --build 1.60.1.70938

Reads:   raw/casc/dbfilesclient/*.db2, raw/cache/DBCache.bin, raw/cache/*.wdb,
         raw/root.csv, _vendor/WoWDBDefs, _vendor/community-listfile.csv
Writes:  db2/<Table>.csv            every client DB2 table as shipped in CASC
         hotfix/<Table>.csv         rows the server pushed (DBCache.bin)
         <Table>.csv                key tables merged (DB2 + hotfix), _source column
         wdb_strings.jsonl          strings per creature/quest/object/page cache record
         files_in_build.csv         every FileDataID in this build's root, with listfile path
         corpus.jsonl               every string with its location, for token mining
         summary.json               row counts and notes
"""
import argparse
import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import db2 as db2mod  # noqa: E402
import hotfix as hfmod  # noqa: E402
import wdb as wdbmod  # noqa: E402

csv.field_size_limit(1 << 30)

KEY_TABLES = [
    "BroadcastText", "LanguageWords", "Languages", "ChrRaces", "ChrClasses", "Creature",
    "AreaTable", "Map", "MapDifficulty", "ItemSparse", "ItemSearchName", "SpellName", "Spell",
    "Achievement", "Toy", "Mount", "QuestV2", "GlobalStrings", "SoundKit", "SoundKitEntry",
    "CharTitles", "Faction", "ZoneMusic", "ZoneIntroMusicTable", "UiMap", "JournalInstance",
    "JournalEncounter", "Emotes", "EmotesText", "EmotesTextData", "ChrCustomizationOption",
    "ChrCustomizationChoice", "CreatureFamily", "CreatureType", "WMOAreaTable", "TaxiNodes",
    "PlayerChoice", "PlayerChoiceResponse", "BroadcastTextDuration", "NamesReserved",
    "NamesProfanity", "Cfg_Regions", "Cfg_Categories", "LoadingScreenTaxiSplines", "Movie",
    "MovieVariation", "CinematicSequences", "SkillLine", "SkillLineAbility", "ItemSet",
    "ItemNameDescription", "CurrencyTypes", "GameObjects", "SpellAuraNames", "MailTemplate", "NameGen",
    "ChrRaceRacialAbility", "QuestSort", "TransmogSet", "NPCSounds", "CreatureSoundData",
]


def load_defs(dbd_root):
    d = os.path.join(dbd_root, "definitions")
    return {os.path.splitext(n)[0].lower(): os.path.join(d, n) for n in os.listdir(d) if n.endswith(".dbd")}


def string_fields(version):
    return [f for f in version.fields if f.type in ("string", "locstring")]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--build", required=True)
    a = ap.parse_args(argv)
    base = a.base
    vendor = os.path.join(base, "_vendor")
    dbd_root = os.path.join(vendor, "WoWDBDefs")
    defs = load_defs(dbd_root)
    summary = {"build": a.build, "db2": {}, "hotfix": {}, "merged": {}, "notes": []}
    corpus = open(os.path.join(base, "corpus.jsonl"), "w", encoding="utf-8")

    def emit(text, where, **extra):
        if text and isinstance(text, str) and any(c.isalpha() for c in text):
            rec = {"text": text, "where": where}
            rec.update(extra)
            corpus.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # ---- 1. every DB2 in CASC ----
    os.makedirs(os.path.join(base, "db2"), exist_ok=True)
    db2_rows = {}
    for path in sorted(glob.glob(os.path.join(base, "raw", "casc", "dbfilesclient", "*.db2"))):
        lname = os.path.splitext(os.path.basename(path))[0]
        dpath = defs.get(lname)
        if not dpath:
            summary["db2"][lname] = {"error": "no DBD definition"}
            continue
        dbd = db2mod.DBD(dpath)
        try:
            t = db2mod.DB2(path, dbd, a.build)
            rows = list(t.rows())
        except Exception as e:  # keep going; record why
            summary["db2"][dbd.name] = {"error": str(e)[:200]}
            continue
        flat = [db2mod.flatten(r, t.version) for r in rows]
        for fr, r in zip(flat, rows):
            fr["_id"] = r["_id"]
        db2mod.write_csv(os.path.join(base, "db2", dbd.name + ".csv"), ["_id"] + t.columns(), flat)
        info = {"rows": len(rows), "layout": t.layout, "sections": t.section_count}
        if t.encrypted_sections:
            info["encrypted_sections_unreadable"] = t.encrypted_sections
        summary["db2"][dbd.name] = info
        db2_rows[dbd.name] = (t.version, rows)
        for f in string_fields(t.version):
            for r in rows:
                v = r.get(f.name)
                for k, s in enumerate(v if isinstance(v, list) else [v]):
                    emit(s, "db2:%s#%s.%s%s" % (dbd.name, r["_id"], f.name, "[%d]" % k if isinstance(v, list) else ""),
                         table=dbd.name, id=r["_id"], field=f.name, src="db2")

    # ---- 2. hotfixes ----
    hdir = os.path.join(base, "hotfix")
    hfmod.main(["--cache", os.path.join(base, "raw", "cache", "DBCache.bin"), "--dbd", dbd_root,
                "--build", a.build, "--out", hdir])
    hsum = json.load(open(os.path.join(hdir, "_summary.json")))
    hot_rows = {}
    for tinfo in hsum["tables"]:
        summary["hotfix"][tinfo["table"]] = {k: v for k, v in tinfo.items() if k != "table"}
        p = os.path.join(hdir, tinfo["table"] + ".csv")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                hot_rows[tinfo["table"]] = list(csv.DictReader(fh))
        sp = os.path.join(hdir, tinfo["table"] + ".status.csv")
        if os.path.exists(sp):
            with open(sp, encoding="utf-8") as fh:
                hot_rows.setdefault(tinfo["table"] + ".status", list(csv.DictReader(fh)))
    for tname, rows in hot_rows.items():
        if tname.endswith(".status"):
            continue
        dp = defs.get(tname.lower())
        if not dp:
            continue
        v = db2mod.DBD(dp).find(a.build)
        if v is None:
            continue
        for f in string_fields(v):
            for r in rows:
                cols = ["%s[%d]" % (f.name, i) for i in range(f.array)] if f.array > 1 else [f.name]
                for c in cols:
                    emit(r.get(c), "hotfix:%s#%s.%s (push %s)" % (tname, r["_record_id"], c, r["_push_id"]),
                         table=tname, id=int(r["_record_id"]), field=c, src="hotfix", push=r["_push_id"])

    # ---- 3. merged key tables ----
    for tname in KEY_TABLES:
        have_db2 = tname in db2_rows
        have_hot = tname in hot_rows
        if not have_db2 and not have_hot:
            continue
        if have_db2:
            version = db2_rows[tname][0]
        else:
            dp = defs.get(tname.lower())
            version = db2mod.DBD(dp).find(a.build) if dp else None
            if version is None:
                continue
        cols = []
        for f in version.fields:
            cols += ["%s[%d]" % (f.name, i) for i in range(f.array)] if f.array > 1 else [f.name]
        merged = {}
        if have_db2:
            for r in db2_rows[tname][1]:
                fr = db2mod.flatten(r, version)
                fr["_id"] = r["_id"]
                fr["_source"] = "db2"
                merged[int(r["_id"])] = fr
        deleted = set()
        for st in hot_rows.get(tname + ".status", []):
            if st["status"] == "deleted":
                deleted.add(int(st["record_id"]))
        for r in hot_rows.get(tname, []):
            rid = int(r["_record_id"])
            fr = {c: r.get(c, "") for c in cols}
            fr["_id"] = rid
            fr["_source"] = "hotfix:push%s" % r["_push_id"] + (":overrides-db2" if rid in merged else "")
            merged[rid] = fr
        for rid in deleted:
            if rid in merged and merged[rid]["_source"] == "db2":
                merged[rid]["_source"] = "db2:deleted-by-hotfix"
        out = [merged[k] for k in sorted(merged)]
        db2mod.write_csv(os.path.join(base, tname + ".csv"), ["_id", "_source"] + cols, out)
        summary["merged"][tname] = {"rows": len(out),
                                   "from_db2": sum(1 for r in out if r["_source"].startswith("db2")),
                                   "from_hotfix": sum(1 for r in out if r["_source"].startswith("hotfix"))}

    # ---- 4. WDB caches ----
    wdb_files = sorted(glob.glob(os.path.join(base, "raw", "cache", "*.wdb")))
    wout = os.path.join(base, "wdb_strings.jsonl")
    wdbmod.main(["--out", wout] + wdb_files)
    wcount = {}
    with open(wout, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            wcount[r["cache"]] = wcount.get(r["cache"], 0) + 1
            for k, s in enumerate(r["strings"]):
                emit(s, "wdb:%s#%d[%d]" % (r["cache"], r["id"], k), table=r["cache"], id=r["id"], src="wdb")
    summary["wdb"] = wcount

    # ---- 5. files in this build, named by the community listfile ----
    names = {}
    with open(os.path.join(vendor, "community-listfile.csv"), encoding="utf-8", errors="replace") as fh:
        for line in fh:
            fd, _, p = line.rstrip("\n").partition(";")
            if fd.isdigit():
                names[int(fd)] = p
    # one row per FileDataID; a file can have several root records (one per
    # locale or content variant), so OR the locale masks and the on-disk flags
    agg = {}
    with open(os.path.join(base, "raw", "root.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            fd = int(r["fdid"])
            loc, cont, local = int(r["locale"], 16), int(r["content"], 16), r["local"] == "1"
            if fd in agg:
                a0 = agg[fd]
                agg[fd] = (a0[0] | loc, a0[1] | cont, a0[2] or local)
            else:
                agg[fd] = (loc, cont, local)
    n_named = n_local = 0
    with open(os.path.join(base, "files_in_build.csv"), "w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["fdid", "path", "locale_mask", "content_flags", "present_locally"])
        for fd in sorted(agg):
            loc, cont, local = agg[fd]
            p = names.get(fd, "")
            n_named += bool(p)
            n_local += local
            w.writerow([fd, p, "%08x" % loc, "%08x" % cont, int(local)])
            if p.startswith("sound/") and ("vo_" in p or "/creature/" in p or "/dialog" in p):
                emit(os.path.basename(p), "listfile:%d %s" % (fd, p), src="listfile", id=fd)
    summary["files_in_build"] = {"fdids": len(agg), "named_by_listfile": n_named, "present_locally": n_local}
    corpus.close()
    with open(os.path.join(base, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    ok = sum(1 for v in summary["db2"].values() if "rows" in v)
    print("db2 tables parsed", ok, "of", len(summary["db2"]))
    print("merged", json.dumps(summary["merged"], indent=0))


if __name__ == "__main__":
    main()
