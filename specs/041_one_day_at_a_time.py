import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine_sketch.sketch import *
from engine_sketch.rig import KNEEL, FLOOR_SIT, ARMS_UP, run
DUR = 9.6
CAPTION = """One day at a time is still a way forward.

Thirty days looked impossible. So I stopped looking at thirty. I just did today.

Send this to someone who feels overwhelmed.

#motivation #mindset #mentalhealth #progress #youvegotthis"""
GX,GY,CELL=430,640,92
def grid(S,done=0,dim=False,only=None):
    for i in range(30):
        r,c=divmod(i,6); x=GX+c*CELL; y=GY+r*CELL
        if only is not None and i!=only: continue
        S.stroke([(x,y),(x+CELL-18,y),(x+CELL-18,y+CELL-18),(x,y+CELL-18)],3 if not dim else 2,0.8,2,closed=True,a=235 if not dim else 90)
        if i<done: S.stroke([(x+14,y+40),(x+32,y+60),(x+64,y+16)],5,0.8,2)
def frame(t):
    S=Sk(t)
    if t<2.2:            # MEDIUM: the bear looks up at a wall of 30 days
        gy=1300; S.ground(gy); grid(S); bear_front(S,250,gy,480,"neutral",(0.7,-0.6)); S.text(300,["30 DAYS?"],180)
    elif t<3.8:          # CLOSE: overwhelmed
        bear_front(S,W/2,2500,1900,"sad",(0.2,-0.5)); S.text(300,["TOO MUCH."],170)
    elif t<6.2:          # MEDIUM: only today matters - he walks to one square and ticks it
        gy=1300; S.ground(gy); u=t-3.8
        grid(S,dim=True)
        x=lerp(160,560,ease(u/1.4))
        P=walk(u*6,22) if u<1.4 else (KNEEL if u<1.9 else STAND)
        bear_side(S,x,gy,480,P,1,"neutral" if u<1.9 else "happy")
        sign(S,800,gy,"TODAY",70,260)
        if u>1.7: S.stroke([(915,gy-330),(940,gy-300),(990,gy-380)],8,1,3)
        S.text(300,["JUST TODAY."],170)
    elif t<7.4:          # CLOSE: relief
        bear_front(S,W/2,2500,1900,"happy",(0,-0.2)); S.text(300,["I CAN DO TODAY."],150)
    else:                # MEDIUM: the days fill up, one tick at a time
        gy=1300; S.ground(gy); n=1+int(29*ease((t-7.4)/1.6)); grid(S,done=n)
        k=ease((t-7.6)/0.5); bear_side(S,230,gy,480,mix(STAND,ARMS_UP,k),1,"happy")
        S.text(250,["NOT 30 DAYS.","JUST TODAY."],150)
    return S.out()
