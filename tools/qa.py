"""QUALITY GATE for a finished video:  python3 tools/qa.py videos/NNN_slug.mp4
Writes previews/NNN_slug_qa.png (a frame every 0.25 s, time-stamped, safe zone) and prints automatic warnings
(frozen spans, black frames, wrong size/length). LOOK at every frame of the sheet before posting."""
import subprocess, sys, os, glob, tempfile
from PIL import Image, ImageDraw
v = sys.argv[1]; name = os.path.splitext(os.path.basename(v))[0]
info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "csv=p=0", v], capture_output=True, text=True).stdout.split()
print("size/duration:", info)
log = subprocess.run(["ffmpeg", "-i", v, "-vf", "freezedetect=n=0.001:d=0.6,blackdetect=d=0.2:pix_th=0.04", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
warn = [l for l in log.splitlines() if "freeze_start" in l or "black_start" in l]
print("WARNINGS:" if warn else "auto-checks: OK (no frozen spans >= 0.6 s, no black frames)")
for l in warn: print("  ", l.split("]")[-1].strip())
d = tempfile.mkdtemp()
subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-vf", "fps=4,crop=1080:1200:0:250,scale=216:-1", os.path.join(d, "f%03d.png")], check=True)
fs = sorted(glob.glob(os.path.join(d, "*.png"))); w, h = Image.open(fs[0]).size; cols = 10
sheet = Image.new("RGB", (cols * w, ((len(fs) + cols - 1) // cols) * (h + 14)), (50, 50, 50))
for i, f in enumerate(fs):
    x, y = (i % cols) * w, (i // cols) * (h + 14); sheet.paste(Image.open(f), (x, y + 14)); ImageDraw.Draw(sheet).text((x + 2, y), "%.2fs" % (i / 4), fill=(255, 255, 0))
os.makedirs("previews", exist_ok=True); out = f"previews/{name}_qa.png"; sheet.save(out); print(out)
