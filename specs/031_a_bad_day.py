import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine_sketch.sketch import *
from engine_sketch.rig import KNEEL, FLOOR_SIT, ARMS_UP, run
DUR = 9.6
CAPTION = """A bad day is not a bad life. Remember that tonight.

Some days just rain on you. Let it. The sun still comes up tomorrow.

Save this for the hard days.

#motivation #mindset #selfimprovement #healing #dailymotivation"""
def frame(t):
    S=Sk(t)
    if t<2.2:           # WIDE: tiny wolf walking along the line, a small cloud raining on him
        gy=880; x=180+190*t
        S.ground(gy,0,W,0.7)
        wolf_side(S,x,gy,120,walk(t*7,24),1,"sad")
        cloud(S,x+10,gy-190,110,t)
        S.text(300,["A BAD DAY"],190)
    elif t<4.3:         # MEDIUM: he stops, rain on him, the words appear
        gy=1270; S.ground(gy,0,W,1.0)
        wolf_front(S,W/2,gy,560,"sad",(0,0.6))
        cloud(S,W/2,gy-700,260,t)
        S.text(300,["A BAD DAY"],190)
    elif t<6.0:         # CLOSE-UP: the sad face, slow push-in
        z=1+0.06*(t-4.3); wolf_front(S,W/2,700+1830*z,2300*z,"sad",(0.15,0.7))
        for i in range(14):
            x=60+i*72; ph=(t*1.4+i*0.29)%1.0; S.stroke([(x,ph*H),(x-8,ph*H+60)],2.0,0.4,1,a=150)
    elif t<7.4:         # CLOSE-UP: he looks up, the rain stops, a small smile
        k=min(1,(t-6.0)/0.5)
        wolf_front(S,W/2,2560,2350,"hopeful" if k>0.6 else "neutral",(0.1,-0.9*k))
        if t>6.5: sun(S,W/2+340,260,70,(t-6.5)/0.9)
    else:               # MEDIUM-WIDE: he walks on under the sun, the line lands
        gy=1300; x=W/2-260+120*(t-7.4)
        S.ground(gy,0,W,1.0)
        wolf_side(S,x,gy,520,walk((t-7.4)*7,22),1,"happy")
        sun(S,W/2+300,860,60,1)
        S.text(250,["IS NOT A","BAD LIFE"],170)
    return S.out()
