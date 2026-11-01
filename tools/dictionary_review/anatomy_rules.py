"""Anatomical descriptions limited by attribute and body-part whitelist."""
PARTS={
 'ears':(3,'уши'),'ear':(2,'ухо'),'tail':(0,'хвост'),'tails':(3,'хвосты'),
 'wings':(3,'крылья'),'wing':(2,'крыло'),'horns':(3,'рога'),'horn':(0,'рог'),
 'hair':(3,'волосы'),'fur':(1,'шерсть'),'body':(2,'тело'),
 'arms':(3,'руки'),'legs':(3,'ноги'),'thighs':(3,'бёдра'),'hips':(3,'бёдра'),
 'hands':(3,'кисти рук'),'feet':(3,'ступни'),'fingers':(3,'пальцы рук'),'toes':(3,'пальцы ног'),
 'eyes':(3,'глаза'),'pupils':(3,'зрачки'),'eyebrows':(3,'брови'),'eyelashes':(3,'ресницы'),
 'lips':(3,'губы'),'teeth':(3,'зубы'),'fangs':(3,'клыки'),'fang':(0,'клык'),
 'nose':(0,'нос'),'mouth':(0,'рот'),'tongue':(0,'язык'),'neck':(1,'шея'),
 'waist':(1,'талия'),'shoulders':(3,'плечи'),'chest':(1,'грудь'),
 'breasts':(1,'грудь'),'butt':(3,'ягодицы'),'belly':(0,'живот'),'stomach':(0,'живот'),
 'muscles':(3,'мышцы'),'paws':(3,'лапы'),'claws':(3,'когти'),'nails':(3,'ногти'),
 'fingernails':(3,'ногти на руках'),'toenails':(3,'ногти на ногах'),
 'nipples':(3,'соски'),'areolae':(3,'ареолы'),'testicles':(3,'яички'),
 'penis':(0,'пенис'),'balls':(3,'яички'),'snout':(1,'морда'),'muzzle':(1,'морда'),
}
ATTRIBUTES={
 'long':(('длинный','длинная','длинное','длинные'), 'ears ear tail tails wings wing horns horn hair arms legs fingers toes eyelashes tongue neck claws nails fingernails toenails penis snout muzzle'),
 'short':(('короткий','короткая','короткое','короткие'), 'ears ear tail tails wings wing horns horn hair arms legs fingers toes eyelashes tongue neck claws nails fingernails toenails penis snout muzzle'),
 'large':(('большой','большая','большое','большие'), 'ears ear tail tails wings wing horns horn body hands feet eyes lips nose mouth breasts butt belly muscles paws nipples areolae testicles penis balls'),
 'big':(('большой','большая','большое','большие'), 'ears ear tail tails wings wing horns horn body hands feet eyes lips nose mouth breasts butt belly muscles paws nipples areolae testicles penis balls'),
 'small':(('маленький','маленькая','маленькое','маленькие'), 'ears ear tail tails wings wing horns horn body hands feet eyes lips nose mouth breasts butt belly muscles paws nipples areolae testicles penis balls'),
 'huge':(('огромный','огромная','огромное','огромные'), 'ears ear tail tails wings wing horns horn body hands feet eyes lips nose mouth breasts butt belly muscles paws nipples areolae testicles penis balls'),
 'thick':(('толстый','толстая','толстое','толстые'), 'tail tails thighs legs arms neck tongue eyebrows lips penis'),
 'thin':(('тонкий','тонкая','тонкое','тонкие'), 'tail tails thighs legs arms neck tongue eyebrows lips penis'),
 'wide':(('широкий','широкая','широкое','широкие'), 'hips shoulders waist nose mouth'),
 'narrow':(('узкий','узкая','узкое','узкие'), 'hips shoulders waist eyes'),
 'fluffy':(('пушистый','пушистая','пушистое','пушистые'), 'ears ear tail tails hair fur body paws'),
 'bushy':(('пушистый','пушистая','пушистое','пушистые'), 'tail tails eyebrows'),
 'pointy':(('заострённый','заострённая','заострённое','заострённые'), 'ears ear nose'),
 'sharp':(('острый','острая','острое','острые'), 'teeth fangs fang claws nails fingernails toenails'),
 'glowing':(('светящийся','светящаяся','светящееся','светящиеся'), 'eyes pupils horns horn hair body tongue claws'),
 'wet':(('мокрый','мокрая','мокрое','мокрые'), 'hair fur body ears ear tail tails'),
}

def anatomy_translation(tag):
    for prefix,(forms,allowed) in ATTRIBUTES.items():
        if tag.startswith(prefix+'_'):
            key=tag[len(prefix)+1:]
            if key in allowed.split() and key in PARTS:
                gender,text=PARTS[key];return forms[gender]+' '+text
    return None
