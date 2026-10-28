import asyncio
import sqlite3
from aiohttp import web
from .utils import Endpoint
from .paths import root_dir
from .related_index import RelatedIndex
from .tagdata_manager import TagDataManager

index = RelatedIndex(root_dir / "data")


@Endpoint.post("related")
async def related(request):
    data = await request.json()
    tag = data.get("tag")
    if not isinstance(tag, str) or not 1 <= len(tag) <= 200:
        return web.json_response({"error": "Неверный тег"}, status=400)
    try:
        limit = max(1, min(100, int(data.get("limit", 20))))
    except (ValueError, TypeError):
        return web.json_response({"error": "Неверный лимит"}, status=400)
    try:
        results = await asyncio.to_thread(index.search, tag, limit)
    except (OSError, ValueError, sqlite3.Error) as error:
        return web.json_response({"error": f"База связанных тегов недоступна: {error}"}, status=503)
    # This connection belongs to ComfyUI's event-loop thread. Keep it here.
    translations = {}
    if TagDataManager.conn:
        values = [tag, *[item["value"] for item in results]]
        placeholders = ",".join("?" for _ in values)
        translations = dict(TagDataManager.conn.execute(
            f"SELECT value,translate FROM main_tags WHERE value IN ({placeholders}) "
            "AND term=value AND site='danbooru' AND translate<>''", values))
        for item in results:
            item["translate"] = translations.get(item["value"], "")
    return web.json_response({"tag": tag, "translate": translations.get(tag, ""), "results": results})
