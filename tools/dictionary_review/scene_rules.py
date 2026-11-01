"""Explicit location cases for ordinary scene and posture tags."""
LOCATIONS={
 'bed':('кровати','кровати'),'chair':('стуле',None),'floor':('полу',None),
 'ground':('земле',None),'grass':('траве','траве'),'table':('столе',None),
 'desk':('письменном столе',None),'couch':('диване',None),'sofa':('диване',None),
 'bench':('скамейке',None),'stairs':('лестнице',None),'beach':('пляже',None),
 'rooftop':('крыше',None),'roof':('крыше',None),'rock':('камне',None),
 'fence':('заборе',None),'branch':('ветке',None),'tree':('дереве',None),
 'snow':('снегу','снегу'),'sand':('песке','песке'),'water':('воде','воде'),
 'pool':(None,'бассейне'),'bathtub':(None,'ванне'),'bath':(None,'ванне'),
 'car':('автомобиле','автомобиле'),'vehicle':('транспортном средстве','транспортном средстве'),
 'bus':(None,'автобусе'),'train':(None,'поезде'),'airplane':(None,'самолёте'),
 'boat':('лодке','лодке'),'ship':('корабле','корабле'),'bicycle':('велосипеде',None),
 'motorcycle':('мотоцикле',None),'swing':('качелях',None),
 'room':(None,'комнате'),'bedroom':(None,'спальне'),'classroom':(None,'классе'),
 'school':(None,'школе'),'forest':(None,'лесу'),'cave':(None,'пещере'),
 'city':(None,'городе'),'kitchen':(None,'кухне'),'bathroom':(None,'ванной комнате'),
}
ACTIONS={'sitting':'сидит','standing':'стоит','lying':'лежит','kneeling':'стоит на коленях',
 'crouching':'сидит на корточках'}

def scene_translation(tag):
    for position,index,preposition in [('on',0,'на'),('in',1,'в')]:
        for place,forms in LOCATIONS.items():
            if forms[index] is None:continue
            phrase=preposition+' '+forms[index]
            if tag==position+'_'+place:return phrase
            for action,verb in ACTIONS.items():
                if tag==action+'_'+position+'_'+place:return verb+' '+phrase
    return None
