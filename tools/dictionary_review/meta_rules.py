"""Bounded definitions for metadata families; unknown words remain pending."""
import re

LANGUAGES = {
 'english':'английском', 'japanese':'японском', 'chinese':'китайском', 'korean':'корейском',
 'russian':'русском', 'spanish':'испанском', 'french':'французском', 'german':'немецком',
 'portuguese':'португальском', 'italian':'итальянском', 'thai':'тайском', 'indonesian':'индонезийском',
 'vietnamese':'вьетнамском', 'latin':'латинском', 'arabic':'арабском', 'polish':'польском',
 'greek':'греческом', 'swedish':'шведском', 'ukrainian':'украинском', 'malaysian':'малайском',
 'toki_pona':'токипона',
}
REQUESTS = {
 'copyright':'произведения', 'character':'персонажа', 'source':'источника', 'clothing':'одежды',
 'gender':'пола персонажа', 'flower':'цветка', 'headwear':'головного убора', 'food':'еды',
 'weapon':'оружия', 'annotation':'содержимого изображения для аннотации', 'artist':'автора',
 'object':'предмета', 'costume':'костюма', 'vehicle':'транспортного средства', 'parody':'пародируемого произведения',
 'cosplay':'косплея', 'medium':'техники или инструмента создания', 'gesture':'жеста',
 'hairstyle':'причёски', 'bird':'птицы', 'plant':'растения', 'animal':'животного', 'meme':'мема',
 'pose':'позы', 'neckwear':'шейного аксессуара', 'reference':'использованного референса',
 'hair_ornament':'украшения для волос', 'song':'песни', 'style':'стиля', 'mecha':'меха',
 'animal_ear':'вида звериных ушей', 'magazine':'журнала', 'font':'шрифта', 'footwear':'обуви',
 'dog':'породы собаки', 'instrument':'музыкального инструмента', 'creature':'существа',
 'location':'места', 'fish':'рыбы', 'constellation':'созвездия', 'reference_work':'произведения-референса',
 'expression':'выражения лица', 'language':'языка', 'fruit':'фрукта', 'pattern':'узора',
 'aircraft':'летательного аппарата', 'background':'элементов фона', 'sound_effect':'звукового эффекта',
}
SOFTWARE = {
 'photoshop':'Photoshop','adobe_photoshop':'Adobe Photoshop','painttool_sai':'PaintTool SAI',
 'paint_tool_sai':'PaintTool SAI','clip_studio_paint':'Clip Studio Paint','procreate':'Procreate',
 'paint.net':'Paint.NET','blender':'Blender','gimp':'GIMP','live2d':'Live2D','ibispaint':'ibisPaint',
 'koikatsu':'Koikatsu','mikumikudance':'MikuMikuDance','source_filmmaker':'Source Filmmaker',
 'spine':'Spine','emofuri':'Emofuri','microsoft_paint':'Microsoft Paint','zbrush':'ZBrush',
 'stable_diffusion':'Stable Diffusion','krita':'Krita','custom_maid_3d_2':'Custom Maid 3D 2',
 'nai_diffusion':'NAI Diffusion','flipnote_studio':'Flipnote Studio','medibang_paint':'MediBang Paint',
 'autodesk_3ds_max':'Autodesk 3ds Max','easytoon':'EasyToon','kisekae':'Kisekae',
 '3d_custom_girl':'3D Custom Girl','maya':'Maya','autodesk_maya':'Autodesk Maya','picrew':'Picrew',
 'adobe_illustrator':'Adobe Illustrator','daz_studio':'DAZ Studio','midjourney':'Midjourney',
 'aseprite':'Aseprite','xnalara':'XNALara','opencanvas':'openCanvas','huashijie':'Huashijie',
 'vrchat':'VRChat','rebelle':'Rebelle','unreal_engine':'Unreal Engine',
 'flipaclip':'FlipaClip','custom_order_maid_3d_2':'Custom Order Maid 3D 2','cinema_4d':'Cinema 4D',
 'drawpile':'Drawpile','adobe_animate':'Adobe Animate','firealpaca':'FireAlpaca',
 'substance_painter':'Substance Painter','mine-imator':'Mine-imator','sketchbook':'Sketchbook',
 'piskel':'Piskel','adobe_after_effects':'Adobe After Effects','inkscape':'Inkscape',
 'flipnote_studio_3d':'Flipnote Studio 3D','art_academy':'Art Academy','colors!_3d':'Colors! 3D',
 'davinci_resolve':'DaVinci Resolve','capcut':'CapCut','live2d_cubism':'Live2D Cubism',
 'vegas_pro':'VEGAS Pro','paint_3d':'Paint 3D','sculptris':'Sculptris',
}
MATERIALS = {
 'painting':'живопись','watercolor':'акварель','photo':'фотография','photography':'фотография',
 'marker':'рисунок маркером','graphite':'графитный карандаш','colored_pencil':'цветные карандаши',
 'pen':'рисунок ручкой','millipen':'рисунок линером','acrylic_paint':'акриловые краски',
 'acrylic_painting':'акриловая живопись','nib_pen':'рисунок пером','oil_painting':'масляная живопись',
 'ballpoint_pen':'шариковая ручка','watercolor_pencil':'акварельные карандаши',
 'calligraphy_brush':'каллиграфическая кисть','pastel':'пастель','papercraft':'поделка из бумаги',
 'color_ink':'цветная тушь или чернила','lego':'конструкция LEGO','gouache':'гуашь',
 'food_art':'изображение, созданное из еды','canvas':'работа на холсте','model_kit':'сборная модель',
 'brush':'рисунок кистью','crayon':'рисунок мелками','paper_cutout':'вырезанная из бумаги композиция',
 'airbrush':'аэрография','coupy_pencil':'цветные карандаши Coupy','charcoal':'рисунок углём',
 'acrylic_gouache':'акриловая гуашь','print':'печатный оттиск','latte_art':'латте-арт',
 'masking_tape':'аппликация из декоративного скотча','clay':'работа из глины',
 'postcard':'рисунок на открытке','digital_media':'цифровое изображение','digital_drawing':'цифровой рисунок',
 'digital_painting':'цифровая живопись','traditional_media':'традиционные художественные материалы',
 '3d':'трёхмерное изображение','pixel':'пиксельная графика','collage':'коллаж',
 'sculpture':'скульптура','digital_watercolor':'цифровая акварель','papercutting':'вырезание из бумаги',
}
SERVICES={'skeb':'Skeb','pixiv':'Pixiv','vgen':'VGen','ko-fi':'Ko-fi','fantia':'Fantia',
 'patreon':'Patreon','fanbox':'FANBOX','enty':'Enty','gumroad':'Gumroad','tumblr':'Tumblr',
 'twitter':'Twitter','artstation':'ArtStation','e-hentai':'E-Hentai','deviantart':'DeviantArt',
 'yandere':'yande.re','nicoseiga':'Niconico Seiga','naver':'Naver','drawcrowd':'DrawCrowd',
 'konachan':'Konachan','gelbooru':'Gelbooru'}

