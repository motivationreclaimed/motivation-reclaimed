"""Shared pieces of the 3D 'gold light' style (built on race.py's renderer)."""
import math, subprocess, os, types
import numpy as np, cv2
from PIL import Image, ImageDraw
from engine3d.race import (W, H, FPS, F, CX, CY, GOLD, Cam, ease, lerp, mix, joints, draw_figure, blob, tag, spaced,
                           finish, STAND, PHONE_STAND, SIT, ARMS_UP, pose_run, pose_phone_walk, font)
from engine import sfx

# better victory pose: arms up in a V (reads from every camera angle)
ARMS_V = dict(hip=0.97, lean=-4, thL=6, shL=6, thR=-8, shR=-8, uaL=150, faL=160, uaR=-150, faR=-160, head=-14)

def room(img, cam, warm=0.0):
    """dark studio: faint warm haze, square floor grid with fog, distant light strips"""
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    img[:] = (np.array([8, 8, 11], np.float32) + np.array([18, 14, 10], np.float32) * (1 + 2 * warm) * np.exp(-((yy - 0.40) / 0.13) ** 2))[:, None, :]
    cx, cz = int(cam.C[0]), int(cam.C[2])
    def seg(p, q, col, th=1):
        a, b = cam.proj(p), cam.proj(q)
        if a and b:
            fog = math.exp(-max(0, (a[2] + b[2]) / 2 - 5) / 14)
            cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), tuple(c * fog for c in col), th, cv2.LINE_AA)
    for x0 in range(cx - 14, cx + 26): seg((x0, 0, cz - 2), (x0, 0, cz + 26), (30, 31, 37))
    for z0 in range(cz - 2, cz + 26): seg((cx - 14, 0, z0), (cx + 26, 0, z0), (30, 31, 37))
    for x0 in range(cx - 14, cx + 26, 5):
        a, b = cam.proj((x0, 0.0, 18.0)), cam.proj((x0, 7.0, 18.0))
        if a and b: cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), (30, 28, 26), max(2, int(F * 0.14 / a[2])), cv2.LINE_AA)

def quad(img, cam, pts, col, edge=None, emis=None, ecol=None):
    q = [cam.proj(p) for p in pts]
    if not all(q): return
    fog = math.exp(-max(0, sum(a[2] for a in q) / 4 - 6) / 16)
    poly = np.array([(int(a[0]), int(a[1])) for a in q], np.int32)
    cv2.fillConvexPoly(img, poly, tuple(c * fog for c in col), cv2.LINE_AA)
    if edge is not None: cv2.polylines(img, [poly], True, tuple(c * fog for c in edge), 2, cv2.LINE_AA)
    if emis is not None: cv2.polylines(emis, [poly], True, ecol, 6, cv2.LINE_AA)

def box(img, cam, x0, x1, y0, y1, z0, z1, top, front, side, edge=None, emis=None, ecol=None):
    """axis-aligned box seen from -z / -x side: draw side (z0), front (x0) and top faces"""
    quad(img, cam, [(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], front, edge)
    quad(img, cam, [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], side, edge)
    quad(img, cam, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], top, edge, emis, ecol)

