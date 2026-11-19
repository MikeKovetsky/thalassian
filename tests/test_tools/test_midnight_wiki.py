"""research/2026-11-revival/scripts/midnight_wiki.py: wikitext parsing, which lines count as Midnight text, the cached
API client, the fetch loop and the extract step."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research", "2026-11-revival", "scripts"))
import midnight_wiki as M  # noqa: E402

ENGLISH = {"a", "an", "and", "be", "blood", "dash", "elf", "hello", "in", "is", "it", "knight", "note", "old", "prove", "she",
           "the", "to", "yourself", "do", "run", "running", "hat", "wear", "wears"}


def eras(text):
    """{cleaned line: era} for the lines of a page."""
    return {M.clean(sg["text"]): sg["era"] for sg in M.segments("Page", text)}


class TestTemplates(unittest.TestCase):
    def test_finds_nested_templates_and_skips_parameters(self):
        found = [inner for _, _, inner in M.scan_templates("a {{Outer|{{Inner|x}}|{{{1}}}}} b")]
        self.assertEqual(found, ["Inner|x", "Outer|{{Inner|x}}|{{{1}}}"])

    def test_splits_only_at_top_level_pipes(self):
        self.assertEqual(M.split_params("Text|say|[[Lor'themar Theron|Lor'themar]]|Hi {{G|x|y}}."),
                         ["Text", "say", "[[Lor'themar Theron|Lor'themar]]", "Hi {{G|x|y}}."])

    def test_clean_reads_a_text_template_and_links(self):
        self.assertEqual(M.clean("{{text|say|[[Lor'themar Theron]]|Anu belore dela'na.}}"),
                         "Lor'themar Theron says: Anu belore dela'na.")
        self.assertEqual(M.clean("[[Silvermoon City|Silvermoon]] is ''bright''."), "Silvermoon is bright.")


class TestSections(unittest.TestCase):
    TEXT = "Lead line.\n==Notes==\nA note.\n==External links==\nLinks."

    def test_a_heading_line_belongs_to_its_own_section(self):
        secs = M.sections(self.TEXT)
        self.assertEqual(M.section_at(secs, 0), "(lead)")
        self.assertEqual(M.section_at(secs, self.TEXT.index("==Notes==")), "Notes")
        self.assertEqual(M.section_at(secs, self.TEXT.index("A note.")), "Notes")
        self.assertEqual(M.section_at(secs, self.TEXT.index("Links.")), "External links")

    def test_segments_put_a_heading_in_its_section(self):
        segs = {sg["text"]: sg["section"] for sg in M.segments("Page", self.TEXT)}
        self.assertEqual(segs["==Notes=="], "Notes")


class TestEras(unittest.TestCase):
    def test_a_marker_under_a_heading_covers_its_sub_sections(self):
        e = eras("Lead text.\n==History==\n{{Legion-section}}\nLegion para.\n===Sub===\nSub para.\n"
                 "==Quotes==\n{{Mn-section}}\n;Gossip\nGossip line.\n===On-click===\nClick line.\n==Notes==\nNote.")
        self.assertEqual(e["Lead text."], "")
        self.assertEqual(e["Legion para."], "legion")
        self.assertEqual(e["Sub para."], "legion")
        self.assertEqual(e["Gossip line."], "mn")
        self.assertEqual(e["Click line."], "mn")
        self.assertEqual(e["Note."], "")

    def test_a_sub_section_marker_wins_over_its_parent(self):
        e = eras("==Biography==\n{{Wow-section}}\nOld.\n===Midnight===\n{{Mn-section}}\nNew.\n===Later===\nLater.")
        self.assertEqual((e["Old."], e["New."], e["Later."]), ("wow", "mn", "wow"))

    def test_a_marker_after_content_marks_its_own_block(self):
        e = eras('==Objective of==\n<ul class="side-by-side"><li>\n{{Legion-section}}\n*Old objective\n</li><li>\n'
                 "{{Mn-section}}\n*New objective\n</li></ul>\n==History==\nIntro.\n{{Mn-section}}\nNew para.\n===Sub===\nSub para.")
        self.assertEqual(e["Old objective"], "legion")
        self.assertEqual(e["New objective"], "mn")
        self.assertEqual((e["Intro."], e["New para."], e["Sub para."]), ("", "mn", ""))

    def test_a_lead_marker_below_the_infobox_marks_the_paragraph_after_it(self):
        e = eras("{{Npcbox\n| name = Valwyn\n| location = Tranquillien {{bc-inline}} <br> Eversong {{mn-inline}}\n}}\n"
                 "'''Valwyn''' is a quest giver.\n\n{{mn-section}}\nShe joined the cult.\n\n==Quotes==\n*Hello.")
        self.assertEqual(e["Valwyn is a quest giver."], "")
        self.assertEqual(e["She joined the cult."], "mn")
        self.assertEqual(e["Tranquillien Eversong"], "mn")
        self.assertEqual(e["Hello."], "")

    def test_an_inline_marker_marks_only_its_line(self):
        e = eras("==Locations==\n{{Npclocations|loc=Dalaran|notes={{wotlk-inline}} In Dalaran.}}\n"
                 "{{Npclocations|loc=Silvermoon|notes=In the Bazaar.}}\n==Notes==\n*In {{Tww-inline}} she wears a hat.\n*Plain note.")
        self.assertEqual(e["In Dalaran."], "wotlk")
        self.assertEqual(e["In the Bazaar."], "")
        self.assertEqual(e["she wears a hat."], "tww")
        self.assertEqual(e["Plain note."], "")

    def test_a_marker_on_a_sub_heading_line_marks_only_that_block(self):
        e = eras("==Quotes==\n;{{Mn-inline}} Midnight\n*New line.\n;Older\n*Old line.")
        self.assertEqual((e["New line."], e["Old line."]), ("mn", ""))

    def test_removed_from_beta_alpha_or_ptr_is_unreleased(self):
        e = eras("==Quotes==\n;Gossip\n{{Rfb-section}} <!-- maybe visible -->\n{{Dialogue|\nBal'a dash, malanore.\n}}\n"
                 "==Lore==\n{{Rfa-section|Midnight}}\n{{Mn-section}}\nStacked text.\n==Beta==\n*Beta line.\n==PTR version==\n*PTR line.")
        self.assertEqual(e["Bal'a dash, malanore."], "unreleased")
        self.assertEqual(e["Stacked text."], "unreleased")
        self.assertEqual(e["Beta line."], "unreleased")
        self.assertEqual(e["PTR line."], "unreleased")

    def test_other_products_are_eras_and_maintenance_markers_are_not(self):
        e = eras("==Quests==\n{{Classic only-section|tbc|patch=7.3.5}}\n*Classic quest\n==Lore==\n{{Stub-section}}\n*Stub line.\n"
                 "==Gone==\n{{Rfg-section|7.2.0}}\n*Removed line.\n==RTS==\n{{WC3-section}}\n*RTS line.\n==Card==\n{{Expac|Forever}} card.")
        self.assertEqual(e["Classic quest"], "classic only")
        self.assertEqual(e["Stub line."], "")
        self.assertEqual(e["Removed line."], "")
        self.assertEqual(e["RTS line."], "wc3")
        self.assertEqual(e["card."], "forever")

    def test_expac_midnight_marks_its_line(self):
        self.assertEqual(eras("==Notes==\n*In {{Expac|Midnight}}, she moved.\n*Earlier.")[", she moved."], "mn")


class TestPages(unittest.TestCase):
    def test_a_lead_removal_template_makes_the_page_unreleased(self):
        self.assertTrue(M.unreleased_page("{{Removedfrombeta|expac=mn}}\n'''X''' was never made available."))
        self.assertTrue(M.unreleased_page("{{rfb}}\nText.\n==Notes==\nN."))
        self.assertFalse(M.unreleased_page("Text.\n==Notes==\n{{Removedfrombeta}}"))
        self.assertFalse(M.unreleased_page("{{Removed|patch=12.0.5}}\nRemoved from the live game, so once live."))

    def test_page_status_and_older_pages(self):
        added = {"text": "==Patch changes==\n*{{Patch 12.0.1|added=}}"}
        self.assertEqual(M.page_status(added, []), ("added", "12.0.1"))
        self.assertFalse(M.older_page(added))
        older = {"text": "*{{Patch 12.0.1|note=Unique On-clicks added.}}\n*{{Patch 2.0.3|note=Added.}}"}
        self.assertEqual(M.page_status(older, []), ("changed", "12.0.1"))
        self.assertTrue(M.older_page(older))
        self.assertEqual(M.page_status({"text": "Text."}, ["cat:Harandar quests"]), ("midnight-cat", "Harandar quests"))

    def test_midnight_line(self):
        self.assertTrue(M.midnight_line("", "added", False, False))
        self.assertTrue(M.midnight_line("mn", "changed", True, False))
        self.assertFalse(M.midnight_line("", "midnight-cat", True, False))
        self.assertTrue(M.midnight_line("", "midnight-cat", False, False))
        self.assertFalse(M.midnight_line("tww", "added", False, False))
        self.assertFalse(M.midnight_line("unreleased", "added", False, False))
        self.assertFalse(M.midnight_line("mn", "added", False, True))


@contextlib.contextmanager
def fake_repo(lexicon, lang_text="'''Quel'falan danas!''' — Phrase used at the end of a compact.\n"):
    """A repo with a small lexicon and a cache folder with a Thalassian language page."""
    with tempfile.TemporaryDirectory() as tmp:
        repo, cache = os.path.join(tmp, "repo"), os.path.join(tmp, "cache")
        os.makedirs(os.path.join(repo, "src", "thalassian", "data"))
        with open(os.path.join(repo, "src", "thalassian", "data", "lexicon.json"), "w", encoding="utf-8") as fh:
            json.dump([{"word": w} for w in lexicon], fh)
        os.makedirs(os.path.join(cache, "lang"))
        with open(os.path.join(cache, "lang", "Thalassian.txt"), "w", encoding="utf-8") as fh:
            fh.write(lang_text)
        with mock.patch.object(M, "load_english", lambda: set(ENGLISH)):
            yield repo, cache


class TestClassifier(unittest.TestCase):
    def test_tokens(self):
        with fake_repo(["shorel'aran", "anu belore dela'na"]) as (repo, cache):
            clf = M.Classifier(repo, os.path.join(cache, "lang"))
        tok = clf.token
        self.assertTrue(tok("Shorel'aran")["apost"])
        self.assertTrue(tok("Shorel'aran")["lex"])
        self.assertEqual(tok("Xal'atath's")["t"], "Xal'atath")  # possessive of an apostrophe name
        self.assertTrue(tok("Xal'atath's")["apost"])
        self.assertTrue(tok("don't")["eng"])  # contraction
        self.assertFalse(tok("don't")["apost"])
        self.assertTrue(tok("runnin'")["eng"])  # dropped g
        self.assertTrue(tok("belore")["lex"])  # a part of a lexicon phrase


class TestReviewLists(unittest.TestCase):
    def test_groups_phrases_and_splits_them(self):
        def rec(phrase, mn=True, tier=1, names=False, lex=False, wiki=False):
            return {"phrase": phrase, "midnight_line": mn, "max_tier": tier, "all_names": names, "in_lexicon": lex,
                    "on_wiki_language_pages": wiki}
        recs = [rec("Shorel'aran", lex=True), rec("shorel'aran"), rec("Quel'falan danas", wiki=True), rec("Hash'ey"),
                rec("Lor'themar", names=True), rec("Bal'a dash", mn=False, lex=True), rec("Weird", tier=2)]
        r = M.review_lists(recs)
        self.assertEqual(r["phrases"], 4)
        self.assertEqual(r["names"], 1)
        self.assertEqual(r["in_lexicon"], ["shorel'aran"])
        self.assertEqual(r["on_wiki_only"], ["quel'falan danas"])
        self.assertEqual(r["in_neither"], ["hash'ey"])


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


class TestWiki(unittest.TestCase):
    def answers(self, *datas):
        it = iter(datas)
        return mock.patch.object(M.urllib.request, "urlopen", lambda req, timeout=60: FakeResponse(json.dumps(next(it)).encode()))

    def test_an_answer_is_cached_and_read_back_without_a_request(self):
        with tempfile.TemporaryDirectory() as cache, mock.patch.object(M.time, "sleep"):
            with self.answers({"query": {"pages": []}}):
                self.assertEqual(M.Wiki(cache).get(action="query", titles="A"), {"query": {"pages": []}})
            with mock.patch.object(M.urllib.request, "urlopen", side_effect=AssertionError("no request expected")):
                self.assertEqual(M.Wiki(cache).get(action="query", titles="A"), {"query": {"pages": []}})
            self.assertEqual([f for f in os.listdir(os.path.join(cache, "api-cache")) if not f.endswith(".json")], [])

    def test_an_api_error_is_raised_and_never_cached(self):
        with tempfile.TemporaryDirectory() as cache, mock.patch.object(M.time, "sleep"):
            with self.answers({"error": {"code": "badvalue", "info": "Unrecognized value"}}):
                with self.assertRaises(M.ApiError):
                    M.Wiki(cache).get(action="query", titles="A")
            self.assertEqual(os.listdir(os.path.join(cache, "api-cache")), [])

    def test_a_transient_error_is_asked_again(self):
        with tempfile.TemporaryDirectory() as cache, mock.patch.object(M.time, "sleep"), contextlib.redirect_stderr(io.StringIO()):
            with self.answers({"error": {"code": "maxlag", "info": "Waiting"}}, {"query": {"pages": [{"title": "A"}]}}):
                self.assertEqual(M.Wiki(cache).get(action="query", titles="A"), {"query": {"pages": [{"title": "A"}]}})
            self.assertEqual(len(os.listdir(os.path.join(cache, "api-cache"))), 1)


class FakeWiki:
    """Answers prop=revisions queries; the first answer leaves "Big" without its text, as the API does past its
    result-size limit."""

    def __init__(self):
        self.asked = []

    def get(self, **params):
        titles = params["titles"].split("|")
        self.asked.append(titles)
        pages = []
        for t in titles:
            if t == "Big" and len(self.asked) == 1:
                pages.append({"pageid": 2, "ns": 0, "title": t})
            elif t == "Gone":
                pages.append({"ns": 0, "title": t, "missing": True})
            else:
                pages.append({"pageid": 1, "ns": 0, "title": t, "revisions": [
                    {"revid": 10, "timestamp": "2026-11-01T00:00:00Z", "slots": {"main": {"content": "Text of " + t}}}]})
        return {"query": {"pages": pages}}


class TestFetch(unittest.TestCase):
    def test_a_page_left_out_of_a_batch_is_asked_for_again(self):
        fake = FakeWiki()
        with tempfile.TemporaryDirectory() as cache, mock.patch.object(M, "Wiki", lambda c: fake), \
                contextlib.redirect_stdout(io.StringIO()):
            M.fetch_titles(cache, ["Small", "Big", "Gone"])
            pages = M.load_pages(cache)
            self.assertEqual(fake.asked, [["Small", "Big", "Gone"], ["Big"]])
            self.assertEqual(pages["Big"]["text"], "Text of Big")
            self.assertEqual(sorted(pages), ["Big", "Small"])
            self.assertEqual(M.fetched_titles(cache), {"Small", "Big", "Gone"})

    def test_a_page_that_never_comes_back_is_reported_not_retried_forever(self):
        class Never(FakeWiki):
            def get(self, **params):
                self.asked.append(params["titles"].split("|"))
                return {"query": {"pages": [{"pageid": 2, "ns": 0, "title": t} for t in params["titles"].split("|")]}}
        fake, err = Never(), io.StringIO()
        with contextlib.redirect_stderr(err):
            qs = list(M.revisions(fake, ["Big"], tries=2, rvprop="content"))
        self.assertEqual(len(qs), 3)
        self.assertIn("no text returned for Big", err.getvalue())

    def test_a_stray_temporary_file_is_skipped(self):
        with tempfile.TemporaryDirectory() as cache:
            os.makedirs(os.path.join(cache, "pages"))
            M.write_json(os.path.join(cache, "pages", "b00000.json"), [{"title": "A", "text": "x"}])
            with open(os.path.join(cache, "pages", "b00001.json.tmp"), "w") as fh:
                fh.write("[{\"title\": ")  # an interrupted write
            self.assertEqual(sorted(M.load_pages(cache)), ["A"])


QUEST = """{{Questbox|name=Quest A}}
==Description==
Prove yourself. Shorel'aran.
==Notes==
{{text|say|Lor'themar Theron|Anu belore dela'na.}}
==Patch changes==
*{{Patch 12.0.1|added=}}
"""
NPC = """{{Npcbox|name=Guard B|race=Blood elf}}
'''Guard B''' is an elf.
==Quotes==
{{Mn-section}}
===Gossip===
{{Dialogue|title=Guard B|
Al diel shala.
}}
===Beta===
{{Dialogue|
Bal'a dash, malanore.
}}
==Patch changes==
*{{Patch 12.0.1|note=Unique on-clicks added.}}
*{{Patch 2.0.3|added=}}
"""
UNRELEASED = """{{Removedfrombeta|expac=mn}}
{{Questbox|name=Lost Quest}}
==Description==
Quel'falan danas!
==Patch changes==
*{{Patch 12.0.1|added=}}
"""


class TestExtract(unittest.TestCase):
    def test_extract(self):
        with fake_repo(["shorel'aran", "anu belore dela'na", "al diel shala", "bal'a dash, malanore"]) as (repo, cache):
            os.makedirs(os.path.join(cache, "pages"))
            M.write_json(os.path.join(cache, "titles.json"), {"Quest A": ["added:12.0.1"], "Guard B": ["cat:Eversong Woods NPCs"],
                                                              "Lost Quest": ["added:12.0.1"]})
            M.write_json(os.path.join(cache, "pages", "b00000.json"), [
                {"title": "Quest A", "text": QUEST}, {"title": "Guard B", "text": NPC}, {"title": "Lost Quest", "text": UNRELEASED}])
            out = os.path.join(cache, "hits.json")
            with contextlib.redirect_stdout(io.StringIO()):
                M.extract(cache, repo, out)
            with open(out, encoding="utf-8") as fh:
                d = json.load(fh)
        recs = {(r["page"], r["phrase"]): r for r in d["records"]}
        mn = {k for k, r in recs.items() if r["midnight_line"]}
        self.assertEqual(mn, {("Quest A", "Shorel'aran"), ("Quest A", "Anu belore dela'na"), ("Guard B", "Al diel shala")})
        self.assertEqual(recs[("Quest A", "Anu belore dela'na")]["speaker"], "Lor'themar Theron")
        self.assertEqual(recs[("Quest A", "Anu belore dela'na")]["section"], "Notes")
        self.assertEqual(recs[("Guard B", "Al diel shala")]["era_marker"], "mn")
        self.assertEqual(recs[("Guard B", "Bal'a dash, malanore")]["era_marker"], "unreleased")
        self.assertFalse(recs[("Lost Quest", "Quel'falan danas")]["midnight_line"])
        self.assertTrue(recs[("Lost Quest", "Quel'falan danas")]["on_wiki_language_pages"])
        self.assertEqual(d["summary"]["unreleased_pages"], 1)
        self.assertEqual(d["review"]["in_lexicon"], ["al diel shala", "anu belore dela'na", "shorel'aran"])
        self.assertEqual(d["summary"]["to_read_in_lexicon"], 3)


if __name__ == "__main__":
    unittest.main()
