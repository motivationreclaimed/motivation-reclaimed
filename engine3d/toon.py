"""Cartoon style: flat 2D bean-head character cards (plum outlines) in a colourful 3D world with ink edges.
Inspired by the owner's cartoon-short skill look; pure Python (numpy + cv2 + PIL)."""
import math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
PLUM = (58, 30, 56)
INK = (28, 20, 30)
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
GOLD = (255, 196, 92)

def font(sz, bold=False): return ImageFont.truetype(SERIF_B if bold else SERIF, int(sz))
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u
def mix(a, b, k): return {key: lerp(a.get(key, 0), b.get(key, 0), k) for key in set(a) | set(b)}

# ---------------- camera ----------------
class Cam:
    def __init__(self, pos, tgt, f=1300.0, cx=W / 2, cy=H / 2):
        self.C = np.array(pos, np.float32); fw = np.array(tgt, np.float32) - self.C
        self.f = fw / np.linalg.norm(fw); up = np.array([0, 1, 0], np.float32)
        r = np.cross(up, self.f); self.r = r / np.linalg.norm(r); self.u = np.cross(self.f, self.r)
        self.F, self.cx, self.cy = f, cx, cy
    def proj(self, P):
        d = np.asarray(P, np.float32) - self.C; z = float(d @ self.f)
        if z < 0.15: return None
        return (self.cx + self.F * float(d @ self.r) / z, self.cy - self.F * float(d @ self.u) / z, z)
    def depth(self, P): return float((np.asarray(P, np.float32) - self.C) @ self.f)

# ---------------- world drawing (toon fills + black ink) ----------------
def quad(img, cam, pts, col, ink=2):
    q = [cam.proj(p) for p in pts]
    if not all(q): return
    poly = np.array([(int(a[0]), int(a[1])) for a in q], np.int32)
    cv2.fillConvexPoly(img, poly, col, cv2.LINE_AA)
    if ink: cv2.polylines(img, [poly], True, INK, ink, cv2.LINE_AA)

def box(img, cam, x0, x1, y0, y1, z0, z1, col, ink=2):
    """toon box: top lighter, front (z0) base, side (x facing camera) darker"""
    c = np.array(col, np.float32)
    top, front, side = tuple((c * 1.12).clip(0, 255).tolist()), tuple(c.tolist()), tuple((c * 0.78).tolist())
    sx = x0 if cam.C[0] < x0 else (x1 if cam.C[0] > x1 else None)
    if sx is not None: quad(img, cam, [(sx, y0, z0), (sx, y0, z1), (sx, y1, z1), (sx, y1, z0)], side, ink)
    quad(img, cam, [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], front, ink)
    if cam.C[1] > y1: quad(img, cam, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], top, ink)

def sky(img, top, bottom, horizon=0.5):
    yy = np.linspace(0, 1, img.shape[0], dtype=np.float32)[:, None]
    k = np.clip(yy / horizon, 0, 1)
    img[:] = (np.array(top, np.float32) * (1 - k) + np.array(bottom, np.float32) * k)[:, None, :]

