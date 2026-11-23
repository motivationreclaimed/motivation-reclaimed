"""SKETCH style (owner-approved 23 Nov 2026): pure black, scratchy hand-drawn white lines with 10 fps line boil,
the Lone Wolf (front view for close-ups, rigged side view for walking/running/kneeling/sitting/arms up),
Amatic SC Bold caps, watermark added automatically by Sk.out()."""
import math, sys, numpy as np, subprocess
from PIL import Image, ImageDraw, ImageFont
import os
from .rig import joints, ground_offset, STAND, walk, mix, run, KNEEL, FLOOR_SIT, ARMS_UP
W,H=1080,1920; SS=2; FPS=30
FONT=os.path.join(os.path.dirname(__file__),"..","assets","fonts","AmaticSC-Bold.ttf")
WHITE=(244,244,240); BLACK=(0,0,0)
class Sk:
    def __init__(s,t):
        s.im=Image.new("RGB",(W*SS,H*SS),BLACK); s.d=ImageDraw.Draw(s.im,"RGBA"); s.rng=np.random.default_rng(int(t*10)+17)  # 10 fps line boil
        s.lw=2.6; s.lj=1.6
    def P(s,p): return (p[0]*SS,p[1]*SS)
    def stroke(s,pts,w=None,j=None,passes=3,closed=False,a=235):
        w=w or s.lw; j=j or s.lj; pts=list(pts)+([pts[0]] if closed else [])
        for _ in range(passes):
            off=s.rng.normal(0,j,(len(pts),2)); sh=s.rng.normal(0,j*0.6,2)
            q=[s.P((x+ox+sh[0],y+oy+sh[1])) for (x,y),(ox,oy) in zip(pts,off)]
            s.d.line(q,fill=WHITE+(a,),width=max(1,int(w*SS*s.rng.uniform(0.7,1.1))),joint="curve")
    def fill(s,pts,col=BLACK): s.d.polygon([s.P(p) for p in pts],fill=col)
    def circle_pts(s,cx,cy,rx,ry,n=40,a0=0,a1=2*math.pi): return [(cx+math.cos(a)*rx,cy+math.sin(a)*ry) for a in np.linspace(a0,a1,n)]
    def shape(s,pts,w=None,j=None,passes=3): s.fill(pts); s.stroke(pts,w,j,passes,closed=True)
    def ell(s,cx,cy,rx,ry,col,outline=True,w=2.4):
        s.d.ellipse([s.P((cx-rx,cy-ry)),s.P((cx+rx,cy+ry))],fill=col)
        if outline: s.stroke(s.circle_pts(cx,cy,rx,ry,30),w,0.8,2,closed=True)
    def fur(s,cx,cy,r,n=60,a0=math.pi*0.95,a1=math.pi*2.05,ln=0.35,w=None):
        w=w or s.lw*0.7
        for _ in range(n):
            a=s.rng.uniform(a0,a1); L=r*s.rng.uniform(0.08,ln); r0=r*s.rng.uniform(0.86,1.02)
            p0=(cx+math.cos(a)*r0,cy+math.sin(a)*r0); bend=s.rng.normal(0,0.25)
            p1=(cx+math.cos(a+bend*0.2)*(r0+L),cy+math.sin(a+bend*0.2)*(r0+L))
            s.d.line([s.P(p0),s.P(p1)],fill=WHITE+(int(s.rng.uniform(150,240)),),width=max(1,int(w*SS)))
    def ground(s,y,x0=0,x1=W,thick=1.0):
        for _ in range(int(40*thick)):
            a=s.rng.uniform(x0,x1-60); L=s.rng.uniform(80,400); yy=y+s.rng.normal(0,2.2*thick)
            s.d.line([s.P((a,yy)),s.P((min(x1,a+L),yy+s.rng.normal(0,1)))],fill=WHITE+(int(s.rng.uniform(90,220)),),width=max(1,int(s.rng.uniform(1,2.6)*SS*thick)))
        s.stroke([(x0,y),(x1,y)],2.4*thick,0.8,2)
    def text(s,y,lines,size,col=WHITE,gap=0.92):
        f=ImageFont.truetype(FONT,int(size*SS))
        for i,t in enumerate(lines):
            w=f.getlength(t); s.d.text(((W*SS-w)/2,(y+i*size*gap)*SS),t,font=f,fill=col)
    def text_at(s,x,y,t,size,col=WHITE):
        f=ImageFont.truetype(FONT,int(size*SS)); w=f.getlength(t); s.d.text((x*SS-w/2,y*SS),t,font=f,fill=col)
    def watermark(s):
        f=ImageFont.truetype(FONT,int(58*SS)); t="MOTIVATION RECLAIMED"; sp=10*SS
        w=sum(f.getlength(ch) for ch in t)+sp*(len(t)-1); x=(W*SS-w)/2
        for ch in t: s.d.text((x,1415*SS),ch,font=f,fill=(236,232,222,215),stroke_width=4*SS,stroke_fill=(0,0,0)); x+=f.getlength(ch)+sp
    def out(s): s.watermark(); return s.im.resize((W,H),Image.LANCZOS)

