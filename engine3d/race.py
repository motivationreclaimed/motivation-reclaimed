"""3D 'gold light' style — sample: PHONE vs DISCIPLINE race (10 s).
Small software 3D renderer (numpy + cv2): perspective camera, capsule figures, reflective floor, fog,
the hero emits gold light from his cracks (bloom), speed-up section with motion blur.
Run: python3 engine3d/race.py out.mp4
"""
import math, subprocess, sys, os, types
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine import sfx

W, H, FPS, DUR = 1080, 1920, 30, 10.0
F = 1350.0                        # focal length (px)
CX, CY = W / 2, 980               # principal point
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
GOLD = np.array([255, 190, 90], np.float32)
TOON = False                      # draw cartoon characters instead of the mannequins
FIN = 37.0                        # finish line x (m)
HERO_Z, GREY_Z = 0.0, 1.9         # lanes

def font(sz): return ImageFont.truetype(SERIF, sz)
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u

# ---------- time: normal, then x4 speed-up (time passing), then normal ----------
def scene_time(t):
    if t < 3.5: return t
    if t < 5.5: return 3.5 + 4 * (t - 3.5)
    return 11.5 + (t - 5.5)

def hero_x(s):
    if s < 1.2: return 0.0
    x = 3.0 * (s - 1.2)
    if x > FIN - 1.0:                                  # ease into the stop just past the line
        over = x - (FIN - 1.0); x = FIN - 1.0 + 1.6 * (1 - math.exp(-over / 1.6))
    return x
def hero_running(s): return 1.2 <= s and 3.0 * (s - 1.2) < FIN + 0.2
def grey_x(s): return 0.0 if s < 1.2 else 0.8 * (min(s, 8.0) - 1.2)

# ---------- camera ----------
class Cam:
    def __init__(self, pos, tgt):
        self.C = np.array(pos, np.float32); f = np.array(tgt, np.float32) - self.C
        self.f = f / np.linalg.norm(f); up = np.array([0, 1, 0], np.float32)
        r = np.cross(up, self.f); self.r = r / np.linalg.norm(r); self.u = np.cross(self.f, self.r)
    def depth(self, P): return float((np.asarray(P, np.float32) - self.C) @ self.f)
    def proj(self, P):
        d = np.asarray(P, np.float32) - self.C
        z = float(d @ self.f)
        if z < 0.2: return None
        return (CX + F * float(d @ self.r) / z, CY - F * float(d @ self.u) / z, z)

def follow(X):
    return (X - 4.4, 2.0, -3.1), (X + 3.0, 0.95, 1.0)

def camera(t, hx, gx):
    if t < 1.2:                                   # slow push-in at the start line
        k = ease(t / 1.2); (c, g) = follow(-0.5)
        return Cam((c[0] - 2 * (1 - k), c[1] + 0.6 * (1 - k), c[2] - 1.5 * (1 - k)), g)
    if t < 5.5:                                   # stay with the one falling behind; the light runs away from us
        return Cam(*follow(gx - 0.3))
    if t < 7.3:                                   # cut straight to him (no empty frames)
        return Cam(*follow(hx - 2.5))
    k = ease((t - 7.3) / 2.7)                     # payoff: slow orbit around him
    a = lerp(-1.17, -0.25, k); R = lerp(7.8, 5.0, k)
    return Cam((hx + R * math.sin(a), lerp(2.0, 1.3, k), -R * math.cos(a)),
               (lerp(hx + 0.5, hx, k), lerp(0.9, 1.15, k), lerp(1.0, 0.0, k)))

# ---------- skeleton (side plane, facing +x) ----------
SEG = dict(thigh=0.47, shin=0.47, torso=0.56, neck=0.1, ua=0.3, fa=0.28)
def pose_run(p):
    s = math.sin(p)
    return dict(hip=0.93 + 0.05 * abs(math.cos(p)), lean=14, thL=38 * s, shL=38 * s - 55 * (0.5 + 0.5 * math.cos(p)),
                thR=-38 * s, shR=-38 * s - 55 * (0.5 - 0.5 * math.cos(p)), uaL=-45 * s, faL=-45 * s + 80,
                uaR=45 * s, faR=45 * s + 80, head=8)