def paint_noise(img, amt=6, seed=1):
    """painted texture feel"""
    n = np.random.default_rng(seed).normal(0, amt, (img.shape[0] // 4, img.shape[1] // 4, 1)).astype(np.float32)
    img += cv2.resize(cv2.GaussianBlur(n, (0, 0), 1.2), (img.shape[1], img.shape[0]))[..., None]

def blob(img, x, y, rx, ry, col, k=1.0):
    h, w = img.shape[:2]
    x0, x1, y0, y1 = int(max(0, x - rx * 2)), int(min(w, x + rx * 2)), int(max(0, y - ry * 2)), int(min(h, y + ry * 2))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    g = np.exp(-(((xx - x) / rx) ** 2 + ((yy - y) / ry) ** 2)) * k
    img[y0:y1, x0:x1] += g[..., None] * np.asarray(col, np.float32)

# ---------------- characters ----------------
# angles in degrees from straight down, + = forward (toward facing)
STAND = dict(lean=0, thB=3, shB=3, thF=-3, shF=-3, uaB=-8, faB=-4, uaF=8, faF=10, head=0)
WAVE = dict(STAND, uaF=128, faF=165)
PHONE = dict(STAND, uaF=40, faF=120, uaB=30, faB=110, head=22, lean=4)
SIT = dict(lean=8, thB=88, shB=4, thF=84, shF=2, uaB=20, faB=60, uaF=25, faF=65, head=10)
SIT_SAD = dict(SIT, lean=24, head=30, uaB=50, faB=95, uaF=55, faF=100)
ARMS_UP = dict(STAND, uaB=-138, faB=-150, uaF=132, faF=150, head=-14)
HOLD = dict(STAND, uaF=60, faF=95, uaB=50, faB=90)              # holding something in front (jar, bag)
LIE = None                                                       # use lie_card()
def walk(p, amp=26):
    s = math.sin(p)
    return dict(lean=4, thB=amp * s, shB=amp * s - 18 * (0.5 + 0.5 * math.cos(p)), thF=-amp * s,
                shF=-amp * s - 18 * (0.5 - 0.5 * math.cos(p)), uaB=-amp * 0.9 * s, faB=-amp * 0.9 * s + 25,
                uaF=amp * 0.9 * s, faF=amp * 0.9 * s + 25, head=0)
def run(p): return dict(walk(p, 42), lean=14, faB=-38 * math.sin(p) + 80, faF=38 * math.sin(p) + 80)

LOOKS = {
    "hero":    dict(skin=(222, 172, 128), top=(52, 54, 64), legs=(40, 42, 50), shoe=(30, 30, 34), hair=(44, 32, 28), crack=True),
    "mustard": dict(skin=(198, 140, 100), top=(214, 168, 64), legs=(70, 82, 110), shoe=(60, 50, 44), hair=(30, 24, 22), crack=False),
    "teal":    dict(skin=(150, 104, 76), top=(70, 150, 150), legs=(56, 60, 74), shoe=(240, 240, 236), hair=(20, 18, 18), crack=False),
    "coral":   dict(skin=(238, 196, 160), top=(222, 110, 96), legs=(60, 70, 96), shoe=(50, 50, 56), hair=(160, 96, 50), crack=False),
    "grey":    dict(skin=(214, 168, 130), top=(122, 128, 140), legs=(76, 80, 92), shoe=(54, 54, 60), hair=(70, 60, 54), crack=False),
}

def _v(a, L, facing): a = math.radians(a); return (math.sin(a) * L * facing, math.cos(a) * L)

def _face(d, cx, cy, s, facing, expr, look):
    fx = 26 * s * facing
    ex = [cx + fx - 40 * s, cx + fx + 40 * s]
    lid = {"tired": 0.45, "sad": 0.25, "determined": 0.3}.get(expr, 0.0)
    for x in ex:
        ew, eh = 25 * s, 31 * s * (1.25 if expr == "shock" else 1)
        d.ellipse([x - ew, cy - eh, x + ew, cy + eh], fill=(250, 248, 242), outline=PLUM, width=max(2, int(6 * s)))
        pr = 12 * s * (0.75 if expr == "shock" else 1)
        px, py = x + 8 * s * facing, cy + (6 * s if expr in ("sad", "tired") else 2 * s)
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=PLUM)
        if lid: d.rectangle([x - ew - 2, cy - eh - 2, x + ew + 2, cy - eh + 2 * eh * lid], fill=look["skin"])
        if lid: d.line([x - ew, cy - eh + 2 * eh * lid, x + ew, cy - eh + 2 * eh * lid], fill=PLUM, width=max(2, int(6 * s)))
    bw = max(3, int(9 * s))
    if expr == "determined":
        d.line([ex[0] - 26 * s, cy - 48 * s, ex[0] + 22 * s, cy - 36 * s], fill=PLUM, width=bw)
        d.line([ex[1] - 22 * s, cy - 36 * s, ex[1] + 26 * s, cy - 48 * s], fill=PLUM, width=bw)
    elif expr in ("worried", "sad"):
        d.line([ex[0] - 24 * s, cy - 38 * s, ex[0] + 22 * s, cy - 50 * s], fill=PLUM, width=bw)
        d.line([ex[1] - 22 * s, cy - 50 * s, ex[1] + 24 * s, cy - 38 * s], fill=PLUM, width=bw)
    mx, my = cx + fx, cy + 62 * s
    if expr in ("happy", "determined"):
        d.arc([mx - 34 * s, my - 30 * s, mx + 34 * s, my + 22 * s], 15, 165, fill=PLUM, width=bw)
    elif expr in ("sad", "worried", "tired"):
        d.arc([mx - 26 * s, my, mx + 26 * s, my + 34 * s], 200, 340, fill=PLUM, width=bw)
    elif expr == "shock":
        d.ellipse([mx - 14 * s, my - 10 * s, mx + 14 * s, my + 22 * s], fill=PLUM)
    else:
        d.line([mx - 20 * s, my + 6 * s, mx + 20 * s, my + 6 * s], fill=PLUM, width=bw)

def _crack(d, pts, s, gold=GOLD):
    d.line(pts, fill=(120, 80, 30), width=max(3, int(11 * s)), joint="curve")
    d.line(pts, fill=gold, width=max(2, int(6 * s)), joint="curve")

def card(pose, look="hero", expr="neutral", facing=1, hpx=500, prop=None):
    """Draw a character card. Returns (RGBA image, anchor=(x of feet, y of soles), extras dict)."""
    L = LOOKS[look]
    s = hpx / 1000 * 2                          # supersample x2
    Wc, Hc = int(700 * s), int(1100 * s)
    im = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # skeleton in design units (hip at 0,0), then shift so lowest foot sits at sole line
    TH, SH, TO, UA, FA = 165, 160, 215, 118, 110
    def leg(th, sh):
        k = _v(th, TH, facing); f = _v(sh, SH, facing); return (k[0], k[1]), (k[0] + f[0], k[1] + f[1])
    kB, fB = leg(pose["thB"], pose["shB"]); kF, fF = leg(pose["thF"], pose["shF"])
    lowest = max(fB[1], fF[1])
    ox, oy = Wc / 2, Hc - 40 * s - lowest * s
    P = lambda p: (ox + p[0] * s, oy + p[1] * s)
    lean = math.radians(pose["lean"])
    neck = (math.sin(lean) * TO * facing, -math.cos(lean) * TO)
    sh_ = (neck[0] * 0.92, neck[1] * 0.92)
    def arm(ua, fa):
        e = _v(ua, UA, facing); h = _v(fa, FA, facing)
        return (sh_[0] + e[0], sh_[1] + e[1]), (sh_[0] + e[0] + h[0], sh_[1] + e[1] + h[1])
    eB, hB = arm(pose["uaB"], pose["faB"]); eF, hF = arm(pose["uaF"], pose["faF"])
    ow = 7 * s
    def limb(a, b, c, wd, col):
        pts = [P(a), P(b), P(c)]
        d.line(pts, fill=PLUM, width=int((wd + 14) * s), joint="curve")
        for p in pts: d.ellipse([p[0] - (wd + 14) * s / 2, p[1] - (wd + 14) * s / 2, p[0] + (wd + 14) * s / 2, p[1] + (wd + 14) * s / 2], fill=PLUM)
        d.line(pts, fill=col, width=int(wd * s), joint="curve")
        for p in pts: d.ellipse([p[0] - wd * s / 2, p[1] - wd * s / 2, p[0] + wd * s / 2, p[1] + wd * s / 2], fill=col)
    def shoe(fp, dark=1.0):
        x, y = P(fp); col = tuple(int(c * dark) for c in L["shoe"])
        d.ellipse([x - 30 * s + 22 * s * facing, y - 26 * s, x + 30 * s + 22 * s * facing + 10 * s, y + 12 * s], fill=col, outline=PLUM, width=int(ow))
    def hand(hp): x, y = P(hp); d.ellipse([x - 24 * s, y - 24 * s, x + 24 * s, y + 24 * s], fill=L["skin"], outline=PLUM, width=int(ow))
    dk = lambda c, k=0.82: tuple(int(v * k) for v in c)
    # back limbs
    limb(sh_, eB, hB, 50, dk(L["top"])); hand(hB)
    limb((0, 0), kB, fB, 62, dk(L["legs"])); shoe(fB, 0.85)
    # torso (pill)
    a, b = P((0, 10)), P(neck)
    d.line([a, b], fill=PLUM, width=int(168 * s)); d.line([a, b], fill=L["top"], width=int(152 * s))
    for p, r in ((a, 84), (b, 84)): d.ellipse([p[0] - r * s, p[1] - r * s, p[0] + r * s, p[1] + r * s], fill=PLUM)
    for p, r in ((a, 76), (b, 76)): d.ellipse([p[0] - r * s, p[1] - r * s, p[0] + r * s, p[1] + r * s], fill=L["top"])
    dt = tuple(int(v * 0.8) for v in L["top"])
    d.arc([b[0] - 62 * s, b[1] - 40 * s, b[0] + 62 * s, b[1] + 46 * s], 20, 160, fill=dt, width=int(12 * s))   # hood collar
    d.line([(a[0] - 40 * s, a[1] - 46 * s), (a[0] + 40 * s, a[1] - 46 * s)], fill=dt, width=int(7 * s))         # pocket seam
    if L["crack"]:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        _crack(d, [(mx - 40 * s, my - 70 * s), (mx - 10 * s, my - 30 * s), (mx - 28 * s, my + 5 * s), (mx + 12 * s, my + 40 * s), (mx + 2 * s, my + 80 * s)], s)
    # front leg
    limb((0, 0), kF, fF, 62, L["legs"]); shoe(fF)
    arms_back = pose.get("arms_back", 0) > 0.5
    if arms_back: limb(sh_, eF, hF, 50, L["top"])
    # head (bean)
    hd = math.radians(pose["lean"] + pose["head"])
    hc = (neck[0] + math.sin(hd) * 150 * facing, neck[1] - math.cos(hd) * 150)
    cx, cy = P(hc); rx, ry = 132 * s, 150 * s
    ex_ = cx - 118 * s * facing                                     # ear on the far side of the face
    d.ellipse([ex_ - 26 * s, cy - 8 * s, ex_ + 26 * s, cy + 46 * s], fill=L["skin"], outline=PLUM, width=int(7 * s))
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=L["skin"], outline=PLUM, width=int(9 * s))
    d.chord([cx - rx + 4 * s, cy - ry + 2 * s, cx + rx - 4 * s, cy + ry * 0.2], 190, 350, fill=L["hair"])
    tx = cx + 30 * s * facing                                       # hair tuft
    d.polygon([(tx - 40 * s, cy - ry + 20 * s), (tx + 10 * s * facing, cy - ry - 26 * s), (tx + 40 * s, cy - ry + 24 * s)], fill=L["hair"])
    shade = tuple(int(v * 0.93) for v in L["skin"])                 # soft cel shade on the back of the head
    d.chord([cx - rx + 9 * s, cy - ry + 9 * s, cx + rx - 9 * s, cy + ry - 9 * s], 100 if facing > 0 else -80, 170 if facing > 0 else 10, fill=shade)
    for k in (-1, 1):                                               # cheeks
        bx = cx + 26 * s * facing + k * 64 * s
        d.ellipse([bx - 20 * s, cy + 58 * s, bx + 20 * s, cy + 74 * s], fill=(236, 140, 130))
    nx_ = cx + 64 * s * facing                                      # nose
    d.arc([nx_ - 16 * s, cy + 24 * s, nx_ + 16 * s, cy + 56 * s], 300 if facing > 0 else 120, 60 if facing > 0 else 240, fill=PLUM, width=int(6 * s))
    if L["crack"]:
        _crack(d, [(cx - 70 * s * facing, cy + 40 * s), (cx - 92 * s * facing, cy + 70 * s), (cx - 80 * s * facing, cy + 100 * s)], s * 0.8)
    _face(d, cx, cy + 18 * s, s, facing, expr, L)
    # front arm + prop
    extras = {}
    if not arms_back: limb(sh_, eF, hF, 50, L["top"])
    hx, hy = P(hF)
    if prop == "phone":
        d.rounded_rectangle([hx - 22 * s, hy - 58 * s, hx + 22 * s, hy + 18 * s], 8 * s, fill=(30, 30, 36), outline=PLUM, width=int(5 * s))
        d.rectangle([hx - 15 * s, hy - 50 * s, hx + 15 * s, hy + 8 * s], fill=(150, 200, 255))
        extras["glow"] = (hx / 2, (hy - 20 * s) / 2)
    hand(hF)
    im = im.resize((Wc // 2, Hc // 2), Image.LANCZOS)
    extras["hand"] = (hx / 2, hy / 2); extras["head"] = (cx / 2, (cy - ry) / 2)
    return im, (Wc / 4, (Hc - 40 * s) / 2), extras

def place(frame_img, cam, P, pose, look, expr, facing, alpha=1.0, prop=None, shadow=True, height=1.75):
    """Project a character standing at world point P (feet). Returns screen info dict or None."""
    p = cam.proj(P)
    if not p: return None
    hpx = cam.F * height / p[2]
    if hpx < 12: return None
    if shadow:
        sh = Image.new("L", (int(hpx * 0.7), int(hpx * 0.12) + 2), 0)
        ImageDraw.Draw(sh).ellipse([0, 0, sh.width - 1, sh.height - 1], fill=int(90 * alpha))
        frame_img.paste((20, 14, 24), (int(p[0] - sh.width / 2), int(p[1] - sh.height / 2)), sh.filter(ImageFilter.GaussianBlur(hpx * 0.02)))
    im, (ax, ay), ex = card(pose, look, expr, facing, hpx, prop)
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im.putalpha(a)
    x0, y0 = int(p[0] - ax), int(p[1] - ay)
    frame_img.paste(im, (x0, y0), im)
    return dict(head=(x0 + ex["head"][0], y0 + ex["head"][1]), hand=(x0 + ex["hand"][0], y0 + ex["hand"][1]),
                glow=(x0 + ex["glow"][0], y0 + ex["glow"][1]) if "glow" in ex else None, hpx=hpx, feet=(p[0], p[1]))

# ---------------- bubbles & text ----------------
def spaced(d, xy, text, size, fill, sp=6, bold=False, stroke=None):
    f = font(size, bold); w = sum(d.textlength(c, font=f) for c in text) + sp * (len(text) - 1)
    x = xy[0] - w / 2
    if stroke is None: stroke = 0           # dark outline: readable on any background
    for c in text:
        d.text((x, xy[1]), c, font=f, fill=fill, anchor="lm", stroke_width=stroke, stroke_fill=(30, 22, 32)); x += d.textlength(c, font=f) + sp

def bubble(d, x, y, text, kind="speech", size=40, gold=False, tail=(0, 1)):
    f = font(size, bold=True); w = d.textlength(text, font=f) + 46; h = size + 34
    x = min(max(x, w / 2 + 30), W - w / 2 - 30)
    edge = (150, 110, 40) if gold else PLUM
    if kind == "thought":
        d.ellipse([x - w / 2 - 10, y - h / 2 - 6, x + w / 2 + 10, y + h / 2 + 6], fill=(252, 250, 245), outline=edge, width=5)
        for i, r in enumerate((12, 8)):
            cx, cy = x + tail[0] * (30 + i * 26) - 20, y + h / 2 + 18 + i * 22
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(252, 250, 245), outline=edge, width=4)
    else:
        d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 18, fill=(252, 250, 245), outline=edge, width=5)
        tx = x + tail[0] * w * 0.25
        d.polygon([(tx - 14, y + h / 2 - 3), (tx + 14, y + h / 2 - 3), (tx + tail[0] * 10, y + h / 2 + 24)], fill=(252, 250, 245))
        d.line([(tx - 14, y + h / 2), (tx + tail[0] * 10, y + h / 2 + 24), (tx + 14, y + h / 2)], fill=edge, width=5)
    d.text((x, y), text, font=f, fill=PLUM, anchor="mm")