# ---------- the wolf, FRONT view (close-ups) ----------
def wolf_front(S,cx,gy,h,expr="neutral",look=(0,0),blink=0.0):
    """h = total height in px (feet to ear tips)."""
    u=h/100.0; S.lw=min(9,max(2.4,u*0.42)); S.lj=min(4,max(1.0,u*0.16))
    hipy=gy-u*34; shy=gy-u*64; hr=u*17; hcy=shy-u*15
    # legs
    for sx in (-1,1):
        x=cx+sx*u*5.2; S.shape([(x-u*3.2,hipy),(x+u*3.2,hipy),(x+u*3.0,gy),(x-u*3.0,gy)])
    # arms
    for sx in (-1,1):
        x=cx+sx*u*11.2; S.shape([(x-u*2.6,shy+u*2),(x+u*2.6,shy+u*2),(x+u*2.4,hipy+u*9),(x-u*2.2,hipy+u*9)])
    # torso
    S.shape([(cx-u*9.6,shy),(cx+u*9.6,shy),(cx+u*9.0,hipy+u*2),(cx-u*9.0,hipy+u*2)])
    S.stroke([(cx-u*2.6,shy+u*0.4),(cx,shy+u*2.4),(cx+u*2.6,shy+u*0.4)],2.0,0.6,2)       # collar
    # ears (behind the fur)
    for sx in (-1,1):
        ear=[(cx+sx*u*8,hcy-hr*0.62),(cx+sx*u*13.5,hcy-hr*1.55),(cx+sx*u*15.5,hcy-hr*0.45)]
        S.shape(ear); S.stroke([(cx+sx*u*10,hcy-hr*0.7),(cx+sx*u*13.2,hcy-hr*1.25)],1.6,0.6,1)
    # head + fur
    S.shape(S.circle_pts(cx,hcy,hr,hr*0.96,40)); S.fur(cx,hcy,hr,n=110,a0=math.pi*1.02,a1=math.pi*1.98,ln=0.4); S.stroke(S.circle_pts(cx,hcy,hr*1.02,hr*0.98,40),None,None,2,closed=True)
    for sx in (-1,1):   # cheek tufts
        for k in range(6):
            a=math.pi*(0.08 if sx>0 else 0.92)+S.rng.normal(0,0.14); r0=hr*0.95
            S.d.line([S.P((cx+math.cos(a)*r0*sx*sx,hcy+math.sin(a)*r0)),S.P((cx+math.cos(a)*(r0+u*S.rng.uniform(2,4)),hcy+math.sin(a)*(r0+u*S.rng.uniform(1,3))))],fill=WHITE+(220,),width=int(S.lw*0.8*SS))
    # eyes
    ey=hcy-hr*0.08; lx,ly=look
    for sx in (-1,1):
        ex=cx+sx*hr*0.38; erx,ery=hr*0.27,hr*0.30
        S.ell(ex,ey,erx,ery,WHITE,outline=False)
        S.ell(ex+lx*erx*0.35,ey+ly*ery*0.4,erx*0.5,ery*0.5,BLACK,outline=False)
        S.ell(ex+lx*erx*0.35-erx*0.18,ey+ly*ery*0.4-ery*0.2,erx*0.12,ery*0.12,WHITE,outline=False)
        lid={"sad":0.48,"tired":0.55,"happy":0.0,"hopeful":0.05}.get(expr,0.12)+blink
        if lid>0:
            if expr=="sad":   # droopy lid slanting down to the outside
                S.fill([(ex-erx*1.1,ey-ery*1.2),(ex+erx*1.1,ey-ery*1.2),(ex+erx*1.1,ey-ery+2*ery*lid*(1.25 if sx>0 else 0.6)),(ex-erx*1.1,ey-ery+2*ery*lid*(0.6 if sx>0 else 1.25))])
                S.stroke([(ex-erx,ey-ery+2*ery*lid*(0.6 if sx>0 else 1.25)),(ex+erx,ey-ery+2*ery*lid*(1.25 if sx>0 else 0.6))],2.2,0.5,1)
            else:
                S.fill([(ex-erx*1.1,ey-ery*1.2),(ex+erx*1.1,ey-ery*1.2),(ex+erx*1.1,ey-ery+2*ery*lid),(ex-erx*1.1,ey-ery+2*ery*lid)])
        # brows
        by=ey-ery*1.35
        if expr=="sad": S.stroke([(ex-sx*erx*0.9,by+u*0.6),(ex+sx*erx*0.6,by-u*1.4)],2.4,0.5,2)
        elif expr in("happy","hopeful"): S.stroke([(ex-erx*0.8,by),(ex,by-u*1.2),(ex+erx*0.8,by)],2.2,0.5,2)
    # snout: small muzzle + nose
    my=hcy+hr*0.42
    S.ell(cx,my-hr*0.12,hr*0.10,hr*0.07,WHITE,outline=False)
    if expr=="sad": S.stroke(S.circle_pts(cx,my+hr*0.26,hr*0.12,hr*0.06,10,math.pi*1.1,math.pi*1.9),2.2,0.4,2)
    elif expr in("happy","hopeful"): S.stroke(S.circle_pts(cx,my+hr*0.08,hr*0.14,hr*0.10,10,math.pi*0.15,math.pi*0.85),2.2,0.4,2)
    else: S.stroke([(cx-hr*0.08,my+hr*0.18),(cx+hr*0.08,my+hr*0.18)],2.0,0.4,1)

