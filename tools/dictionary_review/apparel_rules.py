"""Agreement rules limited to explicitly identified garments and accessories."""
CLOTHING_NOUNS = {}
for gender, pairs in enumerate([
 'apron:фартук|maid_apron:фартук горничной|waist_apron:поясной фартук|bowtie:галстук-бабочка|sailor_collar:матросский воротник|neckerchief:шейный платок|turtleneck:высокий облегающий воротник|suit:костюм|business_suit:деловой костюм|blazer:блейзер|cardigan:кардиган|sweater_vest:вязаный жилет|crop_top:укороченный топ|tank_top:топ без рукавов|tube_top:топ без бретелей|halter_top:топ с завязкой на шее|kimono:наряд кимоно|haori:жакет хаори|jumpsuit:комбинезон|poncho:плащ-пончо',
 'dress_shirt:классическая рубашка|school_uniform:школьная форма|military_uniform:военная форма|baseball_cap:бейсболка|hoodie:толстовка с капюшоном|headband:повязка на голову|veil:вуаль|maid_headdress:головной убор горничной|camisole:майка на тонких бретелях|robe:мантия|loincloth:набедренная повязка|negligee:ночная сорочка|leather_jacket:кожаная куртка|pleated_skirt:плиссированная юбка|suspender_skirt:юбка на подтяжках|hair_ribbon:лента в волосах',
 'sundress:летнее платье|sweater_dress:платье-свитер|china_dress:платье ципао|ribbon-trimmed_dress:платье с отделкой лентой|underwear:нижнее бельё',
 'hakama:хакама|bloomers:блумеры|bikini_bottom:плавки бикини|swim_trunks:плавки-шорты|board_shorts:пляжные шорты|legwear:чулочно-носочные изделия|fishnets:вещи в сетку|stockings:чулки|thigh_highs:чулки выше колена|over-kneehighs:чулки выше колена|ankle_socks:короткие носки|fingerless_gloves:перчатки без пальцев|elbow_gloves:перчатки до локтя|gauntlets:латные перчатки|sneakers:кроссовки|sandals:сандалии|high_heels:туфли на высоком каблуке|mary_janes:туфли с ремешком на подъёме|loafers:лоферы',
]):
    for pair in pairs.split('|'):
        key,text=pair.split(':');CLOTHING_NOUNS[key]=(gender,text)
# A single garment may already include an adjective: both words must agree.
CLOTHING_NOUNS['hoodie']=(1,'толстовка с капюшоном')
CLOTHING_NOUNS['maid_headdress']=(0,'головной убор горничной')
CLOTHING_NOUNS['leather_jacket']=(1,'куртка из кожи')
CLOTHING_NOUNS['school_uniform']=(1,'школьная форма')
CLOTHING_NOUNS.update({'kimono':(2,'кимоно'),'haori':(2,'хаори'),'poncho':(2,'пончо'),'fishnets':(1,'сетчатая одежда'),'one-piece_swimsuit':(0,'слитный купальник'),'competition_swimsuit':(0,'спортивный купальник для соревнований'),'serafuku':(1,'школьная форма с матросским воротником')})

GARMENTS = set(CLOTHING_NOUNS) | set('shirt blouse skirt miniskirt jacket t-shirt bra hat cap beret armor footwear ribbon headband dress coat underwear gloves socks thighhighs pantyhose panties pants shorts shoes boots sleeves clothes clothing kneehighs sandals sneakers legwear bow necktie scarf sweater vest hood belt choker collar leotard bikini swimsuit cape suit hair_bow hair_ribbon'.split())
ADJECTIVES = {
 'leather':('кожаный','кожаная','кожаное','кожаные'),
 'silk':('шёлковый','шёлковая','шёлковое','шёлковые'),
 'silken':('шёлковый','шёлковая','шёлковое','шёлковые'),
 'satin':('атласный','атласная','атласное','атласные'),
 'lace':('кружевной','кружевная','кружевное','кружевные'),
 'latex':('латексный','латексная','латексное','латексные'),
 'denim':('джинсовый','джинсовая','джинсовое','джинсовые'),
 'transparent':('прозрачный','прозрачная','прозрачное','прозрачные'),
 'see-through':('просвечивающий','просвечивающая','просвечивающее','просвечивающие'),
 'wet':('мокрый','мокрая','мокрое','мокрые'),
 'torn':('порванный','порванная','порванное','порванные'),
 'tight':('облегающий','облегающая','облегающее','облегающие'),
 'loose':('свободный','свободная','свободное','свободные'),
 'baggy':('мешковатый','мешковатая','мешковатое','мешковатые'),
}
SUFFIXES={'oversized':'большого размера','frilled':'с оборками','lace-trimmed':'с кружевной отделкой',
 'ribbon-trimmed':'с отделкой лентой','fur-trimmed':'с меховой отделкой',
 'floral_print':'с цветочным узором','animal_print':'с узором под шкуру животного'}

def apparel_translation(tag,nouns):
    if tag in CLOTHING_NOUNS:return CLOTHING_NOUNS[tag][1]
    for prefix in ADJECTIVES.keys() | SUFFIXES.keys():
        if tag.startswith(prefix+'_'):
            key=tag[len(prefix)+1:]
            if key in GARMENTS and key in nouns:
                gender,text=nouns[key]
                if prefix in SUFFIXES:return text+' '+SUFFIXES[prefix]
                return ADJECTIVES[prefix][gender]+' '+text
    return None