def chrome(d, t, cta, payoff, service=False):
    spaced(d, (W / 2, 330), cta.upper(), 34, (255, 214, 150) if t >= payoff else (250, 250, 250), sp=5, bold=True)
    spaced(d, (W / 2, 1490), "MOTIVATION RECLAIMED", 26, (150, 150, 155), sp=8)

def finish(img):
    """light grain + gentle sharpen + soft vignette (survives platform compression)"""
    img = img * 1.35 - cv2.GaussianBlur(img, (0, 0), 1.3) * 0.35
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.28 * (((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H * 0.52) / (H * 0.62)) ** 2)
    img = img * vig[..., None] + np.random.default_rng(int(abs(img[::97, ::97]).sum()) % 9999).normal(0, 1.0, (H, W, 1))
    return np.clip(img, 0, 255).astype(np.uint8)

# ---------------- shared layout: scene panel on a black frame ----------------
TICK_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def on_black(panel, py, t, cta, payoff, top="", lines=(), line_alpha=1.0, gold_first=True, flash=True):
    """Paste the scene panel onto black; top band (counter) above it, 1-2 big lines below, CTA + watermark."""
    canvas = Image.new("RGB", (W, H), (0, 0, 0)); canvas.paste(panel, (0, py)); d = ImageDraw.Draw(canvas)
    if top: spaced(d, (W / 2, py - 34), top, 36, (255, 226, 170), sp=6, bold=True)
    y = py + panel.height + 52
    for i, ln in enumerate(lines):
        big = i == 0
        col = (255, 214, 150) if (big and gold_first) else (255, 255, 255)
        sz = 62 if big else 40
        while sz > 30 and sum(d.textlength(c, font=font(sz, True)) for c in ln) + (10 if big else 7) * len(ln) > W - 90: sz -= 2
        spaced(d, (W / 2, y), ln, sz, tuple(int(c * line_alpha) for c in col), sp=10 if big else 7, bold=True)
        y += 70 if big else 52
    chrome(d, t, cta, payoff)
    out = np.asarray(canvas).astype(np.float32)
    if flash and payoff <= t < payoff + 0.15: out[py:py + panel.height] += (1 - (t - payoff) / 0.15) * 80
    return finish(out)

