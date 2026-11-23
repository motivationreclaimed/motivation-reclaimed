import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine_sketch.sketch import *
from engine_sketch.rig import KNEEL, FLOOR_SIT, ARMS_UP, run
DUR = 9.6
CAPTION = """Everything happens at the right time. Even when it feels slow.

I planted it and checked it every day. Nothing. Then one morning, everything.

Send this to someone who's still waiting.

#motivation #patience #mindset #growthmindset"""
def frame(t):
    S=Sk(t)
    if t<2.0:
        gy=1300; S.ground(gy); wolf_side(S,W/2-150,gy,520,KNEEL,1,"neutral")
        if t>1.0: plant(S,W/2+120,gy,0.0)
        S.text(300,["PLANT IT."],170)
    elif t<4.2:
        gy=900; S.ground(gy,0,W,0.7); u=(t-2.0)/2.2
        wolf_side(S,W/2-120,gy,150,STAND,1,"neutral"); plant(S,W/2+30,gy,0.04+0.1*u*0.3)
        day=int(1+59*ease(u)); (sun if int(t*6)%2==0 else moon)(S,W/2+180,gy-300,40,1) if int(t*6)%2==0 else moon(S,W/2+180,gy-300,40)
        counter(S,300,f"DAY {day}",130)
    elif t<5.8:
        wolf_front(S,W/2,2500,1900,"sad",(0.3,0.8)); S.text(300,["NOT YET?"],150)
    elif t<7.6:
        gy=1300; S.ground(gy); g=ease((t-5.8)/1.4)
        plant(S,W/2+180,gy,0.1+0.9*g,flowers=ease((t-6.8)/0.8)); wolf_front(S,W/2-200,gy,520,"happy",(0.7,-0.7))
    else:
        gy=1300; S.ground(gy); plant(S,W/2+180,gy,1.0,1.0); wolf_front(S,W/2-200,gy,520,"happy",(0.7,-0.7)); sun(S,W/2-300,700,50,1)
        S.text(240,["EVERYTHING HAPPENS","AT THE RIGHT TIME"],128)
    return S.out()