def pose_phone_walk(p):
    s = math.sin(p)
    return dict(hip=0.95 + 0.015 * abs(math.cos(p)), lean=8, thL=18 * s, shL=18 * s - 15 * (0.5 + 0.5 * math.cos(p)),
                thR=-18 * s, shR=-18 * s - 15 * (0.5 - 0.5 * math.cos(p)), uaL=12, faL=105, uaR=18, faR=110, head=38)
STAND = dict(hip=0.95, lean=2, thL=3, shL=3, thR=-3, shR=-3, uaL=-6, faL=-4, uaR=6, faR=8, head=0)
PHONE_STAND = dict(STAND, uaL=12, faL=105, uaR=18, faR=110, head=38, lean=6)
SIT = dict(hip=0.42, lean=34, thL=88, shL=8, thR=82, shR=4, uaL=40, faL=110, uaR=46, faR=115, head=45)
ARMS_UP = dict(hip=0.97, lean=-4, thL=6, shL=6, thR=-8, shR=-8, uaL=168, faL=172, uaR=-168, faR=-172, head=-12)
def mix(a, b, k): return {key: lerp(a[key], b[key], k) for key in a}

def joints(x, z, P, facing=1):
    """3D joints. Angles in degrees from straight down, positive = forward (+x)."""
    def v(a, L): a = math.radians(a); return np.array([math.sin(a) * facing * L, -math.cos(a) * L, 0], np.float32)
    hip = np.array([x, P["hip"], z], np.float32)
    lean = math.radians(P["lean"])
    neck = hip + np.array([math.sin(lean) * facing, math.cos(lean), 0], np.float32) * SEG["torso"]
    hd = math.radians(P["lean"] + P["head"])
    head = neck + np.array([math.sin(hd) * facing, math.cos(hd), 0], np.float32) * (SEG["neck"] + 0.13)
    J = dict(hip=hip, neck=neck, head=head)
    for side, dz in (("L", 0.11), ("R", -0.11)):   # L = far side (+z), R = near side
        o = np.array([0, 0, dz], np.float32)
        k = hip + o + v(P["th" + side], SEG["thigh"]); f = k + v(P["sh" + side], SEG["shin"])
        sh = neck + o * 1.5 - np.array([0, 0.04, 0], np.float32)
        e = sh + v(P["ua" + side], SEG["ua"]); h = e + v(P["fa" + side], SEG["fa"])
        J.update({"k" + side: k, "f" + side: f, "sh" + side: sh, "e" + side: e, "h" + side: h, "hp" + side: hip + o})
    return J

BONES = [("hpL", "kL", .062), ("kL", "fL", .052), ("shL", "eL", .05), ("eL", "hL", .045),
         ("hip", "neck", .115), ("hpR", "kR", .062), ("kR", "fR", .052), ("shR", "eR", .05), ("eR", "hR", .045)]

