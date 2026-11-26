import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from engine_sketch.sketch import *
from engine_sketch.rig import ARMS_UP, FLOOR_SIT
DUR = 9.6
CAPTION = """On low days, small habits are the win.

Got up. Drank some water. Stepped outside. I used to call that nothing.

#motivation #selfimprovement #habits #mentalhealth #youvegotthis"""
def bed(S,x,gy):
    S.shape([(x,gy-60),(x+330,gy-60),(x+330,gy-120),(x,gy-120)])
    for px in (x+8,x+322): S.stroke([(px,gy),(px,gy-60)],4,1,3)
    S.stroke([(x,gy-60),(x,gy-230)],4,1,3)
    S.shape(S.circle_pts(x+70,gy-140,55,24,22))
    S.stroke([(x+140,gy-120),(x+190,gy-150),(x+250,gy-132),(x+330,gy-145),(x+330,gy-120)],3,1,2)
def glass(S,x,gy,level):
    h=250; pts=[(x-70,gy-h),(x-52,gy),(x+52,gy),(x+70,gy-h)]; S.stroke(pts,4,1,3)
    S.stroke(S.circle_pts(x,gy-h,70,14,24),3,0.8,2,closed=True)
    y=gy-h*level; S.stroke([(x-52-18*level+i*(104+36*level)/8,y+(7 if i%2 else -7)) for i in range(9)],3,0.8,2)
def flag(S,x,gy,k):
    if k<=0: return
    h=240*k; S.stroke([(x,gy),(x,gy-h)],4,0.8,3); S.shape([(x,gy-h),(x+90*k,gy-h+34*k),(x,gy-h+68*k)])
def frame(t):
    S=Sk(t)
    if t<1.8:            # MEDIUM: sitting on the floor, flat
        gy=1300; S.ground(gy); bear_side(S,W/2-80,gy,520,FLOOR_SIT,1,"sad"); S.text(250,["DID NOTHING","TODAY?"],160)
    elif t<3.5:          # MEDIUM: he got out of bed
        gy=1300; S.ground(gy); bed(S,60,gy); k=ease((t-2.0)/0.8)
        bear_side(S,720,gy,500,mix(FLOOR_SIT,STAND,k),1,"tired" if k<0.7 else "neutral"); S.text(300,["YOU GOT UP."],170)
    elif t<5.2:          # MEDIUM: water
        gy=1300; S.ground(gy); u=t-3.5; glass(S,780,gy,0.14)
        if u>0.8: S.stroke([(740,gy-390),(775,gy-350),(850,gy-460)],8,1,3)
        bear_front(S,350,gy,540,"neutral" if u<0.8 else "happy",(0.8,0.2) if u<0.8 else (0,0)); S.text(250,["YOU DRANK","SOME WATER."],160)
    elif t<6.9:          # WIDE: stepped outside
        gy=1100; S.ground(gy,0,W,0.7); u=t-5.2; sun(S,W-230,700,60,u)
        for i in range(5): flower(S,560+i*85,gy,1.0,16)
        bear_side(S,170+190*u,gy,180,walk(t*6,22),1,"happy"); S.text(300,["YOU WENT OUTSIDE."],130)
    elif t<7.8:          # CLOSE
        bear_front(S,W/2,2500,1900,"hopeful",(0,-0.3)); S.text(300,["THAT'S THREE."],160)
    else:                # MEDIUM: three little flags and a happy jump
        gy=1300; S.ground(gy); u=t-7.8
        for i,x in enumerate((110,260,830)): flag(S,x,gy,ease((u-i*0.22)/0.3))
        a=(u-0.7)/0.6; j=130*4*a*(1-a) if 0<a<1 else 0
        bear_side(S,W/2+20,gy-j,500,mix(STAND,ARMS_UP,ease((u-0.5)/0.35)),1,"happy")
        S.text(250,["SMALL WINS","ARE STILL WINS."],155)
    return S.out()
