import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine_sketch.sketch import *
from engine_sketch.rig import KNEEL, FLOOR_SIT, ARMS_UP, run
DUR = 9.6
import numpy as _np
CAPTION = """When everything hits at once, breathe first. Then begin.

In for four. Out for four. The mess is still there, but now you can see it.

Save this for the loud days.

#motivation #mentalhealth #mindset #healing #selfimprovement"""
def chaos(S,cx,cy,r,amount):
    rng=_np.random.default_rng(int(S.rng.integers(0,9999)))
    for i in range(int(18*amount)):
        a0=rng.uniform(0,2*math.pi); pts=[]
        for k in range(9):
            a=a0+k*0.7; rr=r*rng.uniform(0.9,1.5)
            pts.append((cx+math.cos(a)*rr*0.8+rng.normal(0,20),cy+math.sin(a)*rr*0.6+rng.normal(0,20)))
        S.stroke(pts,3,1.5,1,a=int(200*min(1,amount)))
def ring(S,cx,cy,r): S.stroke(S.circle_pts(cx,cy,r,r,60),6,1.4,3,closed=True)
def frame(t):
    S=Sk(t)
    if t<2.0:            # MEDIUM: scribbled chaos all around him
        gy=1300; S.ground(gy); chaos(S,W/2,880,300,1.0); bear_front(S,W/2,gy,520,"sad",(0.3,-0.4))
        S.text(300,["EVERYTHING","AT ONCE?"],160)
    elif t<4.2:          # CLOSE: eyes shut, breathe in - the ring grows
        k=ease((t-2.0)/2.0); ring(S,W/2,1000,lerp(430,560,k)); bear_front(S,W/2,2500,1900,"neutral",(0,0),blink=0.95)
        S.text(260,["BREATHE IN"],170); S.text(430,[str(1+min(3,int((t-2.0)/0.5)))],90)
    elif t<6.4:          # CLOSE: breathe out - the ring shrinks
        k=ease((t-4.2)/2.0); ring(S,W/2,1000,lerp(560,430,k)); bear_front(S,W/2,2500,1900,"neutral",(0,0),blink=0.95)
        S.text(260,["BREATHE OUT"],170); S.text(430,[str(1+min(3,int((t-4.2)/0.5)))],90)
    elif t<7.6:          # CLOSE: eyes open, calm
        bear_front(S,W/2,2500,1900,"hopeful",(0,-0.2)); S.text(300,["BETTER."],180)
    else:                # MEDIUM: calm, the chaos is gone, he walks on
        gy=1300; S.ground(gy); x=W/2-200+120*(t-7.6); bear_side(S,x,gy,500,walk((t-7.6)*6,22),1,"happy"); sun(S,W-200,780,56,1)
        S.text(250,["BREATHE FIRST.","THEN BEGIN."],160)
    return S.out()
