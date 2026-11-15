"""TEMPLATE (owner-approved): 3D gold world + cartoon cast — RACE. Copy to specs/NNN_slug.py; to change the story copy engine3d/race.py logic into the spec."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine3d import race
race.TOON = True
exec(open(os.path.join(os.path.dirname(__file__), "..", "specs", "010_which_lane.py")).read().split("def frame")[0].split("from engine3d import race")[1])
def frame(t, sub):
    img, cam, JH, JG, s, hx = race.frame(t, sub)
    return img, (lambda d: race.overlay_draw(d, t, cam, JH, JG, s, hx))
