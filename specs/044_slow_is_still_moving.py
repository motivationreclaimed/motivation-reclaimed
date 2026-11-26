import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine_sketch.sketch import *
from engine_sketch.rig import ARMS_UP, FLOOR_SIT
DUR = 9.6
CAPTION = """Slow progress is still progress. Keep moving.

You don't have to be quick to get somewhere. Look behind you: every one of those steps is yours.

What are you slowly getting better at?

We animate for brands too: mr@pixevon.com

#motivation #progress #consistency #patience"""
def snail(S,x,gy,k=1.0):
    S.shape([(x-70*k,gy),(x+60*k,gy),(x+80*k,gy-46*k),(x+62*k,gy-52*k),(x+40*k,gy-20*k),(x-60*k,gy-14*k)],passes=2)
    cx,cy=x-14*k,gy-50*k; S.shape(S.circle_pts(cx,cy,44*k,42*k,26),passes=2)
    S.stroke([(cx+math.cos(a)*r*k,cy+math.sin(a)*r*k) for a,r in zip(np.linspace(0,3.6*math.pi,40),np.linspace(34,3,40))],2.0,0.5,2)
    for dx in (64,84): S.stroke([(x+70*k,gy-46*k),(x+dx*k,gy-86*k)],2.0,0.5,2); S.ell(x+dx*k,gy-90*k,6*k,6*k,WHITE,outline=False)
def prints(S,x0,x1,gy,step,r):
    x=x0; i=0
    while x<x1:
        S.ell(x,gy+r*1.9+(i%2)*r*1.3,r*1.5,r*0.75,WHITE,outline=False); x+=step; i+=1
def frame(t):
    S=Sk(t)
    if t<2.1:            # MEDIUM: plodding along beside a snail
        gy=1300; S.ground(gy); x=250+80*t; bear_side(S,x,gy,500,walk(t*3.2,17),1,"tired")
        snail(S,780+22*t,gy,1.3); S.text(300,["TOO SLOW?"],180)
    elif t<3.5:          # CLOSE: doubt
        bear_front(S,W/2,2500,1900,"sad",(-0.2,0.6)); S.text(300,["GETTING","NOWHERE?"],160)
    elif t<6.2:          # WIDE: footprints stretch out behind him, step count climbs
        gy=1050; S.ground(gy,0,W,0.7); u=t-3.5; x=560+130*u
        prints(S,70,x-60,gy,52,8); bear_side(S,x,gy,170,walk(t*4,18),1,"neutral"); snail(S,150+14*u,gy,0.5)
        S.text(300,["STEP %d"%(40+int(u/0.45))],170)
    elif t<7.3:          # CLOSE: he notices
        bear_front(S,W/2,2500,1900,"hopeful",(-0.8,0.2)); S.text(300,["LOOK BACK."],170)
    else:                # MEDIUM: walks on, happy
        gy=1300; S.ground(gy); u=t-7.3; x=470+100*u
        prints(S,50,x-130,gy,90,11); bear_side(S,x,gy,500,walk(t*4.6,20),1,"happy"); sun(S,W-190,740,56,1)
        S.text(250,["SLOW IS STILL","MOVING."],160)
    return S.out()
