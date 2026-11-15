"""Render a 3D 'gold light' spec.
  python3 make3d.py specs/NNN_slug.py                      -> videos/NNN_slug.mp4
  python3 make3d.py specs/NNN_slug.py --stills 0.8 3 5 8   -> previews/NNN_slug_sheet.png
A 3D spec defines: DUR, PAYOFF, SOUNDS, CTA, CAPTION, frame(t, sub) -> (float image, overlay(draw)), optional BLUR=(t0, t1)."""
import sys, os, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine3d.r3d import render, stills

path = sys.argv[1]; name = os.path.splitext(os.path.basename(path))[0]
spec_ = importlib.util.spec_from_file_location(name, path); spec = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(spec)
if "--stills" in sys.argv:
    os.makedirs("previews", exist_ok=True)
    ts = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1:]]
    stills(os.path.join("previews", name), spec.frame, ts); print(f"previews/{name}_sheet.png")
else:
    os.makedirs("videos", exist_ok=True); out = os.path.join("videos", name + ".mp4")
    render(out, spec.frame, spec.DUR, spec.PAYOFF, spec.SOUNDS, blur=getattr(spec, "BLUR", None)); print(out)
