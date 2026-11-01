"""Bounded pose and object rules with explicit Russian cases."""
BODY={
 'head':('голове','своей голове'), 'face':('лице','своём лице'),
 'cheek':('щеке','своей щеке'), 'chin':('подбородке','своём подбородке'),
 'neck':('шее','своей шее'), 'shoulder':('плече','своём плече'),
 'shoulders':('плечах','своих плечах'), 'arm':('руке','своей руке'),
 'arms':('руках','своих руках'), 'chest':('груди','своей груди'),
 'breast':('груди','своей груди'), 'breasts':('грудях','своих грудях'),
 'stomach':('животе','своём животе'), 'belly':('животе','своём животе'),
 'abdomen':('животе','своём животе'), 'back':('спине','своей спине'),
 'hip':('бедре','своём бедре'), 'hips':('бёдрах','своих бёдрах'),
 'thigh':('бедре','своём бедре'), 'thighs':('бёдрах','своих бёдрах'),
 'butt':('ягодицах','своих ягодицах'), 'knee':('колене','своём колене'),
 'knees':('коленях','своих коленях'), 'leg':('ноге','своей ноге'),
 'legs':('ногах','своих ногах'), 'foot':('ступне','своей ступне'),
 'feet':('ступнях','своих ступнях'), 'tail':('хвосте','своём хвосте'),
 'ear':('ухе','своём ухе'), 'ears':('ушах','своих ушах'),
}
OBJECTS={
 'book':'книгу','umbrella':'зонт','staff':'посох','wand':'волшебную палочку',
 'sword':'меч','knife':'нож','dagger':'кинжал','gun':'огнестрельное оружие',
 'rifle':'винтовку','handgun':'пистолет','shield':'щит','bow_(weapon)':'лук',
 'bag':'сумку','hat':'головной убор','flower':'цветок','flowers':'цветы',
 'bouquet':'букет','rose':'розу','leaf':'лист растения','food':'еду',
 'fruit':'фрукт','apple':'яблоко','candy':'конфету','cake':'торт',
 'cup':'чашку','mug':'кружку','teacup':'чайную чашку','bottle':'бутылку',
 'glass':'стакан или бокал','wine_glass':'бокал для вина','can':'банку',
 'plate':'тарелку','bowl':'миску','tray':'поднос','spoon':'ложку','fork':'вилку',
 'chopsticks':'палочки для еды','phone':'телефон','cellphone':'мобильный телефон',
 'smartphone':'смартфон','camera':'камеру','microphone':'микрофон','pen':'ручку',
 'pencil':'карандаш','paintbrush':'кисть для рисования','paper':'бумагу',
 'letter':'письмо','envelope':'конверт','card':'карточку','playing_card':'игральную карту',
 'fan':'веер','hand_fan':'ручной веер','towel':'полотенце','blanket':'одеяло',
 'pillow':'подушку','rope':'верёвку','chain':'цепь','leash':'поводок',
 'key':'ключ','keys':'ключи','lantern':'фонарь','candle':'свечу','lightstick':'светящуюся палочку',
 'plushie':'мягкую игрушку','stuffed_toy':'мягкую игрушку','stuffed_animal':'мягкую игрушку-зверька',
 'doll':'куклу','ball':'мяч','balloon':'воздушный шар','gift':'подарок',
 'scythe':'косу — оружие','axe':'топор','hammer':'молот','polearm':'древковое оружие',
 'trident':'трезубец','spear':'копьё','crossbow':'арбалет','weapon':'оружие',
 'guitar':'гитару','violin':'скрипку','flute':'флейту','instrument':'музыкальный инструмент',
}

def pose_translation(tag):
    for hand,label in [('hand','рука'),('hands','руки')]:
        prefix=hand+'_on_own_'
        if tag.startswith(prefix) and tag[len(prefix):] in BODY:
            return label+' на '+BODY[tag[len(prefix):]][1]
        prefix=hand+"_on_another's_"
        if tag.startswith(prefix) and tag[len(prefix):] in BODY:
            return label+' на '+BODY[tag[len(prefix):]][0]+' другого персонажа'
    if tag.endswith('_focus'):
        key=tag[:-6]
        if key in BODY:return 'акцент на '+BODY[key][0]
    for prefix,label in [('holding_','держит '),('carrying_','несёт ')]:
        if tag.startswith(prefix):
            key=tag[len(prefix):]
            if key in OBJECTS:return label+OBJECTS[key]
    return None
