"""The Lone Wolf as a posable 2D character (side view). Poses use engine3d/toon.py's angle system:
degrees from straight down, + = forward. Draw with draw_wolf(layer, hip_xy, scale, pose, expr, facing)."""
import math, sys
from PIL import ImageDraw
import os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine3d.toon import STAND, SIT, SIT_SAD, ARMS_UP, walk, run, mix
INK=(16,14,20); GOLD=(240,186,80)
FUR=(128,130,142); FURD=(88,90,102); FURL=(216,216,224); HOOD=(48,48,58); HOODB=(36,36,44); PANTS=(30,30,38); PANTSB=(22,22,28)
SHOE=(238,236,230); SOLE=(214,160,66)
TH,SH,TO,UA,FA=118,116,150,92,86
FLOOR_SIT=dict(lean=22,thB=116,shB=-6,thF=110,shF=-12,uaB=62,faB=118,uaF=66,faF=122,head=36)
KNEEL=dict(lean=38,thB=8,shB=-82,thF=14,shF=-78,uaB=24,faB=8,uaF=34,faF=14,head=34)
def v(a,L,f): a=math.radians(a); return (math.sin(a)*L*f, math.cos(a)*L)
def add(p,q,k=1): return (p[0]+q[0]*k,p[1]+q[1]*k)
def joints(P,f):
    J={'hip':(0,0)}; ln=math.radians(P.get('lean',0))
    J['neck']=(math.sin(ln)*TO*f,-math.cos(ln)*TO); J['sh']=add((0,0),J['neck'],0.84)
    for s in 'BF':
        J['k'+s]=v(P['th'+s],TH,f); J['a'+s]=add(J['k'+s],v(P['sh'+s],SH,f))
        J['e'+s]=add(J['sh'],v(P['ua'+s],UA,f)); J['h'+s]=add(J['e'+s],v(P['fa'+s],FA,f))
    return J
def ground_offset(J):
    c=[J['aB'][1]+22,J['aF'][1]+22,J['kB'][1]+26,J['kF'][1]+26,J['hB'][1]+14,J['hF'][1]+14,26]
    return max(c)
