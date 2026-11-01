"""Explicit terminology and bounded grammatical rules, never general machine translation."""
from anatomy_rules import anatomy_translation
from visual_rules import COLOR_NOUNS, visual_translation
from pose_rules import pose_translation
from species_rules import species_translation
from lore_rules import translate_lore
from meta_rules import translate_meta
from apparel_rules import CLOTHING_NOUNS, apparel_translation
import csv
from pathlib import Path
with Path(__file__).with_name("glossary.tsv").open(encoding="utf-8-sig", newline="") as stream:
    glossary = dict(csv.reader(stream, delimiter="\t"))

colors = {
 'black':('чёрный','чёрная','чёрное','чёрные'), 'white':('белый','белая','белое','белые'),
 'red':('красный','красная','красное','красные'), 'blue':('синий','синяя','синее','синие'),
 'green':('зелёный','зелёная','зелёное','зелёные'), 'yellow':('жёлтый','жёлтая','жёлтое','жёлтые'),
 'pink':('розовый','розовая','розовое','розовые'), 'purple':('фиолетовый','фиолетовая','фиолетовое','фиолетовые'),
 'brown':('коричневый','коричневая','коричневое','коричневые'), 'grey':('серый','серая','серое','серые'),
 'gray':('серый','серая','серое','серые'), 'orange':('оранжевый','оранжевая','оранжевое','оранжевые'),
 'gold':('золотой','золотая','золотое','золотые'), 'silver':('серебряный','серебряная','серебряное','серебряные'),
 'light_blue':('голубой','голубая','голубое','голубые'), 'dark_blue':('тёмно-синий','тёмно-синяя','тёмно-синее','тёмно-синие'),
 'light_green':('светло-зелёный','светло-зелёная','светло-зелёное','светло-зелёные'),
 'dark_green':('тёмно-зелёный','тёмно-зелёная','тёмно-зелёное','тёмно-зелёные'),
 'dark_red':('тёмно-красный','тёмно-красная','тёмно-красное','тёмно-красные'),
 'multicolored':('разноцветный','разноцветная','разноцветное','разноцветные'),
 'two-tone':('двухцветный','двухцветная','двухцветное','двухцветные'),
 'striped':('полосатый','полосатая','полосатое','полосатые'),
 'polka_dot':('в горошек','в горошек','в горошек','в горошек'),
 'plaid':('клетчатый','клетчатая','клетчатое','клетчатые'),
}
nouns = {}
for gender, pairs in enumerate([
 'background:фон|bow:бант|ribbon:бант из ленты|necktie:галстук|scarf:шарф|sweater:свитер|vest:жилет|hood:капюшон|belt:ремень|choker:чокер|collar:воротник|hair_bow:бант в волосах|hairband:ободок|tail:хвост|beak:клюв|nose:нос|bodysuit:боди|leotard:гимнастический купальник|bikini:купальник-бикини|swimsuit:купальник|cape:плащ-накидка|suit:костюм',
 'shirt:рубашка|blouse:блузка|skirt:юбка|miniskirt:мини-юбка|jacket:куртка|t-shirt:футболка|bra:чашечка бюстгальтера|hat:шляпа|cap:кепка|beret:беретная шапка|skin:кожа|fur:шерсть|scales:чешуя|armor:броня|footwear:обувь|hair_ribbon:лента в волосах|flower:цветочная деталь|rose:роза|bag:сумка|ribbon:лента|headband:повязка на голову',
 'dress:платье|coat:пальто|underwear:нижнее бельё|body:тело|hair_ornament:украшение для волос|sky:небо',
 'hair:волосы|eyes:глаза|gloves:перчатки|socks:носки|thighhighs:чулки выше колена|pantyhose:колготки|panties:трусики|pants:брюки|shorts:шорты|shoes:туфли|boots:сапоги|sleeves:рукава|wings:крылья|ears:уши|horns:рога|claws:когти|feathers:перья|nails:ногти|lips:губы|teeth:зубы|clothes:вещи одежды|clothing:вещи одежды|kneehighs:гольфы до колена|sandals:сандалии|sneakers:кроссовки|frills:оборки|buttons:пуговицы|eyebrows:брови|eyelashes:ресницы|pupils:зрачки|irises:радужки|eyewear:очки|legwear:чулочно-носочные изделия',
]):
    for pair in pairs.split('|'):
        tag, text = pair.split(':'); nouns[tag] = (gender, text)
# Natural Russian forms for garments without forcing a false grammatical gender.
nouns.update({'bra':(0,'бюстгальтер'), 'beret':(0,'берет'), 'clothes':(1,'одежда'),
              'clothing':(1,'одежда'), 'flower':(0,'цветок')})
places = {'bed':'кровати','chair':'стуле','floor':'полу','ground':'земле','table':'столе','desk':'письменном столе',
 'couch':'диване','sofa':'диване','bench':'скамейке','grass':'траве','beach':'пляже','rooftop':'крыше',
 'stairs':'лестнице','rock':'камне','fence':'заборе'}
for place, text in places.items():
    glossary['on_'+place] = 'на '+text
    for action, verb in [('sitting','сидит'),('standing','стоит'),('lying','лежит')]:
        glossary[action+'_on_'+place] = verb+' на '+text
for count in range(1,10):
    glossary[f'{count}girl'+('s' if count>1 else '')] = f'{count} '+('девушка' if count==1 else 'девушки' if count<5 else 'девушек')
    glossary[f'{count}boy'+('s' if count>1 else '')] = f'{count} '+('юноша' if count==1 else 'юноши' if count<5 else 'юношей')

