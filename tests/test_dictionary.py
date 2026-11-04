"""Guard meaning-sensitive Russian labels and preserve canonical tag keys."""
import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]

class DictionaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "translate/Ru_translated.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.rows = list(csv.reader(stream))
        cls.labels = dict(cls.rows)

    def test_meaning_and_grammar(self):
        expected = {
            "highres": "высокое разрешение",
            "clipboard": "планшет с зажимом для бумаги",
            "doll_joints": "кукольные шарниры", "dog_tags": "армейские идентификационные жетоны",
            "mother_and_daughter": "мать и дочь", "head_wreath": "венок на голове",
            "blue_gemstone": "синий драгоценный камень", "single_sock": "один носок",
            "spaghetti_strap": "тонкая бретель", "headpat": "поглаживание по голове",
            "reaching_towards_viewer": "тянется к зрителю", "assault_rifle": "штурмовая винтовка",
            "fins": "плавники", "single_glove": "одна перчатка",
            "thighband_pantyhose": "колготки с тёмными полосами на бёдрах",
            "white_apron": "белый фартук", "staff": "посох",
            "hand_fan": "ручной веер", "hat_ribbon": "лента на головном уборе",
            "procreate_(medium)": "создано в Procreate",
            "zip_available": "доступен архив ZIP",
            "copyright_request": "запрос на опознание произведения",
            "stuffed_animal": "мягкая игрушка в виде животного", "cowboy_shot": "план до бёдер",
            "looking_at_viewer": "смотрит на зрителя", "short_hair": "короткие волосы",
            "parted_lips": "приоткрытые губы", "depth_of_field": "глубина резкости",
            "red_hakama": "красные хакама", "black_thighhighs": "чёрные чулки выше колена",
            "white_dress": "белое платье", "red_bow": "красный бант",
            "school_uniform": "школьная форма", "commission": "работа на заказ",
            "skindentation": "вдавливание тесной одежды в кожу",
        }
        for tag, label in expected.items():
            self.assertEqual(self.labels[tag], label, tag)

    def test_context_specific_meanings(self):
        expected = {
            "snowbell_(flower)": "белоцветник — Leucojum",
            "rope_train": "детская игра в паровозик с верёвкой",
            "mortar": "миномёт",
            "flowjob": "одновременная стимуляция пениса ртом и ступнями",
            "breast_bulge": "выпуклость в груди от предмета, введённого через сосок",
            "throat_transfer": "продевание предмета изо рта одного персонажа в рот другого",
        }
        for tag, label in expected.items():
            self.assertEqual(self.labels[tag], label, tag)
        self.assertIn("в хвост", self.labels["tail_penetration"])
        self.assertIn("без", self.labels["autolactation"])
        self.assertIn("пенис", self.labels["penis_face"])

    def test_names_and_keys(self):
        self.assertEqual(self.labels["blue_archive"], "Blue Archive")
        self.assertEqual(self.labels["fate/grand_order"], "Fate/Grand Order")
        self.assertNotIn("wlop", self.labels)
        self.assertEqual(len(self.labels), len(self.rows), "no duplicate dictionary keys")
        self.assertTrue(all(len(row) == 2 and row[0] and row[1] for row in self.rows))
        self.assertIn("looking_at_viewer", self.labels, "canonical keys remain unchanged")

if __name__ == "__main__":
    unittest.main()
