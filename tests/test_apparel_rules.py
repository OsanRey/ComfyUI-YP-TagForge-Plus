import importlib.util
import sys
import unittest
from pathlib import Path

TOOLS=Path(__file__).parents[1]/"tools/dictionary_review"
sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location("dictionary_review_rules",TOOLS/"rules.py")
    rules=importlib.util.module_from_spec(spec);spec.loader.exec_module(rules)
finally:
    sys.path.remove(str(TOOLS))

class ApparelRulesTests(unittest.TestCase):
    def test_gender_and_declared_compounds(self):
        for tag,expected in {
            "red_apron":"красный фартук", "blue_school_uniform":"синяя школьная форма",
            "white_maid_headdress":"белый головной убор горничной",
            "white_kimono":"белое кимоно", "black_poncho":"чёрное пончо",
            "leather_skirt":"кожаная юбка", "wet_gloves":"мокрые перчатки",
            "lace-trimmed_dress":"платье с кружевной отделкой",
            "oversized_clothes":"одежда большого размера",
            "hand_fan":"ручной веер", "skin_fang":"клык телесного цвета, нарисованный частью контура рта",
        }.items():
            self.assertEqual(rules.descriptive(tag)[0],expected,tag)

    def test_no_unbounded_word_translation(self):
        for tag in ["leather_eyes", "satin_hair", "white_unknown_garment", "silk_wlop"]:
            self.assertIsNone(rules.descriptive(tag)[0],tag)
        self.assertNotEqual(rules.descriptive("hair_bobbles")[0],rules.descriptive("hair_bun")[0])

if __name__=="__main__":unittest.main()
