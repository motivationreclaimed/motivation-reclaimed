"""Render a spec.

  python make.py specs/002_the_hill.py              -> videos/002_the_hill.mp4
  python make.py specs/002_the_hill.py --stills 2 6.5   -> preview PNGs in previews/
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import core

def main():
    path = sys.argv[1]
    spec = core.load_spec(path)
    name = os.path.splitext(os.path.basename(path))[0]
    if "--stills" in sys.argv:
        from PIL import Image
        os.makedirs("previews", exist_ok=True)
        ts = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1:]]
        ims = [Image.fromarray(core.render_frame(spec, int(t * core.FPS))) for t in ts]
        sheet = Image.new("RGB", (360 * len(ims), 640))
        for i, im in enumerate(ims): sheet.paste(im.resize((360, 640)), (i * 360, 0))
        sheet.save(f"previews/{name}_sheet.png"); print(f"previews/{name}_sheet.png")
        return
    os.makedirs("videos", exist_ok=True)
    print(core.render(spec, f"videos/{name}.mp4"))

if __name__ == "__main__":
    main()
