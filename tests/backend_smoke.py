"""Exercise the standalone routes and real tag database without starting ComfyUI."""
import asyncio
import importlib.util
import sys
import time
import types
from pathlib import Path

root = Path(__file__).parents[1]
package = types.ModuleType("yp_tagforge_test")
package.__path__ = [str(root / "py")]
sys.modules[package.__name__] = package

folder_paths = types.ModuleType("folder_paths")
folder_paths.get_filename_list = lambda _: []
folder_paths.get_folder_paths = lambda _: []
sys.modules["folder_paths"] = folder_paths
routes = {}
utils = types.ModuleType(package.__name__ + ".utils")
class Endpoint:
    @classmethod
    def get(cls, name):
        return cls.post(name)
    @classmethod
    def post(cls, name):
        def register(fn):
            routes[name] = fn
            return fn
        return register
utils.Endpoint = Endpoint
sys.modules[utils.__name__] = utils

from yp_tagforge_test import endpoints, related
from yp_tagforge_test.tagdata_manager import TagDataManager as manager

class Request:
    def __init__(self, data): self.data = data
    async def json(self): return self.data

async def main():
    import json
    start = time.monotonic()
    print("Loading main tags...", flush=True)
    await endpoints.load_main(Request({"filename": "danbooru_e621_merged.csv"}))
    print("Loading extra tags...", flush=True)
    await endpoints.load_extra(Request({"filename": "extra-quality-tags.csv"}))
    print("Loading Russian translations...", flush=True)
    await endpoints.load_translate(Request({"filename": "Ru_translated.csv"}))
    print("Checking searches...", flush=True)
    matches = manager.search("oversized", [])
    assert any(item["value"] == "oversized_clothes" and item["translate"] for item in matches)
    artists = manager.search("wlop", ["Artist"])
    assert artists and any(item["categoryName"] == "Artist" for item in artists)
    for query, expected in [("onbe", "on_bed"), ("onbed", "on_bed"), ("on bed", "on_bed"), ("blueeyes", "blue_eyes")]:
        found = manager.search(query, [])
        assert any(item["value"] == expected for item in found), (query, expected)
    assert any(item["value"] == "on_bed" for item in manager.search("onbe", ["General"]))
    manager.restrictAlias = True
    assert any(item["value"] == "blue_eyes" for item in manager.search("blueeyes", []))
    manager.restrictAlias = False
    result = await related.related(Request({"tag": "oversized_shirt"}))
    data = json.loads(result.text)
    assert data["results"][0]["value"] == "oversized_clothes"
    assert data["results"][0]["translate"].strip() == "одежда большого размера", "alias translations must not replace canonical Danbooru translations"
    assert data["translate"].strip() == "рубашка большого размера"
    assert round(data["results"][0]["similarity"] * 100, 2) == 31.81
    print("Standalone search, artists, Russian translations, related-tag route: passed", round(time.monotonic()-start, 2), "seconds")
    manager.close()

# The restricted Windows test environment cannot create asyncio's loopback
# socketpair. Drive these in-memory route coroutines directly instead.
async def inline(function, *args):
    return function(*args)
related.asyncio.to_thread = inline
coroutine = main()
try:
    coroutine.send(None)
except StopIteration:
    pass
else:
    raise AssertionError("Unexpected external await in in-memory smoke test")
