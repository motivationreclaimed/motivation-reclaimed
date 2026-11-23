import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine_sketch.sketch import *
from engine_sketch.rig import KNEEL, FLOOR_SIT, ARMS_UP, run
DUR = 9.6
CAPTION = """Fall. Get up. Try again. That's the whole lesson.

First try, I hit the wall. Second try, I hit it again. Third try, I was over it.

Comment 'again' if you're on your second try.

#motivation #nevergiveup #mindset #mentalstrength #comeback"""
def attempt(S,t0,t,jump_h,ok):
    """run at the wall from the left; jump; bounce back unless ok"""
    gy=1300; S.ground(gy); wall(S,640,gy,110,260); u=t-t0
    if u<0.9:   x=120+420*u/0.9; y=0; P=run(u*11); e="neutral"
    elif u<1.4:
        k=(u-0.9)/0.5; y=-jump_h*4*k*(1-k)
        if ok: x=lerp(540,860,k); P=mix(run(10),ARMS_UP,0.3)
        else: x=lerp(540,550,min(1,k*2))-70*max(0,k-0.5); P=run(10)
        e="neutral"
    else:
        k=ease((u-1.4)/0.35)
        if ok: x=860; y=0; P=mix(STAND,ARMS_UP,k); e="happy"
        else: x=515; y=0; P=mix(run(10),KNEEL,k); e="sad"
    wolf_side(S,x,gy+y,480,P,1,e)
def frame(t):
    S=Sk(t)
    if t<1.9:   attempt(S,0.0,t,140,False); S.text(300,["TRY 1"],120)
    elif t<3.2: wolf_front(S,W/2,2500,1900,"sad",(0,0.7)); S.text(300,["FAILED."],170)
    elif t<5.1: attempt(S,3.2,t,220,False); S.text(300,["TRY 2"],120)
    elif t<6.2: wolf_front(S,W/2,2500,1900,"neutral" if t<5.7 else "hopeful",(0.3,-0.2)); S.text(300,["ONE MORE."],170)
    else:
        attempt(S,6.2,t,420,True)
        if t<8.0: S.text(300,["TRY 3"],120)
        else: S.text(240,["FALL. GET UP.","TRY AGAIN."],160)
    return S.out()
