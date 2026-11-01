"""Explicit species modifiers; unfamiliar taxa and fictional names remain untouched."""
import re
FORMS={
 'mammal':'млекопитающего','canid':'псовых','canine':'псовых','felid':'кошачьих','feline':'кошачьих',
 'cat':'кошки','dog':'собаки','wolf':'волка','fox':'лисы','rabbit':'кролика','leporid':'заячьих',
 'lagomorph':'зайцеобразных','equid':'лошадиных','equine':'лошади','bovid':'полорогих',
 'bovine':'бычьих','cattle':'крупного рогатого скота','marine':'морского существа',
 'mollusk':'моллюска','cephalopod':'головоногого моллюска','arthropod':'членистоногого',
 'avian':'птицы','bird':'птицы','fish':'рыбы','reptile':'рептилии','scalie':'чешуйчатого существа',
 'dragon':'дракона','demon':'демона','bat':'летучей мыши','rodent':'грызуна',
 'shark':'акулы','deer':'оленя','cervine':'оленя','insect':'насекомого',
 'amphibian':'земноводного','hyena':'гиены','ursine':'медведя',
 'goat':'козы','sheep':'овцы','horse':'лошади','snake':'змеи','lizard':'ящерицы',
 'raccoon':'енота','squirrel':'белки','skunk':'скунса','weasel':'ласки','ferret':'хорька',
 'otter':'выдры','leopard':'леопарда','tiger':'тигра','lion':'льва','pantherine':'пантеровых',
}

def species_translation(tag):
    match=re.fullmatch(r'generation_([1-9])_pokemon',tag)
    if match:return 'покемон '+match[1]+'-го поколения'
    if tag.endswith('_humanoid'):
        stem=tag[:-9]
        if stem in FORMS:return 'гуманоид с чертами '+FORMS[stem]
    if tag.startswith('mythological_'):
        stem=tag[len('mythological_'):]
        if stem in FORMS:return 'мифологическое существо с чертами '+FORMS[stem]
    if tag.startswith('were'):
        stem=tag[4:]
        if stem in FORMS:return 'оборотень с чертами '+FORMS[stem]
    return None