copyrights = {'original':'оригинальная работа','pokemon':'Покемон','touhou':'Touhou Project',
 'blue_archive':'Blue Archive','spy_x_family':'Spy × Family','fate_(series)':'Fate (серия)',
 'fate/grand_order':'Fate/Grand Order','kantai_collection':'Kantai Collection',
 'idolmaster':'The Idolmaster','genshin_impact':'Genshin Impact','honkai:_star_rail':'Honkai: Star Rail'}
characters = {'hatsune_miku':'Хацуне Мику','hakurei_reimu':'Хакурэй Рэйму','kirisame_marisa':'Кирисамэ Мариса',
 'oyama_mahiro':'Ояма Махиро','remilia_scarlet':'Ремилия Скарлет','flandre_scarlet':'Фландр Скарлет',
 'anya_(spy_x_family)':'Аня (Spy × Family)','yor_briar':'Йор Брайар',
 'hanako_(blue_archive)':'Ханако (Blue Archive)','hanako_(swimsuit)_(blue_archive)':'Ханако — купальник (Blue Archive)'}

def display_original(tag):
    return tag.replace('_', ' ')


# Additional common palette names; no translation of arbitrary color strings.
colors.update({
 'aqua':('бирюзовый','бирюзовая','бирюзовое','бирюзовые'),
 'cyan':('голубой','голубая','голубое','голубые'),
 'teal':('сине-зелёный','сине-зелёная','сине-зелёное','сине-зелёные'),
 'turquoise':('бирюзовый','бирюзовая','бирюзовое','бирюзовые'),
 'lavender':('светло-сиреневый','светло-сиреневая','светло-сиреневое','светло-сиреневые'),
 'beige':('бежевый','бежевая','бежевое','бежевые'),
 'tan':('светло-коричневый','светло-коричневая','светло-коричневое','светло-коричневые'),
 'cream':('кремовый','кремовая','кремовое','кремовые'),
 'maroon':('тёмно-бордовый','тёмно-бордовая','тёмно-бордовое','тёмно-бордовые'),
 'burgundy':('бордовый','бордовая','бордовое','бордовые'),
 'navy_blue':('тёмно-синий','тёмно-синяя','тёмно-синее','тёмно-синие'),
 'light_brown':('светло-коричневый','светло-коричневая','светло-коричневое','светло-коричневые'),
 'dark_brown':('тёмно-коричневый','тёмно-коричневая','тёмно-коричневое','тёмно-коричневые'),
 'light_grey':('светло-серый','светло-серая','светло-серое','светло-серые'),
 'dark_grey':('тёмно-серый','тёмно-серая','тёмно-серое','тёмно-серые'),
 'light_gray':('светло-серый','светло-серая','светло-серое','светло-серые'),
 'dark_gray':('тёмно-серый','тёмно-серая','тёмно-серое','тёмно-серые'),
 'light_pink':('светло-розовый','светло-розовая','светло-розовое','светло-розовые'),
 'dark_pink':('тёмно-розовый','тёмно-розовая','тёмно-розовое','тёмно-розовые'),
 'light_purple':('светло-фиолетовый','светло-фиолетовая','светло-фиолетовое','светло-фиолетовые'),
 'dark_purple':('тёмно-фиолетовый','тёмно-фиолетовая','тёмно-фиолетовое','тёмно-фиолетовые'),
 'light_red':('светло-красный','светло-красная','светло-красное','светло-красные'),
 'light_yellow':('светло-жёлтый','светло-жёлтая','светло-жёлтое','светло-жёлтые'),
 'dark_yellow':('тёмно-жёлтый','тёмно-жёлтая','тёмно-жёлтое','тёмно-жёлтые'),
 'light_orange':('светло-оранжевый','светло-оранжевая','светло-оранжевое','светло-оранжевые'),
 'dark_orange':('тёмно-оранжевый','тёмно-оранжевая','тёмно-оранжевое','тёмно-оранжевые'),
 'black_and_white':('чёрно-белый','чёрно-белая','чёрно-белое','чёрно-белые'),
})

nouns.update(CLOTHING_NOUNS)
nouns.update(COLOR_NOUNS)

def descriptive(tag):
    if tag in glossary: return glossary[tag], 'glossary'
    anatomy=anatomy_translation(tag)
    if anatomy is not None:return anatomy,'bounded-anatomy-rule'
    visual=visual_translation(tag)
    if visual is not None:return visual,'bounded-shape-rule'
    pose=pose_translation(tag)
    if pose is not None:return pose,'bounded-pose-rule'
    species=species_translation(tag)
    if species is not None:return species,'bounded-species-rule'
    lore=translate_lore(tag)
    if lore is not None:return lore,'contextual-lore-rule'
    apparel=apparel_translation(tag,nouns)
    if apparel is not None:return apparel,'apparel-rule'
    meta=translate_meta(tag)
    if meta is not None:return meta,'metadata-rule'
    for color in sorted(colors, key=len, reverse=True):
        if tag.startswith(color+'_') and tag[len(color)+1:] in nouns:
            noun=tag[len(color)+1:]; gender,text=nouns[noun]
            forms=colors[color]
            # Prefer usual eye and hair color terminology.
            if noun=='eyes' and color=='brown': return 'карие глаза', 'color-template'
            if noun=='hair' and color=='brown': return 'каштановые волосы', 'color-template'
            if noun=='hair' and color=='red': return 'рыжие волосы', 'color-template'
            if color=='polka_dot': return text+' в горошек', 'pattern-template'
            return forms[gender]+' '+text, 'color-template'
    return None, None

