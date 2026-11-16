"""3D — THE LANE (RACE): PHONE vs DISCIPLINE. Same 24 hours; x4 speed-up to DAY 90; he crosses the gold line.
Uses the original race renderer (engine3d/race.py) — copy stairs/gym specs for new scenes."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine3d import race

DUR, PAYOFF, BLUR = 8.9, 7.6, (3.5, 5.5)
CTA = "Which lane are you in? Comment below."
CAPTION = """Same 24 hours, two very different lanes (discipline vs phone)

You don't need more time. You need the hour you're already giving away.

Which lane are you in?

#discipline #selfdiscipline #focus #motivation"""
SOUNDS = [(0.6, "tick", 0.4), (0.9, "tick", 0.4), (1.2, "hit", 0.5), (3.4, "whoosh", 0.6), (3.7, "tick", 0.3), (4.1, "tick", 0.3),
          (4.5, "tick", 0.3), (4.9, "tick", 0.3), (5.3, "tick", 0.3), (5.5, "whoosh", 0.4), (6.0, "thud", 0.3)] + \
         [(1.2 + k * 0.33, "step", 0.3) for k in range(7)] + [(5.5 + k * 0.33, "step", 0.3) for k in range(6)]

def frame(t, sub):
    img, cam, JH, JG, s, hx = race.frame(t, sub)
    return img, (lambda d: race.overlay_draw(d, t, cam, JH, JG, s, hx))