def sparkles(d, cam, t, t0, center, n=28, spread=1.3):
    for i in range(n):
        u = (t - t0) * (0.5 + (i * 37 % 10) / 20) + i * 0.13
        q = cam.proj((center[0] + math.sin(i * 2.1) * spread, (u % 1.0) * 2.6, center[2] + math.cos(i * 1.7) * 0.8))
        if q: d.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=GOLD)

def halo(fr, x, y, r, k):
    g = Image.new("L", (int(r * 2), int(r * 2)), 0); ImageDraw.Draw(g).ellipse([r * 0.25, r * 0.25, r * 1.75, r * 1.75], fill=int(170 * k))
    fr.paste((255, 200, 110), (int(x - r), int(y - r)), g.filter(ImageFilter.GaussianBlur(r * 0.25)))

def book(d, x, y, sc, open_=True):
    w, h = 70 * sc, 50 * sc
    d.polygon([(x - w / 2, y - h / 2), (x, y - h / 2 + 6 * sc), (x, y + h / 2), (x - w / 2, y + h / 2 - 6 * sc)], fill=(250, 246, 236), outline=PLUM)
    d.polygon([(x, y - h / 2 + 6 * sc), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 - 6 * sc), (x, y + h / 2)], fill=(244, 238, 226), outline=PLUM)
    for k in range(3):
        yy = y - h / 4 + k * h / 5; d.line([(x - w / 2 + 8 * sc, yy), (x - 8 * sc, yy + 3 * sc)], fill=(180, 170, 160), width=2)
