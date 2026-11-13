"""Motivation Reclaimed animation engine.

A video is a *spec* module (see specs/) that defines stacked panels, each with a
label and a scene function drawing the brand character and props over time.
The engine handles the signature look: black background, paper-grain texture,
soft panel light, brand character with gold kintsugi crack, watermark, impact
effects and the payoff ending (hero glows gold, others fade, sound logo).
"""
import math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

INK = (240, 236, 226)
GOLD = (214, 170, 72)
PALETTE = {  # calm label colours
    "slate": (128, 150, 184), "sage": (148, 176, 150), "sand": (212, 186, 140),
    "rose": (196, 140, 138), "stone": (160, 160, 168), "gold": GOLD,
}
WATERMARK = "MOTIVATION RECLAIMED"

# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, u): return a + (b - a) * u
def ease_out(u): u = clamp(u); return 1 - (1 - u) ** 3
def ease_in(u): u = clamp(u); return u ** 3
def ease_io(u): u = clamp(u); return u * u * (3 - 2 * u)
def ramp(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)

def track(t, keys, ease=ease_io):
    """Interpolate a number over [(time, value), ...]."""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1: return lerp(v0, v1, ease(ramp(t, t0, t1)))
    return keys[-1][1]

# ------------------------------------------------------------------ poses
# angles in degrees from straight down; + = forward (facing direction).
# lean = torso lean forward; hip = hip height above ground.
L_TORSO, L_NECK, R_HEAD, L_TH, L_SH, L_UA, L_FA = 112, 40, 27, 70, 68, 56, 54
POSES = {
    "stand":   dict(hip=136, lean=0,   thL=4,  shL=2,  thR=-6, shR=-4, uaL=8,   faL=4,   uaR=-4,  faR=-2),
    "proud":   dict(hip=136, lean=-4,  thL=8,  shL=4,  thR=-8, shR=-6, uaL=-14, faL=-6,  uaR=14,  faR=8),
    "push":    dict(hip=124, lean=38,  thL=34, shL=-10, thR=-30, shR=-40, uaL=78, faL=88,  uaR=72,  faR=84),
    "sit":     dict(hip=48,  lean=4,   thL=84, shL=4,  thR=78, shR=-2,  uaL=24,  faL=60,  uaR=18,  faR=54),
    "slump":   dict(hip=46,  lean=40,  thL=80, shL=10, thR=74, shR=4,   uaL=34,  faL=20,  uaR=28,  faR=14),
    "kneel":   dict(hip=78,  lean=18,  thL=88, shL=-2, thR=-20, shR=-90, uaL=20, faL=10,  uaR=14,  faR=6),
    "arms_up": dict(hip=136, lean=-6,  thL=10, shL=4,  thR=-10, shR=-6, uaL=165, faL=172, uaR=150, faR=160),
    "reach":   dict(hip=136, lean=6,   thL=4,  shL=2,  thR=-6, shR=-4, uaL=10,  faL=4,   uaR=140, faR=150),
    "phone":   dict(hip=136, lean=14,  thL=4,  shL=2,  thR=-6, shR=-4, uaL=8,   faL=4,   uaR=30,  faR=120),
    "lift":    dict(hip=128, lean=0,   thL=16, shL=-8, thR=-16, shR=8,  uaL=160, faL=180, uaR=-160, faR=-180),
    "squat":   dict(hip=96,  lean=24,  thL=70, shL=-20, thR=-70, shR=20, uaL=40, faL=20,  uaR=-40, faR=-20),
    "floor":   dict(hip=22,  lean=36,  thL=128, shL=28, thR=118, shR=18,  uaL=34,  faL=78,  uaR=24,  faR=68),  # sitting on the ground, knees up, head down
    "lie":     dict(hip=16,  lean=86,  thL=88, shL=90, thR=86, shR=88,  uaL=96,  faL=96,  uaR=80,  faR=84),
}
KEYS = ["hip", "lean", "thL", "shL", "thR", "shR", "uaL", "faL", "uaR", "faR"]

def blend(a, b, u):
    a = POSES[a] if isinstance(a, str) else a
    b = POSES[b] if isinstance(b, str) else b
    return {k: lerp(a[k], b[k], u) for k in KEYS}