def draw_wolf(lay,hip,s,P,expr="neutral",facing=1,rim=None):
    """hip: screen position of the hip when standing on ground y = hip[1]+ground; returns mask-able drawing on lay."""
    d=ImageDraw.Draw(lay); f=facing; J=joints(P,f); g=ground_offset(J)
    X=lambda p:(hip[0]+p[0]*s, hip[1]+(p[1]-g)*s)
    ink=3.2*s
    def limb(a,b,w1,w2,col):
        A,B=X(a),X(b); dx,dy=B[0]-A[0],B[1]-A[1]; L=math.hypot(dx,dy) or 1; nx,ny=-dy/L,dx/L
        for extra,c in ((ink,INK),(0,col)):
            r1,r2=w1*s/2+extra,w2*s/2+extra
            d.polygon([(A[0]+nx*r1,A[1]+ny*r1),(B[0]+nx*r2,B[1]+ny*r2),(B[0]-nx*r2,B[1]-ny*r2),(A[0]-nx*r1,A[1]-ny*r1)],fill=c)
            d.ellipse([A[0]-r1,A[1]-r1,A[0]+r1,A[1]+r1],fill=c); d.ellipse([B[0]-r2,B[1]-r2,B[0]+r2,B[1]+r2],fill=c)
    def poly(pts,col,o=True):
        q=[X(p) for p in pts]
        if o: d.polygon(q,fill=col,outline=INK,width=int(ink))
        else: d.polygon(q,fill=col)
    def shoe(ank,shin_ang,col,sole):
        # foot points forward, roughly flat; follows the shin a little
        a=math.radians(shin_ang*0.35)
        def R(x,y): return add(ank,(f*(x*math.cos(a)-y*math.sin(a)*1),x*math.sin(a)*f*0+y))
        pts=[R(-16,-8),R(30,-6),R(52,8),R(50,20),R(-20,20)]
        poly(pts,col); poly([R(-20,15),R(50,15),R(50,22),R(-20,22)],sole,False)
    def arm(s_):
        limb(J['sh'],J['e'+s_],44,40,HOOD if s_=='F' else HOODB); limb(J['e'+s_],J['h'+s_],40,36,HOOD if s_=='F' else HOODB)
        H=X(J['h'+s_]); r=17*s; d.ellipse([H[0]-r-ink,H[1]-r-ink,H[0]+r+ink,H[1]+r+ink],fill=INK); d.ellipse([H[0]-r,H[1]-r,H[0]+r,H[1]+r],fill=FUR if s_=='F' else FURD)
    def leg(s_):
        c=PANTS if s_=='F' else PANTSB
        limb((0,0),J['k'+s_],52,46,c); limb(J['k'+s_],J['a'+s_],46,40,c)
        shoe(J['a'+s_],P['sh'+s_],SHOE if s_=='F' else (200,198,192),SOLE)
        # gold side stripe
        A,B,C=X((0,0)),X(J['k'+s_]),X(J['a'+s_]); d.line([A,B,C],fill=GOLD if s_=='F' else (150,110,50),width=max(2,int(3*s)),joint="curve")
    # back limbs
    arm('B'); leg('B')
    # torso (hoodie)
    ln=math.radians(P.get('lean',0)); ux,uy=math.sin(ln)*f,-math.cos(ln); px,py=-uy,ux     # up and perpendicular(forward)
    def T(a,b): return (ux*a+px*b*f*f, uy*a+py*b*f*f)
    body=[T(-14,-52),T(-14,52),T(TO*0.55,60),T(TO*0.92,50),T(TO+6,24),T(TO+6,-28),T(TO*0.92,-48),T(TO*0.5,-58)]
    poly(body,HOOD)
    poly([T(-14,-52),T(-14,52),T(6,54),T(6,-54)],HOODB)                      # waistband
    poly([T(14,6),T(14,46),T(52,40),T(52,10)],HOODB)                          # pocket (front side)
    poly([T(TO-6,-46),T(TO+16,-40),T(TO+22,-8),T(TO-2,-12)],HOODB)           # hood rolled at the back of the neck
    leg('F')
    # head
    ha=math.radians(P.get('lean',0)*0.6+P.get('head',0)); N=J['neck']
    C=add(N,(math.sin(ln)*f*66,-math.cos(ln)*66))
    def Hh(x,y):  # head-local: x forward, y down
        c,s_=math.cos(ha),math.sin(ha); return add(C,((x*c-y*s_)*f,(x*s_+y*c)))
    poly([Hh(-34,-36),Hh(-20,-96),Hh(4,-46)],FURD)                           # back ear
    poly([Hh(-8,-46),Hh(8,-100),Hh(30,-46)],FURD); poly([Hh(0,-52),Hh(9,-86),Hh(22,-52)],(156,122,118),False)
    skull=[Hh(math.cos(a)*66,math.sin(a)*62) for a in [i*math.pi/14 for i in range(28)]]
    poly(skull,FUR)
    poly([Hh(-58,4),Hh(-82,18),Hh(-62,24),Hh(-76,40),Hh(-48,46),Hh(-30,40)],FUR)   # neck ruff
    poly([Hh(24,-14),Hh(90,-2),Hh(100,12),Hh(94,28),Hh(56,38),Hh(26,34)],FUR)      # snout
    poly([Hh(26,20),Hh(94,24),Hh(88,34),Hh(54,44),Hh(22,38)],FURL)                 # light jaw
    poly([Hh(-20,6),Hh(26,14),Hh(26,40),Hh(-6,46),Hh(-30,30)],FURL)                  # light cheek
    poly([Hh(-6,-56),Hh(10,-56),Hh(36,-20),Hh(20,-16)],FURD,False)                   # forehead stripe
    n=Hh(97,10); r=11*s; d.ellipse([X(n)[0]-r,X(n)[1]-r,X(n)[0]+r,X(n)[1]+r],fill=INK)
    E=Hh(34,-14); op={'sad':0.35,'tired':0.35,'determined':0.65,'happy':0.15}.get(expr,0.85)
    eye=[Hh(18,-14),Hh(34,-14-12*op),Hh(52,-16),Hh(34,-14+6*op)]
    poly(eye,GOLD if expr!='sad' else (170,130,60)); 
    pu=Hh(38,-14); r=4*s*max(op,0.4); d.ellipse([X(pu)[0]-r,X(pu)[1]-r,X(pu)[0]+r,X(pu)[1]+r],fill=INK)
    bt=-36+({'determined':8,'sad':-4}.get(expr,0)); d.line([X(Hh(16,bt+8 if expr=='sad' else bt)),X(Hh(54,bt-6 if expr!='determined' else bt+4))],fill=INK,width=int(5*s))
    d.line([X(Hh(62,30)),X(Hh(84,26))],fill=INK,width=int(3*s))
    d.line([X(Hh(-6,-52)),X(Hh(2,-30)),X(Hh(-6,-10)),X(Hh(0,14))],fill=GOLD,width=max(2,int(4*s)),joint="curve")
    arm('F')
    return J,g
