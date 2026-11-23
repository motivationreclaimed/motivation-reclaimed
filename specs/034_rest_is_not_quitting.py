import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine_sketch.sketch import *
from engine_sketch.rig import KNEEL, FLOOR_SIT, ARMS_UP, run
DUR = 9.6
CAPTION = """Rest is not quitting. Read that again.

Tired isn't the same as finished. Sleep, then go again tomorrow.

Save this for when you need permission to rest. 🌙

#motivation #mentalstrength #selfimprovement #healing"""
def frame(t):
    S=Sk(t)
    if t<2.2:
        gy=900; S.ground(gy,0,W,0.7); x=120+260*t; wolf_side(S,x,gy,140,run(t*10.5),1,"neutral"); moon(S,W-220,gy-420+40*t,46); S.text(300,["RUNNING ON EMPTY?"],140)
    elif t<3.6:
        gy=1300; S.ground(gy); k=ease((t-2.4)/0.8); P=mix(walk(t*5,20),FLOOR_SIT,k)
        wolf_side(S,W/2-60,gy,520,P,1,"tired"); moon(S,W-200,520,60); S.text(240,["TIRED?"],170)
    elif t<5.6:
        b=min(0.5,(t-3.6)/1.6*0.5); wolf_front(S,W/2,2500,1900,"tired",(0,0.5),blink=b); moon(S,W/2+340,260,60)
        S.text(300,["REST."],170)
    elif t<7.6:
        k=ease((t-5.6)/0.6); wolf_front(S,W/2,2500,1900,"hopeful" if k>0.5 else "tired",(0.2,-0.7*k))
        sun(S,W/2+340,300-60*k,64,(t-5.6))
    else:
        gy=1300; S.ground(gy); x=W/2-280+130*(t-7.6); wolf_side(S,x,gy,520,walk((t-7.6)*7,24),1,"happy"); sun(S,W-200,760,56,1)
        S.text(230,["REST IS NOT","QUITTING"],160)
    return S.out()
