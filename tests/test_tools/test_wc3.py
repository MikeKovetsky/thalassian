"""tools/wc3: the MPQ reader, the map and subtitle parsers, the extractor's map status and the miner."""
import bz2
import contextlib
import io
import json
import os
import shutil
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools", "wc3"))
import extract_text  # noqa: E402
import mine  # noqa: E402
import mpq  # noqa: E402

M32 = 0xFFFFFFFF


# --------------------------------------------------------------------------
# a reference Storm hash and cipher, written from the format description, to build test archives
# --------------------------------------------------------------------------
def ref_crypt_table():
    table, seed = [0] * 0x500, 0x00100001
    for i in range(0x100):
        for j in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            hi = (seed & 0xFFFF) << 16
            seed = (seed * 125 + 3) % 0x2AAAAB
            table[i + j * 0x100] = hi | (seed & 0xFFFF)
    return table


CRYPT = ref_crypt_table()


def ref_hash(name, kind):
    """Storm's hash of raw name bytes: ASCII letters upper-cased, '/' read as '\\'."""
    seed1, seed2 = 0x7FED7FED, 0xEEEEEEEE
    for ch in name:
        ch = ch - 0x20 if 0x61 <= ch <= 0x7A else 0x5C if ch == 0x2F else ch
        seed1 = CRYPT[(kind << 8) + ch] ^ ((seed1 + seed2) & M32)
        seed2 = (ch + seed1 + seed2 + (seed2 << 5) + 3) & M32
    return seed1


def ref_encrypt(data, key):
    n = len(data) // 4
    out, seed = [], 0xEEEEEEEE
    for (v,) in struct.iter_unpack("<I", data[:n * 4]):
        seed = (seed + CRYPT[0x400 + (key & 0xFF)]) & M32
        out.append(v ^ ((key + seed) & M32))
        key = ((((~key) << 0x15) + 0x11111111) & M32) | (key >> 0x0B)
        seed = (v + seed + (seed << 5) + 3) & M32
    return struct.pack("<%dI" % n, *out) + data[n * 4:]


EXISTS, COMPRESS, ENCRYPTED, FIX_KEY, SINGLE = 0x80000000, 0x200, 0x10000, 0x20000, 0x01000000


def build_mpq(files, sector_shift=0, prefix=b""):
    """files: [(name bytes, content bytes, flags, compressor)] -> archive bytes, MPQ at len(prefix)."""
    sector = 512 << sector_shift
    body = b""
    blocks = []
    for name, content, flags, comp in files:
        off = 32 + len(body)
        key = ref_hash(name.replace(b"/", b"\\").split(b"\\")[-1], 3)
        if flags & FIX_KEY:
            key = ((key + off) ^ len(content)) & M32
        if flags & SINGLE:
            blob = comp(content) if flags & COMPRESS else content
            if flags & ENCRYPTED:
                blob = ref_encrypt(blob, key)
        else:
            chunks = [content[i:i + sector] for i in range(0, len(content), sector)]
            if flags & COMPRESS:
                chunks = [c2 if len(c2) < len(c) else c for c, c2 in ((c, comp(c)) for c in chunks)]
            if flags & ENCRYPTED:
                chunks = [ref_encrypt(c, (key + s) & M32) for s, c in enumerate(chunks)]
            if flags & COMPRESS:
                offs = [4 * (len(chunks) + 1)]
                for c in chunks:
                    offs.append(offs[-1] + len(c))
                table = struct.pack("<%dI" % len(offs), *offs)
                if flags & ENCRYPTED:
                    table = ref_encrypt(table, (key - 1) & M32)
                chunks = [table] + chunks
            blob = b"".join(chunks)
        blocks.append((off, len(blob), len(content), flags | EXISTS))
        body += blob
    nhash = 16
    table = [(M32, M32, 0xFFFF, 0xFFFF, M32)] * nhash
    for bi, (name, _c, _f, _comp) in enumerate(files):
        i = ref_hash(name, 0) % nhash
        while table[i][4] != M32:
            i = (i + 1) % nhash
        table[i] = (ref_hash(name, 1), ref_hash(name, 2), 0, 0, bi)
    hraw = b"".join(struct.pack("<IIHHI", *e) for e in table)
    braw = b"".join(struct.pack("<IIII", *b) for b in blocks)
    hpos = 32 + len(body)
    bpos = hpos + len(hraw)
    header = struct.pack("<4sIIHHIIII", b"MPQ\x1a", 32, bpos + len(braw), 0, sector_shift, hpos, bpos,
                         nhash, len(blocks))
    return prefix + header + body + ref_encrypt(hraw, ref_hash(b"(hash table)", 3)) + \
        ref_encrypt(braw, ref_hash(b"(block table)", 3))