# ---------- drawing ----------
def draw_figure(img, emis, cam, J, hero=False, warm=0.0, alpha=1.0, mirror=False):
    def pr(p):
        if mirror: p = p * np.array([1, -1, 1], np.float32)
        return cam.proj(p)
    if hero: dark, light = np.array([150, 140, 125]), np.array([238, 230, 214])
    else:
        dark = np.array([34, 36, 42]) + warm * np.array([60, 38, 10]); light = np.array([92, 96, 106]) + warm * np.array([120, 80, 25])
    for a, b, r in BONES + [("head", "head", .14)]:
        pa, pb = pr(J[a]), pr(J[b])
        if pa is None or pb is None: continue
        w = max(2, int(2 * F * r / ((pa[2] + pb[2]) / 2)))
        A, B = (int(pa[0]), int(pa[1])), (int(pb[0]), int(pb[1]))
        col_d = tuple(float(c) * alpha for c in dark); col_l = tuple(float(c) * alpha for c in light)
        if a == "head":
            cv2.circle(img, A, w // 2, col_d, -1, cv2.LINE_AA)
            cv2.circle(img, (A[0] - w // 10, A[1] - w // 10), int(w * 0.38), col_l, -1, cv2.LINE_AA)
        else:
            cv2.line(img, A, B, col_d, w, cv2.LINE_AA)
            off = max(1, w // 8)
            cv2.line(img, (A[0] - off, A[1] - off), (B[0] - off, B[1] - off), col_l, max(1, int(w * 0.55)), cv2.LINE_AA)
    if hero and not mirror:                         # glowing kintsugi cracks
        rng = np.random.default_rng(7)
        for a, b, r in BONES + [("neck", "head", 0.1)]:
            pa, pb = pr(J[a]), pr(J[b])
            if pa is None or pb is None: continue
            pts = []
            for i in range(6):
                u = i / 5; x = lerp(pa[0], pb[0], u); y = lerp(pa[1], pb[1], u)
                dx, dy = pb[1] - pa[1], pa[0] - pb[0]; n = math.hypot(dx, dy) + 1e-6
                j = (rng.random() - 0.5) * 0.35 * F * r / pa[2]
                pts.append((int(x + dx / n * j), int(y + dy / n * j)))
            pts = np.array(pts, np.int32)
            th = max(2, int(F * 0.012 / pa[2]))
            cv2.polylines(img, [pts], False, (255, 214, 140), th, cv2.LINE_AA)
            cv2.polylines(emis, [pts], False, (255, 175, 70), th * 2, cv2.LINE_AA)

def blob(img, x, y, rx, ry, col, k=1.0):
    """additive soft light ellipse"""
    x0, x1, y0, y1 = int(max(0, x - rx * 2)), int(min(W, x + rx * 2)), int(max(0, y - ry * 2)), int(min(H, y + ry * 2))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    g = np.exp(-(((xx - x) / rx) ** 2 + ((yy - y) / ry) ** 2)) * k
    img[y0:y1, x0:x1] += g[..., None] * np.asarray(col, np.float32)

def draw_floor(img, emis, cam, hx, glow):
    # background: deep charcoal with a faint warm horizon haze
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    img[:] = (np.array([8, 8, 11], np.float32) + np.array([18, 14, 10], np.float32) * np.exp(-((yy - 0.42) / 0.12) ** 2))[:, None, :]
    xs = np.arange(math.floor(cam.C[0]) - 14, math.floor(cam.C[0]) + 40)
    def seg(p, q, col, th):
        a, b = cam.proj(p), cam.proj(q)
        if a and b:
            fog = math.exp(-max(0, (a[2] + b[2]) / 2 - 5) / 14)
            cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), tuple(c * fog for c in col), th, cv2.LINE_AA)
    for x0 in xs[::6]:                                           # distant light strips (depth)
        a, b = cam.proj((x0, 0.0, 16.0)), cam.proj((x0, 6.0, 16.0))
        if a and b: cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), (30, 28, 26), max(2, int(F * 0.12 / a[2])), cv2.LINE_AA)
    for x0 in xs:                                                # lane surfaces (subtle bands)
        for z0, z1, col in ((-1.0, 0.95, (17, 17, 21)), (0.95, 2.9, (14, 14, 18))):
            q = [cam.proj((x0, 0, z0)), cam.proj((x0 + 1, 0, z0)), cam.proj((x0 + 1, 0, z1)), cam.proj((x0, 0, z1))]
            if all(q):
                fog = math.exp(-max(0, q[0][2] - 5) / 16)
                cv2.fillConvexPoly(img, np.array([(int(a[0]), int(a[1])) for a in q], np.int32), tuple(c * fog for c in col), cv2.LINE_AA)
    for z in (-1.0, 0.95, 2.9):                                   # lane edges
        for x0 in xs: seg((x0, 0, z), (x0 + 1, 0, z), (95, 97, 108), 2)
    for x0 in xs:                                                # cross grid
        seg((x0, 0, -1.0), (x0, 0, 2.9), (34, 35, 41), 1)
    a, b = cam.proj((FIN, 0, -1.0)), cam.proj((FIN, 0, 2.9))      # gold finish line
    if a and b:
        cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), (255, 200, 110), 4, cv2.LINE_AA)
        cv2.line(emis, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), (255, 170, 60), 14, cv2.LINE_AA)
    # the hero's light pool on the floor
    p = cam.proj((hx, 0, HERO_Z))
    if p:
        s = F / p[2]
        blob(img, p[0], p[1], 1.4 * s * (1 + glow), 0.35 * s * (1 + glow), GOLD * (0.10 + 0.25 * glow))

