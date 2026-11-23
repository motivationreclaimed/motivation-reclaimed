import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine_sketch.sketch import *
from engine_sketch.rig import KNEEL, FLOOR_SIT, ARMS_UP, run
DUR = 9.6
import numpy as _np
CAPTION = """Nobody sees the work you do at night. Keep going anyway.

Every quiet night adds a star. One day the whole sky is lit.

#motivation #discipline #consistency #mindset #progress"""
_R=_np.random.default_rng(11); STARS=[(float(_R.uniform(60,1020)),float(_R.uniform(560,1100)),float(_R.uniform(14,26))) for _ in range(40)]
def frame(t):
    S=Sk(t)
    if t<2.4:            # WIDE night: tiny wolf walking, one star per night
        gy=1200; S.ground(gy,0,W,0.7); moon(S,W-180,640,46); n=1+int(t/0.6)
        for i in range(n): star(S,*STARS[i])
        wolf_side(S,140+120*t,gy,140,walk(t*6,22),1,"neutral"); S.text(300,["NOBODY SEES IT."],150)
        S.text(1300,[f"NIGHT {n}"],80)
    elif t<4.2:          # x4: nights fly by, the sky fills
        gy=1200; S.ground(gy,0,W,0.7); u=ease((t-2.4)/1.8); n=4+int(26*u)
        for i in range(min(40,int(4+36*u))): star(S,*STARS[i])
        wolf_side(S,W/2-80+40*math.sin(t*3),gy,140,walk(t*14,26),1,"neutral"); S.text(1300,[f"NIGHT {n}"],80); S.text(300,["X4"],90)
    elif t<6.0:          # CLOSE: he looks up at the stars, tired but steady
        wolf_front(S,W/2,2500,1900,"neutral" if t<5.2 else "hopeful",(0.2,-0.9))
        for sx,sy,r in STARS[:14]: star(S,sx,sy*0.55+40,r)
    else:                # MEDIUM: arms up under a full sky
        gy=1300; S.ground(gy)
        for sx,sy,r in STARS: star(S,sx,sy*0.95+120,r)
        k=ease((t-6.2)/0.5); wolf_side(S,W/2-60,gy,520,mix(STAND,ARMS_UP,k),1,"happy")
        S.text(260,["KEEP GOING","ANYWAY."],170)
    return S.out()