def pose_track(t, keys):
    """keys: [(time, pose_name_or_dict), ...] -> blended pose dict."""
    if t <= keys[0][0]: return blend(keys[0][1], keys[0][1], 0)
    for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
        if t <= t1: return blend(p0, p1, ease_io(ramp(t, t0, t1)))
    return blend(keys[-1][1], keys[-1][1], 0)

def walk(phase, speed=1.0):
    """Walk/run cycle pose. speed 1 = walk, 2 = run."""
    a, b = math.sin(phase), math.sin(phase + math.pi)
    sw = 28 * speed
    return dict(hip=136 - abs(math.cos(phase)) * 5 * speed, lean=6 * speed,
                thL=sw * a, shL=sw * a - 18 * speed - 25 * max(0, -math.cos(phase)),
                thR=sw * b, shR=sw * b - 18 * speed - 25 * max(0, math.cos(phase)),
                uaL=-sw * 0.9 * a, faL=10 + 25 * speed - 20 * a,
                uaR=-sw * 0.9 * b, faR=10 + 25 * speed - 20 * b)

def climb(phase):
    """Stepping up stairs/slope: knees high."""
    a, b = math.sin(phase), math.sin(phase + math.pi)
    return dict(hip=130, lean=16, thL=40 * max(0, a) + 10, shL=-10,
                thR=40 * max(0, b) + 10, shR=-10, uaL=-25 * a, faL=30, uaR=-25 * b, faR=30)

def breathe(p, t, amt=2.0):
    p = dict(p); p["hip"] += math.sin(t * 2.4) * amt; return p

# ------------------------------------------------------------------ figure
def skeleton(x, gy, pose, facing=1, sc=1.0):
    r = math.radians
    hx, hy = x, gy - pose["hip"] * sc
    L_TORSO, L_NECK, L_TH, L_SH, L_UA, L_FA = (v * sc for v in (112, 40, 70, 68, 56, 54))
    lean = pose["lean"]
    neck = (hx + math.sin(r(lean)) * L_TORSO * facing, hy - math.cos(r(lean)) * L_TORSO)
    head = (neck[0] + math.sin(r(lean)) * L_NECK * facing, neck[1] - math.cos(r(lean)) * L_NECK)
    def v(a): return (math.sin(r(a)) * facing, math.cos(r(a)))
    def chain(o, a1, l1, a2, l2):
        v1 = v(a1); p1 = (o[0] + v1[0] * l1, o[1] + v1[1] * l1)
        v2 = v(a2); return p1, (p1[0] + v2[0] * l2, p1[1] + v2[1] * l2)
    sh = (lerp(hx, neck[0], 0.88), lerp(hy, neck[1], 0.88))
    kL, fL = chain((hx, hy), pose["thL"], L_TH, pose["shL"], L_SH)
    kR, fR = chain((hx, hy), pose["thR"], L_TH, pose["shR"], L_SH)
    eL, hL = chain(sh, pose["uaL"], L_UA, pose["faL"], L_FA)
    eR, hR = chain(sh, pose["uaR"], L_UA, pose["faR"], L_FA)
    return dict(hip=(hx, hy), neck=neck, head=head, sh=sh, kL=kL, fL=fL, kR=kR, fR=fR,
                eL=eL, hL=hL, eR=eR, hR=hR, facing=facing, pose=pose)

