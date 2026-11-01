"""Kinship and identity labels explicitly marked as contextual, not visual anatomy."""
KINSHIP={
 'sibling':'брат или сестра','parent':'родитель','brother':'брат','sister':'сестра',
 'mother':'мать','son':'сын','father':'отец','daughter':'дочь','child':'ребёнок родителя',
 'brothers':'братья','sisters':'сёстры','twins':'близнецы','triplets':'тройняшки',
 'cousins':'двоюродные братья или сёстры','adopted':'усыновлённый или удочерённый персонаж',
 'uncle':'дядя','nephew':'племянник','niece':'племянница','aunt':'тётя',
 'grandparent':'дедушка или бабушка','grandchild':'внук или внучка',
 'grandmother':'бабушка','grandfather':'дедушка','grandson':'внук','granddaughter':'внучка',
 'adopted_son':'приёмный сын','adopted_daughter':'приёмная дочь',
 'adoptive_father':'приёмный отец','adoptive_mother':'приёмная мать',
 'adoptive_sibling':'приёмный брат или сестра','adoptive_brother':'приёмный брат',
 'adoptive_sister':'приёмная сестра','adoptive_brothers':'приёмные братья','adoptive_sisters':'приёмные сёстры',
 'stepsibling':'сводный брат или сестра','stepbrother':'сводный брат','stepsister':'сводная сестра',
 'stepbrothers':'сводные братья','stepparent':'отчим или мачеха','stepchild':'пасынок или падчерица',
 'stepfather':'отчим','stepmother':'мачеха','stepson':'пасынок','stepdaughter':'падчерица',
 'ancestor':'предок','descendant':'потомок',
}
IDENTITY={'trans':'трансгендерный персонаж','trans_woman':'трансгендерная женщина',
 'trans_man':'трансгендерный мужчина','nonbinary':'небинарный персонаж',
 'male':'персонаж мужского пола','female':'персонаж женского пола',
 'adult':'совершеннолетний персонаж','young':'юный персонаж','intersex':'интерсекс-персонаж'}

def translate_lore(tag):
    if not tag.endswith('_(lore)'):return None
    key=tag[:-7]
    if key in KINSHIP:return KINSHIP[key]+' (по сюжету)'
    if key in IDENTITY:return IDENTITY[key]+' (по сюжету)'
    if key=='incest':return 'инцест (по сюжету)'
    pairs={'parent_and_child':'родитель и его ребёнок',
        'mother_and_child':'мать и её ребёнок','father_and_child':'отец и его ребёнок',
        'grandparent_and_grandchild':'бабушка/дедушка и внук/внучка',
        'grandmother_and_grandchild':'бабушка и внук/внучка',
        'grandfather_and_grandchild':'дедушка и внук/внучка',
        'stepparent_and_stepchild':'отчим/мачеха и пасынок/падчерица',
        'stepfather_and_stepchild':'отчим и пасынок/падчерица',
        'stepmother_and_stepchild':'мачеха и пасынок/падчерица'}
    if key in pairs:return pairs[key]+' (по сюжету)'
    parts=key.split('_and_')
    if len(parts)==2 and all(part in KINSHIP for part in parts):
        return ' и '.join(KINSHIP[part] for part in parts)+' (по сюжету)'
    return None