def barbell(img, emis, cam, J, gold=False, alpha=1.0):
    c = (J["hL"] + J["hR"]) / 2
    a, b = c + np.array([0, 0, 0.95], np.float32), c - np.array([0, 0, 0.95], np.float32)
    pa, pb = cam.proj(a), cam.proj(b)
    if not (pa and pb): return
    col = (230, 190, 120) if gold else (120, 122, 132)
    cv2.line(img, (int(pa[0]), int(pa[1])), (int(pb[0]), int(pb[1])), tuple(v * alpha for v in col), max(2, int(F * 0.025 / pa[2])), cv2.LINE_AA)
    for e in (0.72, 0.82, -0.72, -0.82):
        p = cam.proj(c + np.array([0, 0, e], np.float32))
        if p:
            r = int(F * 0.22 / p[2])
            cv2.ellipse(img, (int(p[0]), int(p[1])), (max(2, r // 3), r), 0, 0, 360, tuple(v * 0.45 * alpha for v in col), -1, cv2.LINE_AA)
            cv2.ellipse(img, (int(p[0]), int(p[1])), (max(2, r // 3), r), 0, 0, 360, tuple(v * alpha for v in col), 2, cv2.LINE_AA)
            if gold: cv2.ellipse(emis, (int(p[0]), int(p[1])), (max(2, r // 3), r), 0, 0, 360, (255, 170, 60), 4, cv2.LINE_AA)

def aura(emis, cam, J, glow, base=0.12):
    p = cam.proj(J["neck"] * 0.5 + J["hip"] * 0.5)
    if p and p[2] > 0.5:
        s = F / p[2]
        blob(emis, p[0], p[1], 0.5 * s * (1 + 0.8 * glow), 0.85 * s * (1 + 0.6 * glow), GOLD, base + 0.3 * glow)

def floor_light(img, cam, P, glow, k=0.12):
    p = cam.proj(P)
    if p and p[2] > 0.5:
        s = F / p[2]
        blob(img, p[0], p[1], 1.3 * s * (1 + glow), 0.33 * s * (1 + glow), GOLD * (k + 0.25 * glow))

def sparks(emis, cam, t, t0, center, n=70):
    rng = np.random.default_rng(3)
    for i in range(n):
        ph = (t - t0) * (0.4 + rng.random() * 0.5) + rng.random()
        P = np.array([center[0] + (rng.random() - 0.5) * 3, center[1] + (ph % 1.0) * 3.2, center[2] + (rng.random() - 0.5) * 2], np.float32)
        q = cam.proj(P)
        if q: cv2.circle(emis, (int(q[0]), int(q[1])), max(1, int(F * 0.012 / q[2])), (255, 190, 90), -1, cv2.LINE_AA)

def compose(img, emis):
    small = cv2.resize(emis, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    bloom = cv2.resize(cv2.GaussianBlur(small, (0, 0), 5) * 0.9 + cv2.GaussianBlur(small, (0, 0), 16) * 0.7, (W, H))
    return img + emis * 0.35 + bloom

def chrome(d, t, cta, payoff, service=False):
    spaced(d, (W / 2, 335), cta.upper(), 30, (255, 205, 130) if t >= payoff else (205, 205, 210), sp=5)
    d.line([(W / 2 - 300, 370), (W / 2 + 300, 370)], fill=(60, 60, 66), width=1)
    if service and t >= payoff + 0.8:   # quiet credit line, only at the very end
        spaced(d, (W / 2, 1440), "ANIMATIONS FOR BRANDS · MR@PIXEVON.COM", 22, (150, 130, 95), sp=5)
    else:
        spaced(d, (W / 2, 1440), "MOTIVATION RECLAIMED", 22, (90, 90, 96), sp=6)

def render(out, frame_fn, dur, payoff, sounds, blur=None):
    """frame_fn(t, sub) -> (float img, overlay_fn(PIL draw))"""
    tmpv = out + ".v.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-crf", "18", "-maxrate", "10M", "-bufsize", "20M", "-preset", "medium", "-tune", "film",
                           "-pix_fmt", "yuv420p", tmpv], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        t = i / FPS
        if blur and blur[0] <= t < blur[1]:
            outs = [frame_fn(t, sub) for sub in (-0.011, 0.0, 0.011)]
            img, ov = sum(o[0] for o in outs) / 3, outs[1][1]
        else:
            img, ov = frame_fn(t, 0.0)
        if payoff <= t < payoff + 0.15: img = img + (1 - (t - payoff) / 0.15) * 90
        im = Image.fromarray(finish(img).astype(np.uint8)); ov(ImageDraw.Draw(im))
        ff.stdin.write(np.asarray(im).tobytes())
    ff.stdin.close(); ff.wait()
    wav = out + ".wav"; sfx.build(types.SimpleNamespace(DURATION=dur, PAYOFF=payoff, SOUNDS=sounds), wav)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmpv, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(tmpv); os.remove(wav)

def stills(prefix, frame_fn, ts):
    ims = []
    for t in ts:
        img, ov = frame_fn(t, 0.0)
        im = Image.fromarray(finish(img).astype(np.uint8)); ov(ImageDraw.Draw(im)); ims.append(im.resize((432, 768)))
    sheet = Image.new("RGB", (432 * len(ims), 768))
    for i, im in enumerate(ims): sheet.paste(im, (i * 432, 0))
    sheet.save(prefix + "_sheet.png")
