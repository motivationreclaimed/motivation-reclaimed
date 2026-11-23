import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine_sketch.sketch import *
from engine_sketch.rig import KNEEL, FLOOR_SIT, ARMS_UP, run
DUR = 9.6
CAPTION = """Stop looking at how far you have to go. Look how far you've come.

Day one feels like a lifetime ago. That's not nothing. That's everything.

Save this for the days it feels slow.

#motivation #progress #selfimprovement #mindset #consistency"""
def frame(t):
    S=Sk(t)
    if t<2.2:            # MEDIUM: tired, still walking
        gy=1300; S.ground(gy); wolf_side(S,240+100*t,gy,520,walk(t*5,18),1,"tired"); S.text(300,["STILL SO FAR..."],150)
    elif t<3.8:          # CLOSE
        wolf_front(S,W/2,2500,1900,"sad",(0.5,0.4)); S.text(300,["SO FAR TO GO?"],150)
    elif t<5.4:          # MEDIUM: he turns around and looks back
        gy=1300; S.ground(gy); k=ease((t-3.9)/0.4)
        wolf_side(S,W/2+80,gy,520,STAND,-1 if k>0.5 else 1,"neutral")
        for i in range(6): flower(S,80+i*60,gy,1.0,20)
    elif t<7.4:          # WIDE: the whole way back to DAY 1
        gy=1000; S.ground(gy,0,W,0.7); sign(S,110,gy,"DAY 1",44,120)
        for i in range(18): flower(S,190+i*42,gy,1.0,12)
        wolf_side(S,W-110,gy,130,STAND,-1,"happy")
        S.text(300,["DAY 1 TO TODAY"],120)
    else:                # CLOSE: he smiles
        wolf_front(S,W/2,2680,1900,"happy",(-0.4,-0.2))
        S.text(220,["LOOK HOW FAR","YOU'VE COME."],150)
    return S.out()
