import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("translation_edit", Path(__file__).parents[1] / "py/translation_edit.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TranslationEditTests(unittest.TestCase):
    def test_update_append_and_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dictionary.csv"
            path.write_bytes("\ufeffshirt,old\r\nother,metadata,untouched\r\nshirt,duplicate\r\n".encode("utf-8"))
            module.save_translation(path, "shirt", 'рубашка, "новая"')
            module.save_translation(path, "new_tag", "новый перевод")
            with path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.reader(stream))
            self.assertEqual(rows, [["shirt", 'рубашка, "новая"'], ["other", "metadata", "untouched"],
                                    ["shirt", 'рубашка, "новая"'], ["new_tag", "новый перевод"]])
            self.assertTrue(path.read_bytes().startswith(b"\xef\xbb\xbf"))
            self.assertEqual(list(Path(directory).glob("*.tmp")), [])

    def test_failed_replace_keeps_original(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dictionary.csv"
            path.write_text("shirt,old\n", encoding="utf-8")
            with patch.object(module.os, "replace", side_effect=OSError("read only")):
                with self.assertRaises(OSError):
                    module.save_translation(path, "shirt", "new")
            self.assertEqual(path.read_text(encoding="utf-8"), "shirt,old\n")
            self.assertEqual(list(Path(directory).glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
