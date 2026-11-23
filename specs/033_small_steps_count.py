import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine_sketch.sketch import *
from engine_sketch.rig import KNEEL, FLOOR_SIT, ARMS_UP, run
DUR = 9.6
CAPTION = """Small steps still count. Every single one of them.

You don't need to see the top. You just need the next step.

#discipline #consistency #motivation #progress #habits"""
def frame(t):
    S=Sk(t)
    if t<2.4:
        gy=1320; S.ground(gy,0,W,0.7); stairs(S,240,gy,14,52,52)
        sun(S,W-150,gy-14*52-90,40,1); wolf_side(S,190,gy,110,STAND,1,"neutral")
        S.text(260,["ONE STEP"],170); counter(S,500,"STEP 1",90)
    elif t<4.0:      # MEDIUM: he climbs, one step at a time, standing ON the steps
        u=t-2.4; sw,sh,n=150,95,9; x0,gy0=120,1480; S.ground(gy0,0,W,0.7); stairs(S,x0,gy0,n,sw,sh)
        pos=min(n-1,u*1.6); i=int(pos); fr=pos-i
        x=x0+sw*(i+fr)+sw*0.5; y=gy0-sh*(i+1)-sh*ease(min(1,fr*2.2))*(1 if fr>0.3 else 0)*0
        y=gy0-sh*(i+1)-(sh*ease((fr-0.55)/0.45) if fr>0.55 else 0)
        wolf_side(S,x,y,360,walk(u*6.5,26),1,"neutral"); counter(S,300,f"STEP {2+i}",120)
    elif t<5.4:
        b=0.6 if (t%1.3)<0.15 else 0.0
        wolf_front(S,W/2,2500,1900,"tired",(0,0.4),blink=b); S.text(300,["TOO SLOW?"],150)
    elif t<7.8:      # WIDE speed-up: he races up the long staircase, counter flying
        u=(t-5.4)/2.4; gy=1320; S.ground(gy,0,W,0.7); stairs(S,240,gy,14,52,52); sun(S,W-150,gy-14*52-90,40,1)
        pos=13*ease(u); i=int(pos); x=240+52*pos+26; y=gy-52*(i+1)
        wolf_side(S,x,y,110,walk(t*16,30),1,"neutral")
        counter(S,300,f"STEP {int(6+359*ease(u)**1.3)}",120); S.text(440,["X4"],70)
    else:
        gy=1320; S.ground(gy,0,W,0.7); stairs(S,240,gy,14,52,52)
        sun(S,W-150,gy-14*52-90,40,1.0); k=ease((t-7.8)/0.4)
        wolf_side(S,240+13*52+10,gy-14*52,110,mix(STAND,ARMS_UP,k),1,"happy")
        S.text(220,["SMALL STEPS","STILL COUNT"],150)
    return S.out()
