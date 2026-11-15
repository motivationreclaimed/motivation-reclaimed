"""Build compilation videos from finished shorts.

  python3 compile.py wide  "8 Lessons on Discipline" out.mp4 videos/002_the_hill.mp4 videos/003_the_crack.mp4 ...
  python3 compile.py tall  "20 Lessons on Discipline" out.mp4 videos/....mp4 ...

wide = 1920x1080 YouTube long-form: clip centred, animated lesson title card on the left,
       progress + service CTA on the right, intro + outro cards, chapters file written next to out.
tall = 1080x1920 (~3 min TikTok/Reels/Shorts): clips back to back with a short animated
       lesson card between them, service CTA on the outro.
Lesson titles come from each clip's spec (specs/<same name>.py): TITLE if set, else the slug;
the takeaway line is the first line of its CAPTION.
"""
import os, sys, math, subprocess, tempfile, wave, importlib.util
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FPS = 30
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
GOLD = (214, 170, 72); INK = (236, 228, 210); DIM = (110, 106, 98)
SERVICE = "WANT ANIMATIONS LIKE THESE?"
EMAIL = "MR@PIXEVON.COM"
SR = 44100

def F(size, italic=False): return ImageFont.truetype(SERIF_I if italic else SERIF, size)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(u): u = clamp(u); return 1 - (1 - u) ** 3

def tracked(d, x, y, text, font, fill, tr=0, anchor="l"):
    w = sum(font.getlength(c) for c in text) + tr * (len(text) - 1)
    if anchor == "c": x -= w / 2
    elif anchor == "r": x -= w
    for c in text:
        d.text((x, y), c, font=font, fill=fill); x += font.getlength(c) + tr
    return w

def wrap(text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) > width and cur: lines.append(cur); cur = w
        else: cur = t
    if cur: lines.append(cur)
    return lines

def meta(clip):
    name = os.path.splitext(os.path.basename(clip))[0]
    spec = os.path.join(os.path.dirname(os.path.abspath(__file__)), "specs", name + ".py")
    title, take = name.split("_", 1)[-1].replace("_", " ").upper(), ""
    if os.path.exists(spec):
        src = open(spec).read()
        ns = {}
        try:
            s = importlib.util.spec_from_file_location("m", spec); m = importlib.util.module_from_spec(s)
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); s.loader.exec_module(m)
            title = getattr(m, "TITLE", title).upper()
            cap = getattr(m, "CAPTION", "")
            take = cap.strip().split("\n")[0] if cap else ""
        except Exception:
            pass
    # strip emojis / hashtags from the takeaway
    take = "".join(ch for ch in take if ord(ch) < 0x2000).split("#")[0].strip()
    return title, take

def duration(clip):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", clip],
                         capture_output=True, text=True).stdout
    return float(out.strip())

def frames(clip, w=1080, h=1920):
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", clip, "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{w}x{h}", "-r", str(FPS), "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)
    p.wait()

def audio(clip, secs):
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", clip, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                       capture_output=True)
    a = np.frombuffer(p.stdout, np.int16).reshape(-1, 2).astype(np.float32) / 32767
    n = int(secs * SR)
    return a[:n] if len(a) >= n else np.vstack([a, np.zeros((n - len(a), 2), np.float32)])

def whoosh(secs=0.6, g=0.25):
    n = int(secs * SR); t = np.arange(n) / SR
    x = np.random.default_rng(3).normal(0, 1, n).astype(np.float32)
    k = np.ones(60) / 60; x = np.convolve(x, k, "same")
    return (x * np.sin(np.pi * t / secs) ** 2 * g)[:, None].repeat(2, 1)

def grain(h, w, seed):
    return np.random.default_rng(seed).normal(0, 4, (h, w, 1)).astype(np.float32)

