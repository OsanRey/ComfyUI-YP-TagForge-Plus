"""Shape and accessory descriptions, limited to explicitly named objects."""
COLOR_NOUNS={
 'halo':(0,'нимб'),'outline':(0,'контур'),'border':(1,'рамка'),'theme':(1,'цветовая гамма'),
 'ascot':(0,'галстук-аскот'),'handbag':(1,'сумочка'),'school_bag':(1,'школьная сумка'),
 'shoulder_bag':(1,'сумка через плечо'),'backpack':(0,'рюкзак'),'umbrella':(0,'зонт'),
 'lipstick':(1,'губная помада'),'nail_polish':(0,'лак для ногтей'),
 'hairclip':(1,'заколка для волос'),'hairpin':(1,'шпилька для волос'),
 'headphones':(3,'наушники'),'earrings':(3,'серьги'),'necklace':(2,'ожерелье'),
 'bracelet':(0,'браслет'),'tiara':(1,'тиара'),'crown':(1,'корона'),
 'collarbone':(1,'ключица'),'mask':(1,'маска'),'mouth_mask':(1,'маска на лице'),
 'sclera':(3,'белки глаз'),'pupils':(3,'зрачки'),'paws':(3,'лапы'),
 'hair_bow':(0,'бант в волосах'),'hair_tie':(1,'резинка для волос'),
 'scrunchie':(1,'объёмная резинка для волос'),'hair_scrunchie':(1,'объёмная резинка в волосах'),
 'feather':(2,'перо'),'petals':(3,'лепестки'),'scarf':(0,'шарф'),
}
SHAPES={'heart':'сердца','star':'звезды','cross':'креста','x':'буквы X','flower':'цветка',
 'butterfly':'бабочки','diamond':'ромба','crescent':'полумесяца','moon':'луны',
 'skull':'черепа','cat':'кошки','rabbit':'кролика','bat':'летучей мыши','fish':'рыбы',
 'anchor':'якоря','snowflake':'снежинки','ribbon':'ленты','triangle':'треугольника',
 'circle':'круга','square':'квадрата','hexagon':'шестиугольника'}
SHAPE_OBJECTS={'hair_ornament':'украшение для волос','earrings':'серьги','pendant':'кулон',
 'necklace':'ожерелье','pupils':'зрачки','glasses':'очки','eyewear':'очки',
 'brooch':'брошь','button':'пуговица','buttons':'пуговицы','balloon':'воздушный шар'}

def visual_translation(tag):
    for prefix,genitive in SHAPES.items():
        for separator in ['_','-shaped_']:
            if tag.startswith(prefix+separator):
                noun=tag[len(prefix+separator):]
                # An unqualified animal name can denote a motif, not the object's shape.
                if separator=='_' and noun!='hair_ornament':continue
                if noun in SHAPE_OBJECTS:return SHAPE_OBJECTS[noun]+' в форме '+genitive
    return None
