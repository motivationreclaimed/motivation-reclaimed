import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine_sketch.sketch import *
from engine_sketch.rig import KNEEL, FLOOR_SIT, ARMS_UP, run
DUR = 9.6
CAPTION = """On a heavy day, find one good thing. Then another.

The sun came out for a minute. A flower by the road. That counts.

What's one good thing from your day? Comment it.

#motivation #mindset #healing #dailymotivation #selfimprovement"""
def frame(t):
    S=Sk(t)
    if t<2.0:
        wolf_front(S,W/2,2500,1900,"tired",(0,0.5)); S.text(300,["LONG DAY?"],170)
    elif t<4.8:          # MEDIUM: good things appear one by one, his face lifts with each
        gy=1300; S.ground(gy); n=1+int((t-2.0)/0.85)
        e=["sad","neutral","hopeful","happy"][min(3,n-1)]
        wolf_front(S,W/2-120,gy,520,e,(0.6,-0.3))
        if n>=1: sun(S,W/2+260,820,55,min(1,(t-2.0)*2))
        if n>=2: flower(S,W/2+200,gy,ease((t-2.85)/0.5),34)
        if n>=3: star(S,W/2+330,1040,40)
        S.text(300,["FIND ONE","GOOD THING"],150); S.text_at(W/2+280,1180,str(min(3,n)),90)
    elif t<6.4:
        k=ease((t-4.8)/0.6); wolf_front(S,W/2,2500,1900,"happy",(0.1,-0.3))
        for i,(sx,sy) in enumerate(((180,700),(900,640),(860,980),(200,1050))):
            if k>i*0.2: star(S,sx,sy,24+6*math.sin(t*6+i))
    else:
        gy=1240; S.ground(gy); x=200+170*(t-6.4)
        for i in range(10): flower(S,560+i*52,gy,1.0,20)
        sun(S,W-170,760,55,1); wolf_side(S,x,gy,480,walk((t-6.4)*6,22),1,"happy")
        S.text(240,["THEN FIND","ANOTHER."],170)
    return S.out()