# ------------------------------------------------------------------ panel drawing context
class Ctx:
    """Drawing helpers handed to a scene function. Coordinates are panel-local.
    d = crisp layer, g = glow layer (half res, blurred & added)."""
    def __init__(self, d, g, w, h, ground, t, accent):
        self.d, self.g, self.w, self.h, self.ground, self.t, self.accent = d, g, w, h, ground, t, accent
        self.fx = []  # effects requested by the scene (impact etc.)

    # --- figure
    scale = 0.8  # brand character size (fits 3-4 stacked panels)

    def figure(self, x, pose, facing=1, crack=False, gy=None, col=INK, alpha=1.0, glow=0.0, scale=None, fill=1.0):
        """crack=True draws the gold kintsugi crack; fill<1 shows it as a dark break
        that fills with gold from the head down (0 = empty break, 1 = full gold)."""
        sc = scale or self.scale
        gy = self.ground if gy is None else gy
        if isinstance(pose, str): pose = POSES[pose]
        s = skeleton(x, gy, pose, facing, sc)
        low = max(s["fL"][1], s["fR"][1], s["kL"][1], s["kR"][1]) - gy - 4
        if low > 0:  # never sink below the ground mid-transition
            s = {k: ((v[0], v[1] - low) if isinstance(v, tuple) else v) for k, v in s.items()}
        s["sc"] = sc
        c = tuple(int(lerp(12, ch, alpha)) for ch in col)
        w = int(15 * max(0.75, sc))
        RH = R_HEAD * sc
        d = self.d
        def seg(*pts):
            d.line(pts, fill=c, width=w, joint="curve")
            for p in pts: d.ellipse([p[0]-w/2, p[1]-w/2, p[0]+w/2, p[1]+w/2], fill=c)
        seg(s["hip"], s["kL"], s["fL"]); seg(s["sh"], s["eL"], s["hL"])
        seg(s["hip"], s["neck"]); seg(s["hip"], s["kR"], s["fR"]); seg(s["sh"], s["eR"], s["hR"])
        hx, hy = s["head"]
        d.ellipse([hx-RH, hy-RH, hx+RH, hy+RH], fill=c)
        if crack: self._crack(s, glow, fill)
        return s

    def _crack(self, s, glow, fill=1.0):
        hx, hy = s["head"]; nx, ny = s["neck"]; px, py = s["hip"]
        R_HEAD = 27 * s["sc"]
        dx, dy = px - nx, py - ny; L = math.hypot(dx, dy) or 1
        vx, vy = -dy / L, dx / L
        pts = [(hx - R_HEAD*0.35, hy - R_HEAD*0.95), (hx + R_HEAD*0.2, hy - R_HEAD*0.25),
               (hx - R_HEAD*0.25, hy + R_HEAD*0.45), (nx + vx*3, ny + vy*3)]
        for k, f in enumerate([0.3, 0.55, 0.8, 1.0]):
            o = 6 if k % 2 == 0 else -6
            pts.append((nx + dx*f + vx*o, ny + dy*f + vy*o))
        if fill < 1.0:
            self.d.line(pts, fill=(18, 18, 22), width=7, joint="curve")
            segs = list(zip(pts, pts[1:])); lens = [math.hypot(b[0]-a[0], b[1]-a[1]) for a, b in segs]
            left = sum(lens) * clamp(fill); gp = [pts[0]]
            for (a, b), l in zip(segs, lens):
                if left <= 0: break
                u = min(1, left / (l or 1)); gp.append((lerp(a[0], b[0], u), lerp(a[1], b[1], u))); left -= l
            if len(gp) > 1 and fill > 0:
                self.d.line(gp, fill=GOLD, width=7, joint="curve")
                k = 0.5; tip = gp[-1]
                self.g.ellipse([(tip[0]-26)*k, (tip[1]-26)*k, (tip[0]+26)*k, (tip[1]+26)*k], fill=(200, 150, 60))
        else:
            self.d.line(pts, fill=GOLD, width=7, joint="curve")
        if glow > 0:
            k = 0.5
            self.g.line([(x*k, y*k) for x, y in pts], fill=tuple(int(c*glow) for c in (255, 190, 80)), width=int(10 + 10*glow))
            r = 140 * glow
            self.g.ellipse([(hx-r)*k, (hy-r)*k, (hx+r)*k, (hy+r*2.2)*k], fill=tuple(int(c*glow*0.3) for c in (255, 170, 60)))

    # --- light
    def light(self, x, y, r, col=None, a=1.0):
        col = col or self.accent; k = 0.5
        self.g.ellipse([(x-r)*k, (y-r)*k, (x+r)*k, (y+r)*k], fill=tuple(int(c*0.35*a) for c in col))

    def spot(self, x, a=1.0, col=None, width=260):
        """Soft overhead light cone onto the ground at x."""
        col = col or self.accent; k = 0.5
        self.g.polygon([(x*k, -20*k), ((x-width)*k, self.ground*k), ((x+width)*k, self.ground*k)],
                       fill=tuple(int(c*0.16*a) for c in col))

    # --- props
    def ground_line(self, col=(70, 70, 78)):
        self.d.line([(0, self.ground), (self.w, self.ground)], fill=col, width=3)

    def slope(self, x0, x1, rise, col=(70, 70, 78)):
        """Hill from (x0, ground) up to (x1, ground-rise). Returns y(x)."""
        gy = self.ground
        self.d.polygon([(x0, gy), (x1, gy - rise), (x1, gy), ], fill=(22, 22, 26))
        self.d.line([(0, gy), (x0, gy), (x1, gy - rise), (self.w, gy - rise)], fill=col, width=3)
        return lambda x: gy - rise * clamp((x - x0) / (x1 - x0))

    def stairs(self, x0, n, sw=70, sh=34, col=(70, 70, 78)):
        gy = self.ground; pts = [(0, gy), (x0, gy)]
        for i in range(n):
            pts += [(x0 + i*sw, gy - (i+1)*sh), (x0 + (i+1)*sw, gy - (i+1)*sh)]
        pts.append((self.w, gy - n*sh))
        self.d.polygon(pts + [(self.w, gy), (x0, gy)], fill=(22, 22, 26))
        self.d.line(pts, fill=col, width=3)
        return lambda x: gy - sh * clamp(math.floor((x - x0) / sw) + 1, 0, n) if x >= x0 else gy

    def boulder(self, x, y_bottom, r, rot=0.0):
        cx, cy = x, y_bottom - r
        pts = [(cx + math.cos(a + rot) * r * (0.92 + 0.08 * math.sin(a * 3)),
                cy + math.sin(a + rot) * r * (0.92 + 0.08 * math.sin(a * 3))) for a in np.linspace(0, 2*math.pi, 24)]
        self.d.polygon(pts, fill=(40, 40, 46), outline=(100, 100, 110))
        for k in range(3):
            a = rot + k * 2.1
            self.d.line([(cx + math.cos(a)*r*0.2, cy + math.sin(a)*r*0.2), (cx + math.cos(a+0.4)*r*0.7, cy + math.sin(a+0.4)*r*0.7)],
                        fill=(90, 90, 98), width=3)

    def wall(self, x, w, h, cracks=0):
        gy = self.ground
        self.d.polygon([(x, gy), (x, gy-h+20), (x+20, gy-h), (x+w, gy-h), (x+w, gy)], fill=(40, 42, 50), outline=(90, 92, 104))
        r = random.Random(int(x))
        for i in range(int(cracks)):
            y = gy - h * r.uniform(0.2, 0.9)
            self.d.line([(x, y), (x + w*0.3, y + r.uniform(-30, 30)), (x + w*0.55, y + r.uniform(-50, 50))], fill=(120, 124, 136), width=3)

    def barbell(self, s, col=(150, 150, 160)):
        (lx, ly), (rx, ry) = s["hL"], s["hR"]
        cx, cy = (lx + rx) / 2, (ly + ry) / 2
        self.d.line([(cx - 120, cy), (cx + 120, cy)], fill=col, width=8)
        for sx in (-1, 1):
            self.d.rounded_rectangle([cx + sx*110 - 12, cy - 38, cx + sx*110 + 12, cy + 38], 5, fill=(80, 80, 90))

    def phone(self, s, glow=True):
        x, y = s["hR"]
        self.d.rounded_rectangle([x - 9, y - 22, x + 9, y + 6], 4, fill=(30, 34, 46), outline=(170, 190, 230))
        if glow: self.light(x, y - 8, 70, (150, 180, 255), 0.9)

    def bed(self, x, w=300):
        gy = self.ground
        self.d.rounded_rectangle([x, gy - 60, x + w, gy - 20], 10, fill=(50, 52, 62))
        self.d.rectangle([x, gy - 20, x + 14, gy], fill=(50, 52, 62)); self.d.rectangle([x + w - 14, gy - 20, x + w, gy], fill=(50, 52, 62))
        self.d.rounded_rectangle([x + w - 90, gy - 82, x + w - 10, gy - 58], 10, fill=(90, 92, 104))
        return gy - 60

    def flag(self, x, y, wave=0.0):
        self.d.line([(x, y), (x, y - 140)], fill=(150, 150, 160), width=5)
        self.d.polygon([(x, y - 140), (x + 70, y - 122 + 6 * math.sin(wave)), (x, y - 100)], fill=GOLD)

    def door(self, x, w=150, h=300, open_=0.0, light=0.0):
        """Door standing on the ground. open_ 0..1 swings it open; light 0..1 = gold light through it."""
        gy = self.ground
        self.d.rectangle([x - 10, gy - h - 10, x + w + 10, gy], fill=(30, 30, 36), outline=(100, 100, 110), width=3)
        if light > 0:
            self.d.rectangle([x, gy - h, x + w, gy], fill=tuple(int(lerp(12, c, light * 0.9)) for c in (255, 214, 140)))
            self.light(x + w / 2, gy - h / 2, h * 0.9, GOLD, light)
            k = 0.5
            self.g.polygon([(x*k, gy*k), ((x+w)*k, gy*k), ((x+w+260*light)*k, (gy+4)*k), ((x-260*light)*k, (gy+4)*k)], fill=tuple(int(c*0.5*light) for c in GOLD))
        else:
            self.d.rectangle([x, gy - h, x + w, gy], fill=(8, 8, 10))
        ww = w * (1 - 0.82 * clamp(open_))
        self.d.polygon([(x, gy - h), (x + ww, gy - h + 14 * open_), (x + ww, gy - 14 * open_), (x, gy)], fill=(58, 56, 62), outline=(120, 118, 126))
        if ww > 30: self.d.ellipse([x + ww - 26, gy - h / 2 - 6, x + ww - 14, gy - h / 2 + 6], fill=(170, 160, 130))

    def mirror(self, x, w=260, h=420, col=(120, 122, 134)):
        """Standing mirror frame; returns (x0, x1) of the glass."""
        gy = self.ground
        self.d.rounded_rectangle([x, gy - h, x + w, gy - 10], 16, fill=(16, 17, 22), outline=col, width=6)
        self.d.line([(x + 30, gy - h + 40), (x + 70, gy - h + 90)], fill=(50, 52, 60), width=4)
        return x, x + w

    def bar(self, x, y, w, frac, col=None, h=16):
        """Progress bar."""
        col = col or self.accent
        self.d.rounded_rectangle([x, y, x + w, y + h], h // 2, outline=(80, 80, 88), width=2)
        if frac > 0.01:
            self.d.rounded_rectangle([x + 3, y + 3, x + 3 + (w - 6) * clamp(frac), y + h - 3], (h - 6) // 2, fill=col)
            k = 0.5; ex = x + (w - 6) * clamp(frac)
            self.g.ellipse([(ex-24)*k, (y-16)*k, (ex+24)*k, (y+h+16)*k], fill=tuple(int(c*0.4) for c in col))

    def text(self, x, y, s, size=30, col=(200, 200, 205), anchor="mm"):
        f = ImageFont.truetype(FONT_B, size)
        self.d.text((x, y), s, font=f, fill=col, anchor=anchor)

    # --- effects
    def sparks(self, x, y, t0, n=40, spread=(-170, -10), speed=(200, 700), life=0.7, col=(255, 210, 140), seed=0):
        a = self.t - t0
        if a < 0 or a > life: return
        r = random.Random(seed or int(t0 * 1000))
        k = 0.5
        for _ in range(n):
            ang = math.radians(r.uniform(*spread)); sp = r.uniform(*speed); lf = r.uniform(0.5, 1) * life
            if a > lf: continue
            px = x + math.cos(ang) * sp * a; py = y + math.sin(ang) * sp * a + 900 * a * a
            fade = 1 - a / lf
            self.d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=tuple(int(c * fade + 20) for c in col))
            self.g.ellipse([(px-7)*k, (py-7)*k, (px+7)*k, (py+7)*k], fill=tuple(int(c * fade * 0.6) for c in col))

    def dust(self, x, y, t0, life=0.6, seed=0):
        a = self.t - t0
        if a < 0 or a > life: return
        r = random.Random(seed or int(t0 * 997))
        for _ in range(10):
            dx = r.uniform(-1, 1); px = x + dx * 90 * ease_out(a / life); py = y - r.uniform(0, 30) * ease_out(a / life)
            rr = 8 + 18 * a / life; c = int(70 * (1 - a / life))
            self.d.ellipse([px - rr, py - rr, px + rr, py + rr], outline=(c, c, c + 4), width=2)

    def impact(self, t0, strength=1.0):
        """Request a camera hit (shake + chromatic split) on this panel at t0."""
        self.fx.append(("impact", t0, strength))


# ------------------------------------------------------------------ overlays (precomputed)
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_d2 = ((_xx - W/2) / (W*0.62))**2 + ((_yy - H/2) / (H*0.62))**2
VIGN = (np.clip(1.15 - _d2*0.75, 0.3, 1.0) * np.where((_yy.astype(int) % 4) == 0, 0.95, 1.0))[..., None].astype(np.float32)
_rng = np.random.default_rng(3)
GRAIN = [_rng.normal(0, 6.5, (H, W, 1)).astype(np.float32) for _ in range(6)]
_fib = Image.fromarray((_rng.random((H//8, W//8)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
PAPER = ((np.asarray(_fib, np.float32) - 128) * 0.035)[..., None]
DUST = [(random.Random(i).uniform(0, W), random.Random(i+99).uniform(0, H), random.Random(i+7).uniform(4, 14),
         random.Random(i+3).uniform(1, 2.6), random.Random(i+5).uniform(0, 6.28)) for i in range(55)]

def tracked(d, x, y, text, font, fill, tr=0, anchor="l"):
    w = sum(font.getlength(c) for c in text) + tr * (len(text) - 1)
    if anchor == "c": x -= w / 2
    elif anchor == "r": x -= w
    for c in text:
        d.text((x, y), c, font=font, fill=fill); x += font.getlength(c) + tr

def chroma(arr, k):
    k = int(k)
    if k <= 0: return arr
    arr[:, :, 0] = np.roll(arr[:, :, 0], k, axis=1); arr[:, :, 2] = np.roll(arr[:, :, 2], -k, axis=1)
    return arr

# ------------------------------------------------------------------ render
def render_frame(spec, fi):
    t = fi / FPS
    panels = spec.PANELS
    n = len(panels)
    gap = 20
    ph = getattr(spec, "PANEL_H", {1: 1250, 2: 600, 3: 420, 4: 340}[n])
    total = n * ph + (n - 1) * gap
    top = (H - total) // 2 - 30
    ground = int(ph * 0.885)
    payoff = getattr(spec, "PAYOFF", None)
    hero = getattr(spec, "HERO", n - 1)
    dim = ease_io(ramp(t, payoff + 0.3, payoff + 0.9)) if payoff is not None else 0
    F_LABEL = ImageFont.truetype(FONT_B, 44 if n <= 3 else 38)
    fig_scale = getattr(spec, "FIG_SCALE", {1: 1.6, 2: 1.0, 3: 0.8, 4: 0.68}[n])

    frame = np.zeros((H, W, 3), np.float32)
    shake_global = 0.0
    ca = 0.0
    if payoff is not None and 0 <= t - payoff < 0.45:
        shake_global = 14 * (1 - (t - payoff) / 0.45); ca = 12 * (1 - (t - payoff) / 0.45)

    for i, P in enumerate(panels):
        accent = PALETTE.get(P.get("color", "stone"), P.get("color")) if isinstance(P.get("color", "stone"), str) else P["color"]
        if i == hero: accent = GOLD if P.get("color") is None else accent
        pimg = Image.new("RGB", (W, ph)); glow = Image.new("RGB", (W // 2, ph // 2))
        ctx = Ctx(ImageDraw.Draw(pimg), ImageDraw.Draw(glow), W, ph, ground, t, accent)
        ctx.scale = fig_scale
        ctx.is_hero = (i == hero)
        ctx.payoff_glow = ease_out(ramp(t, payoff, payoff + 0.5)) if (payoff is not None and i == hero) else 0.0
        P["scene"](ctx, t)
        if not P.get("no_ground"): pass
        glow = glow.filter(ImageFilter.GaussianBlur(12)).resize((W, ph), Image.BILINEAR)
        g2 = glow.filter(ImageFilter.GaussianBlur(28))
        pa = np.asarray(pimg, np.float32) + np.asarray(glow, np.float32) * 1.25 + np.asarray(g2, np.float32) * 0.9
        if i != hero and dim > 0:
            lum = pa.mean(axis=2, keepdims=True); pa = lerp(pa, lum * 0.32, dim)
        lab = Image.fromarray(np.clip(pa, 0, 255).astype(np.uint8)); dl = ImageDraw.Draw(lab)
        lc = accent if not (i != hero and dim > 0) else tuple(int(lerp(c, 80, dim)) for c in accent)
        label = P["label"](t) if callable(P.get("label")) else P.get("label")
        if label: tracked(dl, 48, 26, label, F_LABEL, lc, tr=7)
        if P.get("sub") and t >= P.get("sub_t", 0):
            sc = (175, 175, 180) if i != hero else (235, 220, 190)
            if i != hero and dim > 0: sc = tuple(int(lerp(c, 70, dim)) for c in sc)
            tracked(dl, 50, 82, P["sub"], ImageFont.truetype(FONT_B, 26), sc, tr=4)
        pa = np.asarray(lab, np.float32)
        # per-panel impacts
        amp = shake_global
        for (kind, t0, st) in ctx.fx:
            if 0 <= t - t0 < 0.18: amp = max(amp, 9 * st * (1 - (t - t0) / 0.18)); ca = max(ca, 5 * st * (1 - (t - t0) / 0.18))
        ox = int(math.sin(t * 97 + i) * amp); oy = int(math.cos(t * 83 + i * 2) * amp)
        y0 = top + i * (ph + gap) + oy
        sx0, sx1 = max(0, ox), min(W, W + ox)
        frame[y0:y0 + ph, sx0:sx1] = pa[:, sx0 - ox:sx1 - ox]
        bc = np.array([34, 34, 40], np.float32)
        if i == hero and payoff is not None: bc = lerp(bc, np.array(GOLD, np.float32), dim * (0.7 + 0.3 * math.sin(t * 5)))
        frame[y0:y0 + 2] = bc; frame[y0 + ph - 2:y0 + ph] = bc

    img = Image.fromarray(np.clip(frame, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
    for (x, y, sp, sz, phs) in DUST:
        yy = (y - t * sp * 6) % H; xx = x + math.sin(t + phs) * 18; c = int(48 + 30 * math.sin(t * 2 + phs))
        d.ellipse([xx, yy, xx + sz, yy + sz], fill=(c, int(c * 0.85), int(c * 0.6)))
    tracked(d, W / 2, top + total + 40, WATERMARK, ImageFont.truetype(FONT, 24), (92, 90, 84), tr=10, anchor="c")

    arr = np.asarray(img, np.float32).copy()
    arr = chroma(arr, ca)
    if payoff is not None and 0 <= t - payoff < 0.3:
        f = (1 - (t - payoff) / 0.3) ** 1.5 * 0.7
        arr = lerp(arr, np.array([255, 226, 170], np.float32), f)
    arr = arr * VIGN + GRAIN[fi % 6] + PAPER
    if t < 0.15: arr *= t / 0.15
    return np.clip(arr, 0, 255).astype(np.uint8)


def render(spec, out, workers=2):
    """Render spec to out (.mp4) with sound. Splits frames across processes."""
    import os, sys, tempfile
    from concurrent.futures import ProcessPoolExecutor
    from . import sfx
    nf = int(spec.DURATION * FPS)
    tmp = tempfile.mkdtemp()
    chunks = [(i * nf // workers, (i + 1) * nf // workers) for i in range(workers)]
    spec_path = spec.__file__
    with ProcessPoolExecutor(workers) as ex:
        parts = list(ex.map(_render_chunk, [(spec_path, a, b, f"{tmp}/part{k}.mp4") for k, (a, b) in enumerate(chunks)]))
    lst = f"{tmp}/list.txt"
    open(lst, "w").write("".join(f"file {p}\n" for p in parts))
    wav = f"{tmp}/sfx.wav"
    sfx.build(spec, wav)
    tmp_out = out + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "160k", "-shortest", tmp_out], check=True)
    os.replace(tmp_out, out)
    return out


def load_spec(path):
    import importlib.util
    s = importlib.util.spec_from_file_location("spec", path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def _render_chunk(args):
    spec_path, a, b, out = args
    spec = load_spec(spec_path)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", out + ".tmp.mp4"], stdin=subprocess.PIPE)
    for fi in range(a, b):
        p.stdin.write(render_frame(spec, fi).tobytes())
    p.stdin.close()
    if p.wait() != 0: raise RuntimeError("ffmpeg failed")
    import os; os.replace(out + ".tmp.mp4", out)
    return out
