from .utils import Endpoint
from .tagdata_manager import TagDataManager
from .wildcards import WildcardLoader
from . import paths

from aiohttp import web
import folder_paths


def load_data_file(filename_attr, loader, base_dir, filename):
    TagDataManager.resolve_data_path(base_dir, filename)
    setattr(TagDataManager, filename_attr, filename)
    loader()


# ===============================================
# エンドポイント
# ===============================================

# --- main タグファイルリストを取得 ---
@Endpoint.get("get_main_files")
async def get_main_files(req: web.Request):
    files = paths.tags_dir.glob("*.csv")
    filelist = [file.name for file in files if not file.stem.startswith("extra")]

    return web.json_response(filelist)

# --- extra タグファイルリストを取得 ---
@Endpoint.get("get_extra_files")
async def get_extra_files(req: web.Request):
    files = paths.tags_dir.glob("*.csv")
    filelist = [file.name for file in files if file.stem.startswith("extra")]

    return web.json_response(filelist)

# --- translate ファイルリストを取得 ---
@Endpoint.get("get_translate_files")
async def get_translate_files(req: web.Request):
    files = paths.translate_dir.glob("*.csv")
    filelist = [file.name for file in files]
    filelist = ["None"] + filelist
    
    return web.json_response(filelist)


# -----------------------------------------------
# On Change
# -----------------------------------------------

# --- Enable切り替え ---
@Endpoint.post("toggle_enable")
async def toggle_enble(req: web.Request):
    data = await req.json()
    value = data.get("value")

    TagDataManager.toggle_enable(value)

    return web.json_response({"status": "success"})


# --- Main CSV ---
@Endpoint.post("load_main")
async def load_main(req: web.Request):
    data = await req.json()
    filename = data.get("filename")

    try:
        load_data_file("main_filename", TagDataManager.load_main, paths.tags_dir, filename)
    except ValueError as error:
        return web.json_response({"error": str(error)}, status=400)

    return web.json_response({"status": "success"})


# --- Extra CSV ---
@Endpoint.post("load_extra")
async def load_extra(req: web.Request):
    data = await req.json()
    filename = data.get("filename")

    try:
        load_data_file("extra_filename", TagDataManager.load_extra, paths.tags_dir, filename)
    except ValueError as error:
        return web.json_response({"error": str(error)}, status=400)

    return web.json_response({"status": "success"})


# --- Translate ---
@Endpoint.post("load_translate")
async def load_translate(req: web.Request):
    data = await req.json()
    filename = data.get("filename")

    try:
        load_data_file("translate_filename", TagDataManager.load_translate, paths.translate_dir, filename)
    except ValueError as error:
        return web.json_response({"error": str(error)}, status=400)

    return web.json_response({"status": "success"})


# --- Embeddings ---
@Endpoint.post("load_embeddings")
async def load_embeddings(req: web.Request):
    data = await req.json()
    value = data.get("value")
    
    TagDataManager.enable_embeddings = value
    TagDataManager.load_embeddings()

    return web.json_response({"status": "success"})


# --- LoRA ---
@Endpoint.post("load_loras")
async def load_loras(req: web.Request):
    data = await req.json()
    value = data.get("value")

    TagDataManager.enable_loras = value
    TagDataManager.load_loras()

    return web.json_response({"status": "sccuess"})


# --- Wildcard ---
@Endpoint.post("load_wildcards")
async def load_wildcard(req: web.Request):
    data = await req.json()
    value = data.get("value")

    TagDataManager.enable_wildcards = value
    TagDataManager.load_wildcards()

    return web.json_response({"status": "success"})


@Endpoint.get("tagcomplete/wildcards/list")
async def wildcard_list(req: web.Request):
    return web.json_response(WildcardLoader.get_wildcards_list())


@Endpoint.get("tagcomplete/wildcards/status")
async def wildcard_status(req: web.Request):
    status = WildcardLoader.get_status()
    return web.json_response({**status, "count": status["total_available"], "ready": True})


@Endpoint.post("tagcomplete/wildcards/refresh")
async def wildcard_refresh(req: web.Request):
    WildcardLoader.refresh()
    if TagDataManager.enable and TagDataManager.enable_wildcards:
        TagDataManager.load_wildcards(refresh_loader=False)
    return web.json_response({"status": "success", **WildcardLoader.get_status()})


# --- Suggestion Count設定 --- 
@Endpoint.post("set_suggestion_count")
async def set_suggestion_count(req: web.Request):
    data = await req.json()
    value = data.get("value")
    
    TagDataManager.max_count = value
    
    return web.json_response({"status": "success"})


# --- Restict Alias設定 ---
@Endpoint.post("set_restrict_alias")
async def set_restrict_alias(req: web.Request):
    data = await req.json()
    value = data.get("value")

    TagDataManager.restrictAlias = value
    
    return web.json_response({"status": "success"})


# --- 検索実行 ---
@Endpoint.post("search")
async def search(req: web.Request):
    data = await req.json()
    term = data.get("term")
    filters = data.get("filters")

    results = TagDataManager.search(term, filters)

    return web.json_response(results)

@Endpoint.post("save_translation")
async def save_translation(req: web.Request):
    from .translation_edit import save_translation as write_csv
    from .tagdata_manager import compact_tag
    data = await req.json()
    tag, translation = data.get("tag"), data.get("translation")
    if (not isinstance(tag, str) or not 1 <= len(tag.strip()) <= 200
            or any(ord(char) < 32 for char in tag)
            or not isinstance(translation, str) or len(translation) > 2000
            or any(ord(char) < 32 for char in translation)):
        return web.json_response({"error": "Неверный тег или перевод"}, status=400)
    tag, translation = tag.strip(), translation.strip()
    filename = TagDataManager.translate_filename
    if not filename or filename == "None":
        return web.json_response({"error": "Сначала выберите словарь перевода в настройках"}, status=400)
    try:
        csv_path = TagDataManager.resolve_data_path(paths.translate_dir, filename)
        write_csv(csv_path, tag, translation)
    except (OSError, ValueError, UnicodeError) as error:
        return web.json_response({"error": f"Не удалось сохранить словарь: {error}"}, status=400)
    if TagDataManager.conn:
        for table in TagDataManager.tables:
            TagDataManager.conn.execute(
                f"UPDATE {table}_tags SET translate=?, compactTranslate=? WHERE value=? OR term=?",
                (translation, compact_tag(translation), tag, tag))
        TagDataManager.conn.commit()
    return web.json_response({"tag": tag, "translation": translation, "filename": filename})