def tag(d, x, y, text, gold=False):
    f = font(30); w = d.textlength(text, font=f) + 34
    col = (255, 205, 130) if gold else (190, 192, 200)
    x = min(max(x, w / 2 + 40), W - w / 2 - 40)          # always fully on screen
    d.rounded_rectangle([x - w / 2, y - 26, x + w / 2, y + 26], 8, fill=(14, 14, 16), outline=col, width=2)
    d.text((x, y), text, font=f, fill=col, anchor="mm")

def spaced(d, xy, text, size, fill, sp=6, anchor="mm"):
    f = font(size); w = sum(d.textlength(c, font=f) for c in text) + sp * (len(text) - 1)
    x = xy[0] - w / 2 if anchor == "mm" else xy[0]
    for c in text:
        d.text((x, xy[1]), c, font=f, fill=fill, anchor="lm"); x += d.textlength(c, font=f) + sp

# ---------- one frame ----------
def frame(t, sub=0.0):
    s = scene_time(t + sub)
    hx, gx = hero_x(s), grey_x(s)
    glow = ease((t - 7.6) / 0.6) if t > 7.6 else 0.0
    cam = camera(t, hx, gx)
    img = np.zeros((H, W, 3), np.float32); emis = np.zeros_like(img); refl = np.zeros_like(img)
    draw_floor(img, emis, cam, hx, glow)
    # poses
    if s < 1.2: hp = STAND
    elif hero_running(s): hp = pose_run(s * 10.5)
    else: hp = mix(STAND, ARMS_UP, ease((t - 7.65) / 0.5)) if t > 7.6 else STAND
    if s < 1.2: gp = PHONE_STAND
    elif s < 8.0: gp = pose_phone_walk(s * 6.0)
    else: gp = mix(PHONE_STAND, SIT, ease((s - 8.0) / 0.8))
    JH, JG = joints(hx, HERO_Z, hp), joints(gx, GREY_Z, gp)
    warm = 0.25 + 0.75 * glow if abs(gx - hx) < 6 else 0.1 * glow
    if TOON:                                            # cartoon characters in the dark world
        from engine3d import toon as T
        from engine3d.r3d import draw_toon
        if s < 1.2: th = T.STAND
        elif hero_running(s): th = T.run(s * 10.5)
        else: th = T.ARMS_UP if t > 7.7 else T.STAND
        if s < 1.2: tg = T.PHONE
        elif s < 8.0: tg = dict(T.walk(s * 6.0, 18), uaF=40, faF=120, uaB=30, faB=110, head=22)
        else: tg = T.SIT_SAD
        for who in sorted(("g", "h"), key=lambda q: -cam.depth(np.array([hx if q == "h" else gx, 1, HERO_Z if q == "h" else GREY_Z], np.float32)) if hasattr(cam, "depth") else 0):
            if who == "g": draw_toon(img, emis, cam, np.array([gx, 0, GREY_Z], np.float32), tg, "grey", "tired" if s > 4 else "neutral", 1, prop="phone", bright=0.85)
            else: draw_toon(img, emis, cam, np.array([hx, 0, HERO_Z], np.float32), th, "hero", "happy" if t > 7.6 else "determined", 1, glow=glow)
    else:
        # reflections (mirrored, blurred, faint)
        draw_figure(refl, emis, cam, JG, warm=warm, mirror=True); draw_figure(refl, emis, cam, JH, hero=True, mirror=True)
        img += cv2.GaussianBlur(refl, (0, 0), 6) * 0.22
        for J, hero in sorted([(JG, False), (JH, True)], key=lambda q: -float((q[0]["hip"] - cam.C) @ cam.f)):
            draw_figure(img, emis, cam, J, hero=hero, warm=warm)
            if not hero:                                   # phone screen glow
                p = cam.proj((J["hL"] + J["hR"]) / 2)
                if p and s < 9.5:
                    cv2.rectangle(img, (int(p[0]) - 5, int(p[1]) - 8), (int(p[0]) + 5, int(p[1]) + 8), (170, 200, 255), -1)
                    blob(emis, p[0], p[1] - 10, 30, 30, (60, 110, 255), 0.9)
        # hero aura
        p = cam.proj(JH["neck"] * 0.5 + JH["hip"] * 0.5)
        if p and p[2] > 0.5:
            s_ = F / p[2]
            blob(emis, p[0], p[1], 0.5 * s_ * (1 + 0.8 * glow), 0.85 * s_ * (1 + 0.6 * glow), GOLD, 0.12 + 0.3 * glow)
    if glow > 0:   # payoff: gold sparks rising
        rng = np.random.default_rng(3)
        for i in range(70):
            ph = (t - 7.6) * (0.4 + rng.random() * 0.5) + rng.random()
            P = np.array([hx + (rng.random() - 0.5) * 3, (ph % 1.0) * 3.2, HERO_Z + (rng.random() - 0.5) * 2], np.float32)
            q = cam.proj(P)
            if q: cv2.circle(emis, (int(q[0]), int(q[1])), max(1, int(F * 0.012 / q[2])), (255, 190, 90), -1, cv2.LINE_AA)
    # bloom
    small = cv2.resize(emis, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    bloom = cv2.resize(cv2.GaussianBlur(small, (0, 0), 5) * 0.9 + cv2.GaussianBlur(small, (0, 0), 16) * 0.7, (W, H))
    img += emis * 0.35 + bloom
    return img, cam, JH, JG, s, hx

def overlay(img8, t, cam, JH, JG, s, hx):
    im = Image.fromarray(img8); overlay_draw(ImageDraw.Draw(im), t, cam, JH, JG, s, hx)
    return np.asarray(im)

def overlay_draw(d, t, cam, JH, JG, s, hx):
    # labels floating above heads
    for J, name, gold in ((JG, "PHONE", False), (JH, "DISCIPLINE", True)):
        p = cam.proj(J["head"] + np.array([0, 0.42, 0], np.float32))
        if p and 0 < p[0] < W and t < 9.6:
            spaced(d, (p[0], p[1]), name, min(44, max(22, int(F * 0.11 / p[2]))), (255, 205, 130) if gold else (150, 152, 162), sp=4)
    # speech tags (like comments popping up)
    for t0, t1, J, text, gold in ((1.9, 3.3, JG, "after this video.", False), (2.5, 3.5, JH, "let's go.", True),
                                  (6.0, 7.2, JG, "maybe tomorrow.", False)):
        if t0 <= t < t1:
            p = cam.proj(J["head"] + np.array([0, 0.85, 0], np.float32))
            if p: tag(d, p[0], p[1], text, gold)
    # hook line, speed-up counter
    if t < 1.5:
        a = int(255 * min(1, (1.5 - t) / 0.3))
        spaced(d, (W / 2, 520), "SAME 24 HOURS.", 54, (a, a, a), sp=8)
    if 3.5 <= t < 5.7:
        day = 1 + int(89 * min(1, (t - 3.5) / 2.0))
        spaced(d, (W / 2, 520), f"DAY {day}", 84, (240, 240, 244), sp=10)
        spaced(d, (W / 2, 590), "× 4", 30, (150, 150, 160), sp=6)
    if t >= 7.7:
        a = ease((t - 7.7) / 0.5)
        spaced(d, (W / 2, 520), "DAY 90", 84, tuple(int(c * a) for c in (255, 205, 130)), sp=10)
    # CTA band (brand rule) + watermark
    spaced(d, (W / 2, 335), "WHICH LANE ARE YOU IN? COMMENT BELOW.", 30, (255, 205, 130) if t >= 7.6 else (205, 205, 210), sp=5)
    d.line([(W / 2 - 300, 370), (W / 2 + 300, 370)], fill=(60, 60, 66), width=1)
    spaced(d, (W / 2, 1440), "MOTIVATION RECLAIMED", 22, (90, 90, 96), sp=6)

def finish(img):
    # light grain only: heavy grain is smeared into blotches by Instagram/TikTok/YouTube re-compression
    g = np.random.default_rng(int(img.sum()) % 99999).normal(0, 1.1, (H, W, 1)).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.45 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.55) / (H * 0.6)) ** 2)
    img = 255 * (1 - np.exp(-np.maximum(img, 0) / 210))   # filmic: no blown-out whites
    img = img * 1.4 - cv2.GaussianBlur(img, (0, 0), 1.3) * 0.4         # gentle sharpening: survives platform compression
    return np.clip((img + g) * vig[..., None], 0, 255)

