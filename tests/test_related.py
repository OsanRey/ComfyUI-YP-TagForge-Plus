import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("related_index", Path(__file__).parents[1] / "py/related_index.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RelatedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.tags = self.root / "danbooru_tags.csv"
        self.tags.write_text(
            "tag,category,count,alias\n"
            "shirt,0,100,\nclothes,0,120,\nartist,1,50,\n"
            "common,0,800,\nincidental,0,800,\ncollar,0,200,\ncorpus_marker,0,1400,\n",
            encoding="utf-8",
        )
        self.edges = self.root / "danbooru_tags_cooccurrence.csv"
        self.edges.write_text(
            "tag_a,tag_b,count\nshirt,clothes,80\nartist,shirt,20\n"
            "shirt,common,60\nshirt,incidental,56\ncollar,shirt,18\n",
            encoding="utf-8",
        )
        self.index = module.RelatedIndex(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_bidirectional_and_jaccard(self):
        results = self.index.search("shirt")
        self.assertEqual([item["value"] for item in results], ["clothes", "collar", "common"])
        self.assertAlmostEqual(results[0]["similarity"], 80 / 140)
        self.assertGreater(results[2]["similarity"], results[1]["similarity"])
        self.assertEqual(self.index.search("clothes")[0]["value"], "shirt")
        self.assertEqual(self.index.search("common")[0]["value"], "shirt")
        self.assertEqual(self.index.search("incidental"), [])
        self.assertEqual(self.index.search("shirt", 100), results)
        self.assertEqual(self.index.search("artist")[0]["value"], "shirt")
        self.assertEqual(len(self.index.search("shirt", 1)), 1)
        self.assertEqual(self.index.search("missing"), [])

    def test_rebuild_when_csv_changes(self):
        self.index.search("shirt")
        self.edges.write_text(
            "tag_a,tag_b,count\ncorpus_marker,common,100\nshirt,common,50\n",
            encoding="utf-8",
        )
        # The anchored union is now 2100, so 50 exceeds its expected count.
        self.assertEqual(self.index.search("shirt")[0]["value"], "common")
        self.assertFalse(list(self.root.glob("*.tmp")))

    def test_append_up_to_five_characters_to_general_results(self):
        with self.tags.open("a", encoding="utf-8") as tags:
            for number in range(1, 7):
                tags.write(f"character_{number},4,100,\n")
            tags.write("weak_character,4,100,\nseries,3,100,\n")
        with self.edges.open("a", encoding="utf-8") as edges:
            edges.write("shirt,series,100\nshirt,weak_character,1\ncollar,character_1,80\n")
        self.assertEqual(
            [item["value"] for item in self.index.search("collar")],
            ["shirt", "character_1"],
        )
        with self.edges.open("a", encoding="utf-8") as edges:
            for number in range(1, 7):
                edges.write(f"character_{number},shirt,{90 + number}\n")
        results = self.index.search("shirt", 2)
        self.assertEqual([item["value"] for item in results], [
            "clothes", "collar", "character_6", "character_5", "character_4", "character_3", "character_2",
        ])
        self.assertTrue(all(item["categoryName"] == "Character" for item in results[2:]))

    def test_resolve_aliases_and_preserve_exact_tags(self):
        direct = self.index.search("shirt")
        self.assertEqual(self.index.search_with_sources("shirt", alias_groups=({"clothes"},)), (["shirt"], direct))
        self.assertEqual(self.index.search_with_sources(
            "shirt_alias", alias_groups=({"shirt"}, {"clothes"}),
        ), (["shirt"], direct))
        self.assertEqual(self.index.search_with_sources(
            "shirt_variant", alias_groups=(set(), {"shirt", "not_indexed"}),
        ), (["shirt"], direct))

    def test_combine_matches_without_duplicate_rows_or_source_tags(self):
        with self.edges.open("a", encoding="utf-8") as edges:
            edges.write("clothes,collar,70\nclothes,common,75\n")
        names, results = self.index.search_with_sources(
            "ambiguous", 2, alias_groups=({"shirt", "clothes"}, {"corpus_marker"}),
        )
        self.assertEqual(names, ["clothes", "shirt"])
        self.assertEqual([item["value"] for item in results], ["collar", "common"])
        self.assertEqual(results[0]["sourceTag"], "clothes")
        self.assertAlmostEqual(results[0]["similarity"], 70 / 250)


if __name__ == "__main__":
    unittest.main()
