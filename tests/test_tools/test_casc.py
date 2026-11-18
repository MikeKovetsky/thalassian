"""tools/wowf/casc.py: known-answer vectors and the BLTE and extraction edge cases."""
import os
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools", "wowf"))
import casc  # noqa: E402

KEY_NAME = "0123456789ABCDEF"
KEY = bytes(range(16))


def blte_single(chunk):
    return b"BLTE" + struct.pack(">I", 0) + chunk


def blte_multi(chunks_and_sizes):
    count = len(chunks_and_sizes)
    table = b"".join(struct.pack(">II", len(c), size) + bytes(16) for c, size in chunks_and_sizes)
    header = b"BLTE" + struct.pack(">I", 12 + 24 * count) + b"\x0f" + count.to_bytes(3, "big") + table
    return header + b"".join(c for c, _ in chunks_and_sizes)


def encrypted_chunk(plain_chunk, index=0, key=KEY, key_name=KEY_NAME):
    iv = bytearray(b"\x11\x22\x33\x44")
    stored_iv = bytes(iv)
    for i in range(4):
        iv[i] ^= (index >> (i * 8)) & 0xFF
    payload = casc.salsa20_xor(key, bytes(iv) + bytes(4), plain_chunk)
    name = bytes.fromhex(key_name)[::-1]
    return b"E" + bytes([len(name)]) + name + bytes([4]) + stored_iv + b"S" + payload


class FakeCasc(object):
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def read_ckey(self, ckey):
        self.calls += 1
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class TestPrimitives(unittest.TestCase):
    def test_salsa20_estream_set1_vector0(self):
        # 128-bit key 80 00..00, nonce 0: first 64 keystream bytes (eSTREAM); matches PyCryptodome.
        out = casc.salsa20_xor(bytes.fromhex("80" + "00" * 15), bytes(8), bytes(64))
        self.assertEqual(out.hex().upper(),
                         "4DFA5E481DA23EA09A31022050859936DA52FCEE218005164F267CB65F5CFD7F"
                         "2B4F97E0FF16924A52DF269515110A07F9E460BC65EF95DA58F740B7D1DBB0AA")

    def test_jenkins_lookup3_vectors(self):
        # Bob Jenkins' lookup3.c driver5 values for hashlittle2 (pc, pb) -> (c, b).
        self.assertEqual(casc.hashlittle2(b"", 0, 0), (0xDEADBEEF, 0xDEADBEEF))
        self.assertEqual(casc.hashlittle2(b"", 0, 0xDEADBEEF), (0xBD5B7DDE, 0xDEADBEEF))
        text = b"Four score and seven years ago"
        self.assertEqual(casc.hashlittle2(text, 0, 0), (0x17770551, 0xCE7226E6))
        self.assertEqual(casc.hashlittle2(text, 1, 0), (0xCD628161, 0x6CBEA4B3))


class TestBLTE(unittest.TestCase):
    def test_plain_and_zlib_chunks(self):
        self.assertEqual(casc.blte_decode(blte_single(b"Nhello")), b"hello")
        data = blte_multi([(b"N" + b"ab", 2), (b"Z" + zlib.compress(b"cdef"), 4)])
        self.assertEqual(casc.blte_decode(data), b"abcdef")

    def test_encrypted_chunk_with_known_key(self):
        data = blte_multi([(b"Nab", 2), (encrypted_chunk(b"Nsecret", index=1), 6)])
        self.assertEqual(casc.blte_decode(data, {KEY_NAME: KEY}), b"absecret")

    def test_unknown_key_zero_fills_a_sized_chunk(self):
        missing = set()
        data = blte_multi([(b"Nab", 2), (encrypted_chunk(b"Nsecret", index=1), 6)])
        self.assertEqual(casc.blte_decode(data, {}, missing), b"ab" + bytes(6))
        self.assertEqual(missing, {KEY_NAME})

    def test_unknown_key_in_a_single_chunk_raises(self):
        missing = set()
        with self.assertRaises(casc.MissingKey):
            casc.blte_decode(blte_single(encrypted_chunk(b"Nsecret")), {}, missing)
        self.assertEqual(missing, {KEY_NAME})


class TestExtractFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = os.path.join(self.tmp.name, "out")

    def tearDown(self):
        self.tmp.cleanup()

    def test_writes_under_the_output_folder(self):
        self.assertIsNone(casc.extract_file(FakeCasc(b"WDC5"), b"ck", self.out, "dbfilesclient/map.db2"))
        with open(os.path.join(self.out, "dbfilesclient", "map.db2"), "rb") as f:
            self.assertEqual(f.read(), b"WDC5")

    def test_given_bytes_skip_the_local_read(self):
        fake = FakeCasc(b"local")
        self.assertIsNone(casc.extract_file(fake, b"ck", self.out, "a\\b.ogg", data=b"cdn"))
        self.assertEqual(fake.calls, 0)
        with open(os.path.join(self.out, "a", "b.ogg"), "rb") as f:
            self.assertEqual(f.read(), b"cdn")

    def test_encrypted_file_is_reported_not_raised(self):
        why = casc.extract_file(FakeCasc(casc.MissingKey(KEY_NAME)), b"ck", self.out, "dbfilesclient/x.db2")
        self.assertIn(KEY_NAME, why)
        self.assertFalse(os.path.exists(os.path.join(self.out, "dbfilesclient", "x.db2")))

    def test_missing_file_is_reported(self):
        self.assertEqual(casc.extract_file(FakeCasc(None), b"ck", self.out, "x.db2"), "not on disk")
        self.assertEqual(casc.extract_file(FakeCasc(b"x"), None, self.out, "x.db2"), "not on disk")

    def test_paths_that_leave_the_output_folder_are_refused(self):
        for rel in ("../escape.db2", "dbfilesclient/../../escape.db2", "/tmp/escape.db2", "..\\escape.db2"):
            self.assertIsNotNone(casc.extract_file(FakeCasc(b"x"), b"ck", self.out, rel), rel)
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "escape.db2")))


if __name__ == "__main__":
    unittest.main()
