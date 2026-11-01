import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).parents[1]

class AuditTests(unittest.TestCase):
    def test_complete_inventory_and_honest_statuses(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run([sys.executable, str(ROOT/"tools/dictionary_review/audit.py"), "--output", directory],
                           check=True, capture_output=True)
            summary=json.loads((Path(directory)/"summary.json").read_text(encoding="utf-8"))
            with (Path(directory)/"inventory.csv").open(encoding="utf-8-sig",newline="") as stream:
                rows=list(csv.DictReader(stream))
            self.assertEqual(len(rows),summary["total"])
            self.assertEqual(sum(summary["statuses"].values()),len(rows))
            tags={row["tag"]:row for row in rows}
            self.assertEqual(tags["wlop"]["status"],"preserve_handle")
            self.assertEqual(tags[":d"]["status"],"preserve_symbol")
            self.assertEqual(tags["parent_and_child_(lore)"]["status"],"reviewed")
            self.assertEqual(tags["cowboy_shot"]["status"],"reviewed")
            self.assertEqual(tags["stuffed_animal"]["translation"],"мягкая игрушка в виде животного")
            self.assertGreater(summary["statuses"]["needs_review"],0)
            self.assertGreater(summary["statuses"]["missing_translation"],0)

if __name__=="__main__":unittest.main()