def zlib_sector(data):
    return b"\x02" + zlib.compress(data)


def bzip2_sector(data):
    return b"\x10" + bz2.compress(data)


WTS = ("STRING 1\r\n{\r\n" + "Shan'do Stormrage will be defenseless! " * 40 + "\r\n}\r\n").encode()
SCRIPT = ("function main takes nothing returns nothing\n" * 60).encode()
SECRET = b"Ishnu-alah, sisters! (30 bytes)"[:30]
CP1252_NAME = b"caf\xe9.txt"  # not UTF-8: older maps name members in the system code page


def sample_archive(prefix=b""):
    return build_mpq([
        (b"(listfile)", b"war3map.wts\r\nscripts\\war3map.j\r\nsecret.txt\r\n" + CP1252_NAME + b"\r\n", 0, None),
        (b"war3map.wts", WTS, COMPRESS, zlib_sector),
        (b"scripts\\war3map.j", SCRIPT, COMPRESS | ENCRYPTED | FIX_KEY, bzip2_sector),
        (b"secret.txt", SECRET, SINGLE | ENCRYPTED | FIX_KEY, None),
        (CP1252_NAME, b"plain", SINGLE, None),
    ], prefix=prefix)


class StormHash(unittest.TestCase):
    def test_known_answers(self):
        # the table keys every MPQ reader uses, and the (listfile) name hashes seen in real archives
        self.assertEqual(mpq.CRYPT[0], 0x55C636E2)
        self.assertEqual(mpq.hash_string("(hash table)", mpq.HASH_KEY), 0xC3AF3770)
        self.assertEqual(mpq.hash_string("(block table)", mpq.HASH_KEY), 0xEC83B3A3)
        self.assertEqual(mpq.hash_string("(listfile)", mpq.HASH_A), 0xFD657910)
        self.assertEqual(mpq.hash_string("(listfile)", mpq.HASH_B), 0x4E9B98A7)

    def test_case_and_slash_insensitive(self):
        for kind in range(4):
            self.assertEqual(mpq.hash_string("Scripts/War3map.j", kind),
                             mpq.hash_string("SCRIPTS\\WAR3MAP.J", kind))

    def test_non_ascii_names_hash_their_raw_bytes(self):
        # Storm upper-cases ASCII only: e-acute is hashed as its two UTF-8 bytes, never as E-acute
        self.assertEqual(mpq.hash_string("café", 1), ref_hash("café".encode("utf-8"), 1))
        self.assertNotEqual(mpq.hash_string("café", 1), mpq.hash_string("cafÉ", 1))
        self.assertEqual(mpq.hash_string(CP1252_NAME.decode("utf-8", "surrogateescape"), 2),
                         ref_hash(CP1252_NAME, 2))