def translate_meta(tag):
    if tag in SOFTWARE:return 'создано в '+SOFTWARE[tag]
    palette={'black':'чёрный','white':'белый','blue':'синий','purple':'фиолетовый','red':'красный',
        'pink':'розовый','grey':'серый','green':'зелёный','brown':'коричневый','orange':'оранжевый','yellow':'жёлтый'}
    parts=tag.split('_and_')
    if len(parts)>1 and all(part in palette for part in parts):return 'цвета: '+', '.join(palette[part] for part in parts)
    services={'ci-en':'Ci-en','bilibili':'Bilibili','misskey.io':'Misskey','youtube':'YouTube','dropbox':'Dropbox',
        'bluesky':'Bluesky','artstreet':'ART street'}
    for key,name in services.items():
        if tag=='bad_'+key+'_id':return 'неверный идентификатор источника на '+name
    match=re.fullmatch(r'(\d+):(\d+)',tag)
    if match:return 'соотношение сторон '+tag
    if re.fullmatch(r'(18|19|20)\d{2}',tag):return tag+' год'
    match=re.fullmatch(r'(\d+)th_century',tag)
    if match:return match[1]+'-й век'
    for key,language in LANGUAGES.items():
        for suffix,noun in [('commentary','комментарий автора'),('audio','аудио'),('text','текст'),('description','описание')]:
            if tag==key+'_'+suffix:return noun+' на '+language+' языке'
    if tag.endswith('_(medium)') or tag.endswith('_(artwork)'):
        stem=tag.rsplit('_(',1)[0]
        if stem in MATERIALS:return MATERIALS[stem]
        if stem in SOFTWARE:return 'создано в '+SOFTWARE[stem]
    for prefix in ['','check_']:
        for key,meaning in REQUESTS.items():
            if not prefix and tag==key+'_request':return 'запрос на опознание '+meaning
            if prefix and tag==prefix+key:return 'проверить определение '+meaning
    for key,service in SERVICES.items():
        if tag==key+'_commission':return 'работа на заказ через '+service
        if tag==key+'_reward':return 'платный материал с '+service
        if tag==key+'_sample':return 'уменьшенная предварительная версия с '+service
    for key,feature in {'bad':'ошибками','censored':'цензурой','downscaled':'уменьшенным разрешением',
        'cropped':'обрезанными краями','artifacted':'артефактами','watermarked':'водяным знаком',
        'adversarial_noise':'добавленным состязательным шумом','lossy':'сжатием с потерями'}.items():
        if tag=='has_'+key+'_revision':return 'существует версия с '+feature
    return None
