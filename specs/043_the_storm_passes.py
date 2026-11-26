import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine_sketch.sketch import *
from engine_sketch.rig import ARMS_UP, FLOOR_SIT
DUR = 9.6
CAPTION = """The storm passes. Your mindset just has to outlast it.

When it gets loud, I stop trying to win. I hold on and wait.

Send this to someone in the middle of it.

#motivation #mindset #mentalstrength #hope #healing"""
_R=np.random.default_rng(5)
GUSTS=[(float(_R.uniform(0,1)),float(_R.uniform(560,1270)),float(_R.uniform(140,360)),float(_R.uniform(0.7,1.4))) for _ in range(26)]
def wind(S,t,k,y0=560,y1=1270):
    """sketched gusts sweeping right to left; k = strength 0..1 (draw before the bear: always behind him)"""
    for i,(ph,y,L,v) in enumerate(GUSTS[:int(26*k)]):
        x=1300-((ph+t*v*0.9)%1.0)*1700; y=y0+(y-560)/710*(y1-y0)
        pts=[(x+L*a,y+math.sin(a*5+i)*14) for a in np.linspace(0,1,10)]
        if i%4==0: pts=[(x+34+math.cos(a)*34,y-34+math.sin(a)*34) for a in np.linspace(math.pi*1.7,math.pi*0.5,10)]+pts
        S.stroke(pts,3,1.0,2,a=190)
def lean(a): return dict(STAND,lean=a,head=a*0.4,thF=24,shF=6,thB=-22,shB=-32,uaF=30,faF=70,uaB=-20,faB=20)
def frame(t):
    S=Sk(t)
    if t<2.0:            # WIDE: tiny bear in the wind
        gy=1100; S.ground(gy,0,W,0.7); wind(S,t,1.0,620,1060); cloud(S,W/2+180-30*t,640,230,t,False)
        bear_side(S,W/2,gy,150,lean(20+4*math.sin(t*9)),1,"sad"); S.text(300,["IT'S LOUD NOW."],150)
    elif t<3.6:          # MEDIUM: leaning into it
        gy=1300; S.ground(gy); wind(S,t,1.0,640,1260)
        bear_side(S,W/2-40,gy,520,lean(24+3*math.sin(t*11)),1,"tired"); S.text(300,["HOLD ON."],180)
    elif t<5.3:          # CLOSE: eyes shut, waiting it out
        wind(S,t,0.8,620,1380); bear_front(S,W/2,2500,1900,"neutral",(0,0),blink=0.95); S.text(300,["STAY PUT."],180)
    elif t<7.3:          # MEDIUM: wind dies, cloud drifts away, sun arrives
        gy=1300; S.ground(gy); k=ease((t-5.3)/1.5); wind(S,t,0.5*(1-k),640,1260)
        cloud(S,lerp(760,1450,k),660,260,t,False)
        if k>0.35: sun(S,230,700,60,(k-0.35))
        bear_side(S,W/2-40,gy,520,mix(lean(24),STAND,k),1,"neutral" if k<0.6 else "happy"); S.text(300,["QUIETER NOW."],160)
    else:                # CLOSE: calm
        sun(S,W/2+340,500,56,(t-7.3)); bear_front(S,W/2,2680,1900,"happy",(0.3,-0.3))
        S.text(220,["IT WILL","PASS."],180)
    return S.out()