class Reader(unittest.TestCase):
    def test_round_trip(self):
        m = mpq.MPQ(sample_archive())
        self.assertEqual(sorted(mpq.display_name(n) for n in m.listfile()),
                         ["caf�.txt", "scripts\\war3map.j", "secret.txt", "war3map.wts"])
        self.assertEqual(m.read("war3map.wts"), WTS)                 # zlib sectors
        self.assertEqual(m.read("Scripts/War3map.J"), SCRIPT)        # bzip2, encrypted, fix key
        self.assertEqual(m.read("secret.txt"), SECRET)              # single unit, tail not a word
        cp = [n for n in m.listfile() if n.startswith("caf")][0]
        self.assertEqual(m.read(cp), b"plain")                      # a name that is not UTF-8

    def test_header_found_at_a_512_boundary_only(self):
        prefix = b"HM3W" + b"\0" * 96 + b"MPQ\x1a" + b"\0" * 408  # a decoy header at offset 100
        m = mpq.MPQ(sample_archive(prefix))
        self.assertEqual(m.base, 512)
        self.assertEqual(m.read("war3map.wts"), WTS)

    def test_missing_member(self):
        with self.assertRaises(KeyError):
            mpq.MPQ(sample_archive()).read("war3map.lua")

    def test_lzma_is_unsupported_not_misread(self):
        with self.assertRaises(mpq.Unsupported):
            mpq._decompress(b"\x12" + b"\x5d\x00\x00\x80\x00" + b"\0" * 20, 64)

    def test_no_header(self):
        with self.assertRaises(mpq.NotMPQ):
            mpq.MPQ(os.urandom(4096).replace(b"MPQ\x1a", b"xxxx"))


class ExtractMap(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_ok_writes_text_members(self):
        status, found, written = extract_text.extract_map(sample_archive(), self.tmp, "w3x")
        self.assertEqual(status, "ok")
        self.assertIn("war3map.wts", found.split(","))
        with open(os.path.join(self.tmp, "war3map.wts"), "rb") as f:
            self.assertEqual(f.read(), WTS)
        with open(os.path.join(self.tmp, "scripts", "war3map.j"), "rb") as f:
            self.assertEqual(f.read(), SCRIPT)
        self.assertEqual(written, 4)  # wts, j and the two .txt; (listfile) is not a text member
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "caf�.txt")))  # cp1252 name, readable

    def test_w3xd_without_header_is_encrypted(self):
        data = os.urandom(8192).replace(b"MPQ\x1a", b"xxxx")
        self.assertEqual(extract_text.extract_map(data, self.tmp, "w3xd"), ("encrypted", "", 0))

    def test_other_unreadable_maps_are_errors_not_crashes(self):
        self.assertEqual(extract_text.extract_map(b"\0" * 4096, self.tmp, "w3x")[0], "error")
        truncated = b"MPQ\x1a" + b"\0" * 8  # header cut short
        self.assertEqual(extract_text.extract_map(truncated, self.tmp, "w3x")[0], "error")
        self.assertEqual(os.listdir(self.tmp), [])


class Parsers(unittest.TestCase):
    def parse(self, raw):
        path = os.path.join(self.tmp, "war3map.wts")
        with open(path, "wb") as f:
            f.write(raw)
        return {sid: (c, t) for sid, c, t in mine.parse_wts(mine.read_text(path))}

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_double_encoded_bom(self):
        got = self.parse(b"\xc3\xaf\xc2\xbb\xc2\xbfSTRING 0\r\n{\r\nJugador 1\r\n}\r\n\r\nSTRING 1\r\n{\r\nB\r\n}\r\n")
        self.assertEqual({k: v[1] for k, v in got.items()}, {0: "Jugador 1", 1: "B"})

    def test_header_without_body_does_not_take_the_next_string(self):
        got = self.parse(b"STRING 681\r\n#VALUE!\r\n\r\nSTRING 682\r\n{\r\nText\r\n}\r\n")
        self.assertEqual({k: v[1] for k, v in got.items()}, {682: "Text"})

    def test_empty_body_comments_and_indented_brace(self):
        got = self.parse(b"STRING 1\n{\n}\n\nSTRING 3\n// Units: hC00 (Art Director\n), Name (Name)\n {\n"
                         b"Art Director\n\n}\nSTRING 4\n{\nline one\nline two\n}\n")
        self.assertEqual(got[1], ("", ""))
        self.assertEqual(got[3], ("Units: hC00 (Art Director", "Art Director\n"))
        self.assertEqual(got[4][1], "line one\nline two")

    def test_fdf_line_numbers_ignore_form_feeds(self):
        text = 'A_KEY "one\x0ctwo",\r\nB_KEY "three",\r\n'
        self.assertEqual(list(mine.parse_fdf(text)), [(1, "A_KEY", "one\x0ctwo"), (2, "B_KEY", "three")])


