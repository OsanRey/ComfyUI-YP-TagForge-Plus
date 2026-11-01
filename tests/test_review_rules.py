import importlib.util
import sys
import unittest
from pathlib import Path

TOOLS=Path(__file__).parents[1]/"tools/dictionary_review"
sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location("extended_review_rules",TOOLS/"rules.py")
    rules=importlib.util.module_from_spec(spec);spec.loader.exec_module(rules)
finally:sys.path.remove(str(TOOLS))

class ExtendedReviewTests(unittest.TestCase):
    def test_cases_and_context(self):
        for tag,expected in {
            "hands_on_own_shoulders":"руки на своих плечах",
            "hand_on_another's_knee":"рука на колене другого персонажа",
            "holding_violin":"держит скрипку",
            "blue_one-piece_swimsuit":"синий слитный купальник",
            "butterfly-shaped_earrings":"серьги в форме бабочки",
            "white_outline":"белый контур",
            "father_(lore)":"отец (по сюжету)",
            "parent_and_child_(lore)":"родитель и его ребёнок (по сюжету)",
            "trans_woman_(lore)":"трансгендерная женщина (по сюжету)",
            "generation_4_pokemon":"покемон 4-го поколения",
            "wolf_humanoid":"гуманоид с чертами волка",
            "cover":"изображение обложки",
            "long_claws":"длинные когти", "small_paws":"маленькие лапы",
            "lavender_dress":"светло-сиреневое платье",
            "dark_brown_gloves":"тёмно-коричневые перчатки",
            "thighband_pantyhose":"колготки с тёмными полосами на бёдрах",
        }.items():self.assertEqual(rules.descriptive(tag)[0],expected,tag)

    def test_unknowns_stay_pending(self):
        for tag in ["generation_99_pokemon","unknown_taxon_humanoid","unidentified_species",
                    "holding_wlop","long_unknown_part","large_school_uniform","hand_on_own_unknown_part","herm_(lore)","irreplaceable_bvas"]:
            self.assertIsNone(rules.descriptive(tag)[0],tag)

if __name__=="__main__":unittest.main()
