"""Test the production SQL method without importing the ComfyUI runtime."""
import ast
import sqlite3
import unittest
from pathlib import Path

source=Path(__file__).parents[1]/"py/tagdata_manager.py"
tree=ast.parse(source.read_text(encoding="utf-8"))
manager=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=="TagDataManager")
methods=[node for node in manager.body if isinstance(node,ast.FunctionDef)
         and node.name in {"sync_alias_translations", "related_alias_groups"}]
namespace={}
wrapper=ast.ClassDef(name="Harness",bases=[],keywords=[],body=methods,decorator_list=[])
exec(compile(ast.fix_missing_locations(ast.Module(body=[wrapper],type_ignores=[])),str(source),"exec"),namespace)
Harness=namespace["Harness"]

class AliasTranslationTests(unittest.TestCase):
    def setUp(self):
        Harness.tables=["main"]
        Harness.conn=sqlite3.connect(":memory:")
        Harness.conn.execute("CREATE TABLE main_tags(term,value,translate,compactTranslate,postCount,site,category)")
        Harness.conn.executemany("INSERT INTO main_tags VALUES (?,?,?,?,?,?,?)",[
            ("canonical","canonical","первое","первое","10","a","0"),
            ("canonical","canonical","второе","второе","10","b","0"),
            ("old_a","canonical","stale","stale","Alias","a","0"),
            ("canonical","canonical","self alias stale","selfaliasstale","Alias","a","0"),
            ("old_b","canonical","stale","stale","Alias","b","0"),
            ("other_category","canonical","keep","keep","Alias","a","4"),
            ("custom","canonical","custom value","customvalue",None,"a","0"),
        ])

    def tearDown(self):
        Harness.conn.close()

    def test_canonical_site_and_category(self):
        Harness.sync_alias_translations()
        labels=dict(Harness.conn.execute("SELECT term,translate FROM main_tags WHERE term<>value"))
        self.assertEqual(labels["old_a"],"первое")
        self.assertEqual(labels["old_b"],"второе")
        self.assertEqual(labels["other_category"],"keep")
        self.assertEqual(labels["custom"],"custom value")

    def test_empty_and_missing_canonical(self):
        for empty in [None,""]:
            Harness.conn.execute("UPDATE main_tags SET translate=?,compactTranslate=? WHERE term='canonical' AND site='a'",(empty,empty))
            Harness.sync_alias_translations()
            row=Harness.conn.execute("SELECT translate,compactTranslate FROM main_tags WHERE term='old_a'").fetchone()
            self.assertEqual(row,(empty,empty))

    def test_related_aliases_respect_source_sites(self):
        Harness.conn.executemany(
            "INSERT INTO main_tags(term,value,site) VALUES (?,?,?)",
            [
                ("back_hug", "hug_from_behind", "danbooru"),
                ("hugging_from_behind", "hugging_from_behind", "e621"),
                ("hug_from_behind", "hugging_from_behind", "e621"),
                ("embracing_from_behind", "hugging_from_behind", "e621"),
                ("hugging_from_behind", "custom_tag", "custom"),
            ],
        )
        self.assertEqual(Harness.related_alias_groups("back_hug"), ({"hug_from_behind"}, set(), set()))
        self.assertEqual(Harness.related_alias_groups("hugging_from_behind"), (
            set(), {"hugging_from_behind", "hug_from_behind", "embracing_from_behind"}, set(),
        ))
        self.assertEqual(Harness.related_alias_groups("embracing_from_behind"),
                         Harness.related_alias_groups("hugging_from_behind"))

    def test_related_alias_bridge_requires_agreement(self):
        Harness.conn.executemany(
            "INSERT INTO main_tags(term,value,site) VALUES (?,?,?)",
            [
                ("hearteyes", "heart_eyes", "e621"),
                ("heart_eyes", "heart_eyes", "e621"),
                ("heart_in_eyes", "heart_eyes", "e621"),
                ("heart_eyes", "heart-shaped_eyes", "danbooru"),
            ],
        )
        self.assertEqual(Harness.related_alias_groups("hearteyes")[2], {"heart-shaped_eyes"})
        Harness.conn.execute(
            "INSERT INTO main_tags(term,value,site) VALUES ('heart_in_eyes','heart','danbooru')",
        )
        self.assertEqual(Harness.related_alias_groups("hearteyes")[2], set())

if __name__=="__main__":unittest.main()
