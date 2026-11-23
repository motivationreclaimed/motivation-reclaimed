import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine_sketch.sketch import *
from engine_sketch.rig import KNEEL, FLOOR_SIT, ARMS_UP, run
DUR = 9.6
CAPTION = """It fell. So build it again, taller this time.

Starting over isn't going back to zero. You start with everything you learned.

#motivation #nevergiveup #comeback #mindset #discipline"""
STACK=[(W/2+200,1300-45-i*92) for i in range(8)]
FALLEN=[(W/2+40,1255,0.4),(W/2+150,1255,-0.2),(W/2+270,1255,0.15),(W/2+380,1255,-0.5),(W/2+210,1170,0.9)]
def frame(t):
    S=Sk(t); gy=1300
    if t<3.0:
        S.ground(gy); fall=ease((t-1.6)/0.6)
        for i in range(5):
            sx,sy=STACK[i]; fx,fy,fa=FALLEN[i]; ff=min(1,max(0,fall*1.3-i*0.08))
            block(S,lerp(sx,fx,ff),lerp(sy,fy,ff)-math.sin(ff*math.pi)*60,140,86,fa*ff)
        wolf_front(S,W/2-220,gy,520,"happy" if t<1.6 else "sad",(0.6,-0.2) if t<1.6 else (0.6,0.6))
        if t<1.6: S.text(300,["ALMOST..."],160)
    elif t<4.6:
        wolf_front(S,W/2,2500,1900,"sad",(0.4,0.8)); S.text(300,["IT FELL."],170)
    elif t<7.4:
        S.ground(gy); u=(t-4.6)/2.8; n=int(u*7)+1
        for i in range(min(n,7)):
            q=ease((u*7-i)/0.7); sx,sy=STACK[i]; fx,fy,fa=FALLEN[i%5]
            block(S,lerp(fx,sx,q),lerp(fy,sy,q)-math.sin(q*math.pi)*90,140,86,lerp(fa,0,q))
        wolf_side(S,W/2-200,gy,520,KNEEL if int(t*3)%2 else STAND,1,"neutral"); counter(S,300,f"{min(n,7)} / 7",120)
    else:
        S.ground(gy)
        for i in range(7): sx,sy=STACK[i]; block(S,sx,sy,140,86,0)
        k=ease((t-7.4)/0.4); wolf_side(S,W/2-200,gy,520,mix(STAND,ARMS_UP,k),1,"happy")
        S.text(220,["BUILD IT","AGAIN."],170)
    return S.out()