class Miner(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        strings = os.path.join(self.tmp, "base", "casc", "War3.w3mod", "_Locales", "enUS.w3mod", "Strings")
        os.makedirs(strings)
        with open(os.path.join(strings, "DialogueNightElfBase.fdf"), "w", encoding="utf-8") as f:
            f.write('NIGHTELF_UNIT_RUNNER_WHAT1 "Your pardon, Shan\'do.",\n'
                    'NIGHTELF_UNIT_RUNNER_WHAT2 "A well-known path, Shan-do.",\n')
        self.words = os.path.join(self.tmp, "words")
        with open(self.words, "w", encoding="utf-8") as f:
            f.write("\n".join(["your", "pardon", "shan", "do", "a", "well", "known", "path", "well-known",
                               "sisters", "teacher", "honored", "druid"]) + "\n")
        self.lexicon = os.path.join(self.tmp, "lexicon.json")
        with open(self.lexicon, "w", encoding="utf-8") as f:
            json.dump([{"word": "shan", "source": "darnassian", "canon_basis": "attested"},
                       {"word": "thero", "source": "darnassian", "canon_basis": "attested"}], f)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_miner(self, *extra):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            mine.main(["--base", os.path.join(self.tmp, "base"), "--lexicon", self.lexicon,
                       "--wowf", os.path.join(self.tmp, "no-wowf"), "--words", self.words] + list(extra))
        with open(os.path.join(self.tmp, "base", "analysis", "tokens.tsv"), encoding="utf-8") as f:
            rows = [l.rstrip("\n").split("\t") for l in f][1:]
        return {r[1]: r for r in rows}

    def test_apostrophe_names_of_english_parts_are_kept(self):
        tokens = self.run_miner()
        self.assertIn("shan'do", tokens)             # shan and do are both in the word list
        self.assertIn("lex", tokens["shan'do"][4])
        self.assertNotIn("well-known", tokens)       # an English compound
        self.assertNotIn("shan-do", tokens)          # hyphenated and all English: dropped as before

    def test_missing_wiki_file_is_an_error(self):
        with self.assertRaises(SystemExit):
            self.run_miner("--wiki", os.path.join(self.tmp, "Thalassian.txt"))


class Audio(unittest.TestCase):
    def test_voice_files_by_file_name(self):
        tmp = tempfile.mkdtemp()
        try:
            rows = [
                ("War3.w3mod:Sound/Dialogue/NightElfCampaign/NightElf01/N01Tyrande13.ogg", "", 200, 1),
                ("War3.w3mod:Sound/Dialogue/NightElfCampaign/NightElf01/N01Archimonde30.ogg", "", 100, 1),
                ("War3.w3mod:_Locales/enUS.w3mod:Units/NightElf/HeroWarden/HeroWardenYes3.ogg", "enUS", 300, 1),
                ("War3.w3mod:_HD.w3mod:_Locales/enUS.w3mod:Units/NightElf/HeroWarden/HeroWardenYes3.ogg", "enUS",
                 50, 1),
                ("War3.w3mod:_Locales/deDE.w3mod:Units/NightElf/HeroWarden/HeroWardenYes3.ogg", "deDE", 70, 0),
                ("War3.w3mod:Sound/Units/NightElf/NightElfDissipate1.ogg", "", 20, 1),
                ("War3.w3mod:Sound/Dialogue/HumanCampaign/Human03/H03Priest21.mp3", "", 10, 1),
            ]
            with open(os.path.join(tmp, "filelist.tsv"), "w", encoding="utf-8") as f:
                f.write("path\tckey\ttags\tlocale\tsize\tlocal\n")
                for path, loc, size, local in rows:
                    f.write("%s\t00\t\t%s\t%d\t%d\n" % (path, loc, size, local))
            totals = mine.write_audio(tmp, tmp)
            self.assertEqual(totals, {"unit": [1, 300], "dialogue": [1, 200]})
            with open(os.path.join(tmp, "audio.tsv"), encoding="utf-8") as f:
                listed = [l.split("\t")[0].rsplit("/", 1)[-1] for l in f][1:]
            self.assertEqual(sorted(listed), ["HeroWardenYes3.ogg", "HeroWardenYes3.ogg", "N01Tyrande13.ogg"])
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
