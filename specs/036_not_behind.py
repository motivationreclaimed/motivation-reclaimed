import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine_sketch.sketch import *
from engine_sketch.rig import KNEEL, FLOOR_SIT, ARMS_UP, run
DUR = 9.6
CAPTION = """You're not behind. You're on your own path, at your own pace.

There's no clock on becoming who you're meant to be.

Send this to someone who feels late.

#motivation #mindset #selfimprovement #patience #personalgrowth"""
def frame(t):
    S=Sk(t)
    if t<2.2:            # WIDE: signposts of "deadlines", tiny wolf walking slowly
        gy=900; S.ground(gy,0,W,0.7)
        for x,txt in ((300,"AGE 25"),(620,"AGE 30"),(940,"AGE 35")): sign(S,x,gy,txt,40,120)
        wolf_side(S,90+60*t,gy,120,walk(t*5,20),1,"sad"); S.text(300,["TOO LATE?"],170)
    elif t<4.0:          # CLOSE: worry
        wolf_front(S,W/2,2500,1900,"sad",(-0.6,0.3)); S.text(300,["AM I BEHIND?"],150)
    elif t<6.0:          # MEDIUM: he walks on, flowers grow wherever he has stepped
        gy=1300; S.ground(gy); x=200+150*(t-4.0)
        for i in range(8):
            fx=140+i*48
            if fx<x-40: flower(S,fx,gy,ease((x-40-fx)/90),24)
        sign(S,880,gy,"YOUR PACE",50,180); wolf_side(S,x,gy,520,walk((t-4)*6,22),1,"neutral")
    elif t<7.6:          # CLOSE: he smiles
        k=ease((t-6.0)/0.5); wolf_front(S,W/2,2500,1900,"happy" if k>0.5 else "neutral",(0.2,-0.4*k))
    else:                # WIDE: a long trail of flowers behind him
        gy=1100; S.ground(gy,0,W,0.8)
        for i in range(16): flower(S,40+i*42,gy,1.0,16)
        wolf_side(S,760+60*(t-7.6),gy,240,walk((t-7.6)*5,20),1,"happy")
        S.text(260,["YOU'RE NOT BEHIND.","YOU'RE ON YOUR WAY."],120)
    return S.out()
