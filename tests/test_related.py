import csv
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
        (self.root / "danbooru_tags.csv").write_text("tag,category,count,alias\nshirt,0,100,\nclothes,0,120,\nartist,1,50,\n", encoding="utf-8")
        self.edges = self.root / "danbooru_tags_cooccurrence.csv"
        self.edges.write_text("tag_a,tag_b,count\nshirt,clothes,80\nartist,shirt,20\n", encoding="utf-8")
        self.index = module.RelatedIndex(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_bidirectional_and_jaccard(self):
        results = self.index.search("shirt")
        self.assertEqual([item["value"] for item in results], ["clothes", "artist"])
        self.assertAlmostEqual(results[0]["similarity"], 80 / 140)
        self.assertEqual(results[1]["categoryName"], "Artist")
        self.assertEqual(self.index.search("artist")[0]["value"], "shirt")
        self.assertEqual(len(self.index.search("shirt", 1)), 1)
        self.assertEqual(self.index.search("missing"), [])

    def test_rebuild_when_csv_changes(self):
        self.index.search("shirt")
        self.edges.write_text("tag_a,tag_b,count\nshirt,artist,30\n", encoding="utf-8")
        self.assertEqual(self.index.search("shirt")[0]["value"], "artist")
        self.assertFalse(list(self.root.glob("*.tmp")))


if __name__ == "__main__":
    unittest.main()