# --------------------------------------------------------------------------- WIDE
def build_wide(title, out, clips):
    W, H = 1920, 1080
    INTRO, OUTRO, CARD = 3.0, 4.5, 1.2        # seconds
    crop_t, crop_b, crop_l, crop_r = 250, 1450, 30, 1050   # vertical clips' content area (safe zone)
    ch = 980; cw = int((crop_r - crop_l) * ch / (crop_b - crop_t))
    cx0, cy0 = (W - cw) // 2, (H - ch) // 2
    tmp = tempfile.mkdtemp()
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                            "-maxrate", "1600k", "-bufsize", "3200k", "-pix_fmt", "yuv420p", f"{tmp}/v.mp4"],
                           stdin=subprocess.PIPE)
    G = [grain(H, W, s) for s in range(4)]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vign = np.clip(1.2 - (((xx - W/2)/(W*0.7))**2 + ((yy - H/2)/(H*0.7))**2) * 0.8, 0.35, 1)[..., None]
    fi = 0
    def emit(img):
        nonlocal fi
        a = np.asarray(img, np.float32) * vign + G[fi % 4]
        enc.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes()); fi += 1

    def base_layer():
        im = Image.new("RGB", (W, H), (6, 6, 8)); d = ImageDraw.Draw(im)
        tracked(d, W - 70, 60, "MOTIVATION", F(22), DIM, tr=8, anchor="r")
        tracked(d, W - 70, 90, "RECLAIMED", F(22), DIM, tr=8, anchor="r")
        return im

    metas = [meta(c) for c in clips]
    chapters, tcur = [("00:00", "Intro")], INTRO
    audio_parts = [np.zeros((int(INTRO * SR), 2), np.float32)]
    audio_parts[0][:int(0.6*SR)] += whoosh(0.6, 0.2)

    # intro
    for k in range(int(INTRO * FPS)):
        t = k / FPS; im = base_layer(); d = ImageDraw.Draw(im)
        a = ease(t / 0.8); col = tuple(int(c * a) for c in INK)
        f = F(84)
        for i, ln in enumerate(wrap(title.upper(), f, 1400)):
            tracked(d, W / 2, 400 + i * 100 - (1 - a) * 30, ln, f, col, tr=10, anchor="c")
        lw = 380 * ease((t - 0.4) / 0.9)
        d.line([(W/2 - lw, 640), (W/2 + lw, 640)], fill=GOLD, width=3)
        tracked(d, W / 2, 680, "MOTIVATION RECLAIMED", F(30), tuple(int(c * ease((t-0.8)/0.8)) for c in GOLD), tr=12, anchor="c")
        emit(im)

    n = len(clips)
    for i, (clip, (ttl, take)) in enumerate(zip(clips, metas)):
        dur = duration(clip)
        mm, ss = divmod(int(tcur), 60); chapters.append((f"{mm:02d}:{ss:02d}", f"Lesson {i+1}: {ttl.title()}"))
        seg = CARD + dur; tcur += seg
        audio_parts.append(np.vstack([whoosh(CARD, 0.18), audio(clip, dur)]))
        # static side panels for this lesson
        side = base_layer(); d = ImageDraw.Draw(side)
        tracked(d, W - 70, H - 160, "WANT ANIMATIONS", F(22), DIM, tr=4, anchor="r")
        tracked(d, W - 70, H - 130, "LIKE THESE?", F(22), DIM, tr=4, anchor="r")
        tracked(d, W - 70, H - 92, EMAIL, F(24), GOLD, tr=4, anchor="r")
        for j in range(n):
            y = 300 + j * min(46, 480 / max(1, n))
            on = j <= i
            d.ellipse([W - 92, y, W - 80, y + 12], fill=GOLD if j == i else ((150, 140, 120) if on else (45, 45, 50)))
        tracked(d, W - 110, 296 + i * min(46, 480 / max(1, n)) - 4, f"{i+1:02d}", F(22), GOLD, tr=3, anchor="r")
        gen = frames(clip)
        last = None
        for k in range(int(seg * FPS)):
            t = k / FPS
            im = side.copy(); d = ImageDraw.Draw(im)
            # left lesson card (animated in)
            a = ease((t - 0.1) / 0.7); off = (1 - a) * -40
            tracked(d, 90 + off, 300, f"LESSON {i+1:02d}", F(28), tuple(int(c*a) for c in GOLD), tr=10)
            d.line([(90 + off, 350), (90 + off + 300 * ease((t - 0.3) / 0.8), 350)], fill=GOLD, width=2)
            f = F(64)
            for li, ln in enumerate(wrap(ttl, f, 420)):
                tracked(d, 90 + off, 380 + li * 74, ln, f, tuple(int(c*a) for c in INK), tr=6)
            if take:
                fi_ = F(30, True); a2 = ease((t - 0.6) / 0.8)
                for li, ln in enumerate(wrap(take, fi_, 400)[:4]):
                    d.text((90, 560 + li * 40), ln, font=fi_, fill=tuple(int(c*a2*0.85) for c in INK))
            # centre clip
            if t >= CARD:
                fr = next(gen, None)
                if fr is not None: last = fr
                if last is not None:
                    c = Image.fromarray(last[crop_t:crop_b, crop_l:crop_r]).resize((cw, ch), Image.LANCZOS)
                    a3 = ease((t - CARD) / 0.35)
                    if a3 < 1: c = Image.eval(c, lambda v: int(v * a3))
                    im.paste(c, (cx0, cy0))
                    d.rectangle([cx0 - 1, cy0 - 1, cx0 + cw, cy0 + ch], outline=(40, 38, 34))
            else:  # card: big lesson number in the centre
                a4 = ease(t / 0.4) * (1 - ease((t - CARD + 0.35) / 0.35))
                tracked(d, W / 2, H / 2 - 60, f"{i+1:02d}", F(140), tuple(int(c*a4) for c in GOLD), tr=8, anchor="c")
                tracked(d, W / 2, H / 2 + 110, ttl, F(36), tuple(int(c*a4) for c in INK), tr=10, anchor="c")
            emit(im)

    # outro
    mm, ss = divmod(int(tcur), 60); chapters.append((f"{mm:02d}:{ss:02d}", "Work with us"))
    audio_parts.append(np.vstack([whoosh(0.6, 0.2), np.zeros((int((OUTRO - 0.6) * SR), 2), np.float32)]))
    for k in range(int(OUTRO * FPS)):
        t = k / FPS; im = base_layer(); d = ImageDraw.Draw(im)
        a = ease(t / 0.8)
        tracked(d, W / 2, 330, "SUBSCRIBE FOR A NEW LESSON EVERY DAY", F(40), tuple(int(c*a) for c in INK), tr=8, anchor="c")
        d.line([(W/2 - 300 * a, 420), (W/2 + 300 * a, 420)], fill=GOLD, width=2)
        a2 = ease((t - 0.8) / 0.8)
        tracked(d, W / 2, 500, SERVICE, F(36), tuple(int(c*a2) for c in INK), tr=8, anchor="c")
        tracked(d, W / 2, 560, "Custom animations for creators and brands", F(30, True), tuple(int(c*a2*0.8) for c in INK), anchor="c")
        tracked(d, W / 2, 640, EMAIL, F(54), tuple(int(c*a2) for c in GOLD), tr=10, anchor="c")
        emit(im)

    enc.stdin.close(); enc.wait()
    a = np.vstack(audio_parts); a /= max(1e-6, np.abs(a).max()) / 0.9
    with wave.open(f"{tmp}/a.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((a * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{tmp}/v.mp4", "-i", f"{tmp}/a.wav", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out + ".tmp.mp4"], check=True)
    os.replace(out + ".tmp.mp4", out)
    open(os.path.splitext(out)[0] + "_chapters.txt", "w").write("\n".join(f"{a} {b}" for a, b in chapters) + "\n")
    return out