# ---------- the wolf, SIDE view (wide shots, walking) ----------
def wolf_side(S,hipx,gy,h,P,facing=1,expr="neutral"):
    u=h/560.0; J=joints(P,facing); g=ground_offset(J)
    X=lambda p:(hipx+p[0]*u,gy+(p[1]-g)*u)
    def limb(a,b,wd):
        A,B=X(a),X(b); dx,dy=B[0]-A[0],B[1]-A[1]; L=math.hypot(dx,dy) or 1; nx,ny=-dy/L*wd*u/2,dx/L*wd*u/2
        S.shape([(A[0]+nx,A[1]+ny),(B[0]+nx,B[1]+ny),(B[0]-nx,B[1]-ny),(A[0]-nx,A[1]-ny)],w=2.0 if h<300 else 2.6,j=0.8 if h<300 else 1.4,passes=2)
    for sd in "B":
        limb(J['sh'],J['e'+sd],26); limb(J['e'+sd],J['h'+sd],24); limb((0,0),J['k'+sd],30); limb(J['k'+sd],J['a'+sd],28)
    N=J['neck']; S.shape([X((-46*facing,0)),X((46*facing,0)),X((N[0]+40*facing,N[1])),X((N[0]-40*facing,N[1]))],w=2.0 if h<300 else 2.6,j=0.8,passes=2)
    for sd in "F":
        limb((0,0),J['k'+sd],30); limb(J['k'+sd],J['a'+sd],28)
    C=X((N[0]+10*facing,N[1]-90)); r=95*u
    S.shape([(C[0]-r*0.1*facing,C[1]-r*0.7),(C[0]+r*0.25*facing,C[1]-r*1.55),(C[0]+r*0.6*facing,C[1]-r*0.6)],w=2.0,j=0.6,passes=2)
    S.shape(S.circle_pts(C[0],C[1],r,r*0.95,30),w=2.0 if h<300 else 2.6,j=0.8,passes=2)
    S.fur(C[0],C[1],r,n=26 if h<300 else 60,a0=math.pi*0.6,a1=math.pi*2.2,ln=0.3,w=1.4)
    S.shape([(C[0]+r*0.7*facing,C[1]-r*0.05),(C[0]+r*1.32*facing,C[1]+r*0.18),(C[0]+r*1.25*facing,C[1]+r*0.42),(C[0]+r*0.7*facing,C[1]+r*0.5)],w=1.8,j=0.6,passes=2)
    S.ell(C[0]+r*1.3*facing,C[1]+r*0.22,r*0.09,r*0.08,WHITE,outline=False)
    ex,ey=C[0]+r*0.42*facing,C[1]-r*0.1
    S.ell(ex,ey,r*0.3,r*0.34,WHITE,outline=False); S.ell(ex+r*0.1*facing,ey+(r*0.06 if expr=="sad" else 0),r*0.15,r*0.17,BLACK,outline=False)
    if expr=="sad": S.fill([(ex-r*0.35,ey-r*0.4),(ex+r*0.35,ey-r*0.4),(ex+r*0.35,ey-r*0.05),(ex-r*0.35,ey-r*0.18)])
    for sd in "F": limb(J['sh'],J['e'+sd],26); limb(J['e'+sd],J['h'+sd],24)