def main(out):
    yy, xx = None, None
    tmpv = out + ".video.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-crf", "16", "-maxrate", "16M", "-bufsize", "32M", "-preset", "medium", "-tune", "film",
                           "-pix_fmt", "yuv420p", tmpv], stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    for i in range(n):
        t = i / FPS
        if 3.5 <= t < 5.5:                       # speed-up: motion blur from 3 sub-frames
            acc = None
            for sub in (-0.011, 0.0, 0.011):
                im, cam, JH, JG, s, hx = frame(t, sub)
                acc = im if acc is None else acc + im
            img = acc / 3
        else:
            img, cam, JH, JG, s, hx = frame(t)
        if t >= 7.6 and t < 7.75: img = img + (1 - (t - 7.6) / 0.15) * 90        # payoff flash
        img8 = finish(img).astype(np.uint8)
        ff.stdin.write(overlay(img8, t, cam, JH, JG, s, hx).tobytes())
    ff.stdin.close(); ff.wait()
    steps = [(1.2 + k * 0.33, "step", 0.3) for k in range(7)] + [(5.5 + k * 0.33, "step", 0.3) for k in range(6)]
    spec = types.SimpleNamespace(DURATION=DUR, PAYOFF=7.6, SOUNDS=[(0.6, "tick", 0.4), (0.9, "tick", 0.4), (1.2, "hit", 0.5),
                                 (3.4, "whoosh", 0.6), (3.7, "tick", 0.3), (4.1, "tick", 0.3), (4.5, "tick", 0.3), (4.9, "tick", 0.3),
                                 (5.3, "tick", 0.3), (5.5, "whoosh", 0.4), (6.0, "thud", 0.3)] + steps)
    wav = out + ".wav"; sfx.build(spec, wav)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmpv, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(tmpv); os.remove(wav)

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--stills":
        for t in map(float, sys.argv[3:]):
            img, cam, JH, JG, s, hx = frame(t)
            Image.fromarray(overlay(finish(img).astype(np.uint8), t, cam, JH, JG, s, hx)).resize((540, 960)).save(f"{sys.argv[1]}_{t:.1f}.png")
    else:
        main(sys.argv[1])