# --------------------------------------------------------------------------- TALL
def build_tall(title, out, clips):
    W, H = 1080, 1920
    CARD, OUTRO = 1.0, 3.5
    tmp = tempfile.mkdtemp()
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                            "-maxrate", "3500k", "-bufsize", "7000k", "-pix_fmt", "yuv420p", f"{tmp}/v.mp4"],
                           stdin=subprocess.PIPE)
    G = [grain(H, W, s) for s in range(4)]; fi = 0
    def emit(img):
        nonlocal fi
        a = np.asarray(img, np.float32) + G[fi % 4]
        enc.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes()); fi += 1
    audio_parts = []
    metas = [meta(c) for c in clips]; n = len(clips)
    for i, (clip, (ttl, take)) in enumerate(zip(clips, metas)):
        dur = duration(clip)
        audio_parts.append(np.vstack([whoosh(CARD, 0.18), audio(clip, dur)]))
        for k in range(int(CARD * FPS)):  # lesson card (inside the safe zone)
            t = k / FPS; im = Image.new("RGB", (W, H), (6, 6, 8)); d = ImageDraw.Draw(im)
            a = ease(t / 0.35) * (1 - ease((t - CARD + 0.3) / 0.3))
            tracked(d, W/2, 700, f"LESSON {i+1} / {n}", F(36), tuple(int(c*a) for c in GOLD), tr=10, anchor="c")
            for li, ln in enumerate(wrap(ttl, F(80), 900)):
                tracked(d, W/2, 780 + li * 92, ln, F(80), tuple(int(c*a) for c in INK), tr=8, anchor="c")
            emit(im)
        for fr in frames(clip):
            emit(Image.fromarray(fr))
    audio_parts.append(np.vstack([whoosh(0.6, 0.2), np.zeros((int((OUTRO - 0.6) * SR), 2), np.float32)]))
    for k in range(int(OUTRO * FPS)):
        t = k / FPS; im = Image.new("RGB", (W, H), (6, 6, 8)); d = ImageDraw.Draw(im)
        a = ease(t / 0.6); a2 = ease((t - 0.6) / 0.6)
        tracked(d, W/2, 640, "FOLLOW FOR A LESSON A DAY", F(44), tuple(int(c*a) for c in INK), tr=6, anchor="c")
        d.line([(W/2 - 260*a, 720), (W/2 + 260*a, 720)], fill=GOLD, width=2)
        tracked(d, W/2, 790, SERVICE, F(38), tuple(int(c*a2) for c in INK), tr=6, anchor="c")
        tracked(d, W/2, 860, EMAIL, F(52), tuple(int(c*a2) for c in GOLD), tr=8, anchor="c")
        tracked(d, W/2, 1380, "MOTIVATION RECLAIMED", F(26), DIM, tr=9, anchor="c")
        emit(im)
    enc.stdin.close(); enc.wait()
    a = np.vstack(audio_parts); a /= max(1e-6, np.abs(a).max()) / 0.9
    with wave.open(f"{tmp}/a.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((a * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{tmp}/v.mp4", "-i", f"{tmp}/a.wav", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out + ".tmp.mp4"], check=True)
    os.replace(out + ".tmp.mp4", out)
    return out

if __name__ == "__main__":
    mode, title, out, *clips = sys.argv[1:]
    print((build_wide if mode == "wide" else build_tall)(title, out, clips))