def cloud(S,cx,cy,w,rain_t=None,raining=True):
    blobs=[(-0.35,0.05,0.26),(-0.1,-0.12,0.32),(0.2,-0.05,0.3),(0.42,0.08,0.22),(0.05,0.12,0.3)]
    for bx,by,br in blobs: S.shape(S.circle_pts(cx+bx*w,cy+by*w,br*w,br*w*0.8,26),w=2.2,j=1.0,passes=2)
    for bx,by,br in blobs: S.fill(S.circle_pts(cx+bx*w,cy+by*w,br*w*0.86,br*w*0.66,26))
    if raining and rain_t is not None:
        for i in range(16):
            x=cx+(-0.45+0.9*(i/15))*w; ph=(rain_t*1.6+i*0.37)%1.0; y=cy+0.2*w+ph*w*1.5
            S.stroke([(x,y),(x-w*0.02,y+w*0.1)],2.0,0.4,1,a=200)
def sun(S,cx,cy,r,k):
    S.stroke(S.circle_pts(cx,cy,r,r,30),2.6,1.2,3,closed=True)
    for i in range(12):
        a=i*math.pi/6+k*0.4; S.stroke([(cx+math.cos(a)*r*1.3,cy+math.sin(a)*r*1.3),(cx+math.cos(a)*r*(1.3+0.5*min(1,k*2)),cy+math.sin(a)*r*(1.3+0.5*min(1,k*2)))],2.4,0.8,2)

# ---------- props ----------
def moon(S,cx,cy,r):
    S.stroke(S.circle_pts(cx,cy,r,r,30,math.pi*0.35,math.pi*1.65),None,None,3)
    S.stroke(S.circle_pts(cx+r*0.45,cy,r*0.78,r*0.86,24,math.pi*0.55,math.pi*1.45),None,None,3)
def plant(S,x,gy,g,flowers=0.0):
    """g 0..1 growth: sprout -> sapling -> tree. flowers 0..1"""
    h=20+g*620; w=6+g*26
    S.shape([(x-w/2,gy),(x+w/2,gy),(x+w*0.25,gy-h),(x-w*0.25,gy-h)])
    if g<0.25:
        for sd in (-1,1): S.shape([(x,gy-h),(x+sd*28*(0.4+g*2),gy-h-14),(x+sd*40*(0.4+g*2),gy-h+6)])
        return
    k=min(1,(g-0.25)/0.75)
    for sd,hy,L in ((-1,0.55,170),(1,0.68,150),(-1,0.82,110),(1,0.9,90)):
        y=gy-h*hy; S.stroke([(x,y),(x+sd*L*k,y-80*k)],None,None,2)
    if k>0.3:
        q=(k-0.3)/0.7; r=np.random.default_rng(3)
        for i in range(10):
            a=r.uniform(0,2*math.pi); rad=r.uniform(0,190)*q; cx=x+math.cos(a)*rad*1.1; cy=gy-h-40+math.sin(a)*rad*0.6
            rr=r.uniform(50,90)*q; S.shape(S.circle_pts(cx,cy,rr,rr*0.8,22))
        for i in range(int(18*flowers)):
            a=r.uniform(0,2*math.pi); rad=r.uniform(0,200); cx=x+math.cos(a)*rad*1.1; cy=gy-h-40+math.sin(a)*rad*0.6
            S.ell(cx,cy,9,9,WHITE,outline=False)
def stairs(S,x0,gy,n,sw,sh):
    pts=[(x0,gy)]
    for i in range(n): pts+= [(x0+i*sw,gy-(i+1)*sh),(x0+(i+1)*sw,gy-(i+1)*sh)]
    pts+=[(x0+n*sw,gy)]; S.fill(pts); S.stroke(pts[:-1],None,None,3)
def block(S,cx,cy,w,h,a):
    c,s_=math.cos(a),math.sin(a); pts=[(cx+x*c-y*s_,cy+x*s_+y*c) for x,y in ((-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2))]
    S.shape(pts); S.stroke([((pts[0][0]+pts[1][0])/2,(pts[0][1]+pts[1][1])/2),((pts[2][0]+pts[3][0])/2,(pts[2][1]+pts[3][1])/2)],None,None,1,a=120)
def counter(S,y,txt,size=80): S.text(y,[txt],size)

def ease(x): x=min(1,max(0,x)); return x*x*(3-2*x)
def lerp(a,b,k): return a+(b-a)*k
def sign(S,x,gy,text,size=60,h=230):
    """a small hand-drawn signpost with a word on it"""
    S.shape([(x-6,gy),(x+6,gy),(x+6,gy-h),(x-6,gy-h)],passes=2)
    f=ImageFont.truetype(FONT,int(size*SS)); w=f.getlength(text)/SS
    S.shape([(x-w/2-22,gy-h-size*1.25),(x+w/2+22,gy-h-size*1.25),(x+w/2+22,gy-h+8),(x-w/2-22,gy-h+8)])
    S.text_at(x,gy-h-size*1.2,text,size)
def star(S,cx,cy,r):
    pts=[]
    for i in range(10):
        a=-math.pi/2+i*math.pi/5; rr=r if i%2==0 else r*0.45; pts.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr))
    S.stroke(pts,None,None,2,closed=True)
def wall(S,x,gy,w,h): S.shape([(x,gy),(x+w,gy),(x+w,gy-h),(x,gy-h)]); S.stroke([(x,gy-h*0.5),(x+w,gy-h*0.5)],None,None,1,a=120)
def flower(S,x,gy,k=1.0,size=26):
    if k<=0: return
    h=size*2.4*k; S.stroke([(x,gy),(x,gy-h)],None,None,2)
    if k>0.5:
        r=size*0.42*min(1,(k-0.5)*2)
        for i in range(5):
            a=i*2*math.pi/5; S.ell(x+math.cos(a)*r*1.3,gy-h+math.sin(a)*r*1.3,r*0.75,r*0.75,BLACK,outline=True,w=S.lw*0.6)
        S.ell(x,gy-h,r*0.6,r*0.6,WHITE,outline=False)
