"""Owner's cartoon character, drawn from the finished full-body pose art (assets/poses/*.png, facing right).

No cut-out rig (that looked artificial): the engine's pose (named or interpolated dict) is matched to the
closest drawn pose and that whole drawing is shown, pose-to-pose like a cartoon. Walking alternates the
"walk" and "stand" drawings with a small bob. Returns the stick skeleton so specs can still attach props.
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.join(HERE, "..", "assets", "poses")

# engine pose name -> drawing
SPRITE = {
    "stand": "stand", "proud": "open_arms", "push": "push", "lift": "lift", "arms_up": "victory",
    "reach": "open_arms", "sit": "sit_hug", "slump": "sit_hug", "kneel": "kneel_pray",
    "squat": "lift", "floor": "sit_hug", "lie": "bed_phone", "phone": "stand",
}
STAND_PX = 330.0      # height of the standing drawing in the art
H_PER_SC = 340.0      # on-screen standing height per unit figure scale

_src, _cache = {}, {}
def src(name):
    if name not in _src:
        _src[name] = Image.open(os.path.join(PDIR, name + ".png")).convert("RGBA")
    return _src[name]

def sprite_for(pose, POSES):
    """Pick the drawing that best matches an (interpolated) pose dict."""
    if isinstance(pose, str):
        return SPRITE.get(pose, "stand"), 0.0
    stride = abs(pose.get("thL", 0) - pose.get("thR", 0))
    best, bd = "stand", 1e9
    for name, p in POSES.items():
        if name not in SPRITE or name in ("proud", "reach"): continue   # those only when named exactly
        d = sum(abs(pose.get(k, 0) - v) for k, v in p.items() if isinstance(v, (int, float)))
        if d < bd: best, bd = name, d
    spr = SPRITE[best]
    if spr == "stand" and stride > 30:          # mid-stride -> walking/running drawing (2-pose cycle)
        return ("run" if pose.get("lean", 0) > 9 else "walk"), stride
    return spr, stride

def get(name, S, flip, alpha):
    key = (name, round(S, 3), flip, round(alpha, 2))
    im = _cache.get(key)
    if im is None:
        im = src(name)
        im = im.resize((max(1, int(im.width * S)), max(1, int(im.height * S))), Image.LANCZOS)
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        if alpha < 1:
            r, g, b, a = im.split(); a = a.point(lambda v: int(v * alpha)); im = Image.merge("RGBA", (r, g, b, a))
        if len(_cache) > 400: _cache.clear()
        _cache[key] = im
    return im

def halo(R):
    key = ("halo", R)
    h = _cache.get(key)
    if h is None:
        h = Image.new("L", (R * 4, R * 6), 0)
        ImageDraw.Draw(h).ellipse([R, R, R * 3, R * 5], fill=255)
        h = h.filter(ImageFilter.GaussianBlur(R * 0.45)); _cache[key] = h
    return h

def draw(ctx, x, gy, pose, facing, sc, glow=0.0, alpha=1.0, POSES=None, skel=None):
    name, stride = sprite_for(pose, POSES)
    if isinstance(pose, str): pose = POSES[pose]
    S = H_PER_SC * sc / STAND_PX
    im = get(name, S, facing < 0, alpha)
    bob = -6 * sc if name in ("walk", "run") else 0
    H = H_PER_SC * sc
    if glow > 0:   # warm halo BEHIND him so he stays readable at the payoff
        R = int(150 * sc); h = halo(R)
        m = h.point(lambda v: int(v * 0.55 * glow))
        ctx.img.paste(Image.new("RGB", h.size, (255, 175, 70)), (int(x - R * 2), int(gy - H * 0.5 - R * 3)), m)
    ctx.img.paste(im, (int(round(x - im.width / 2)), int(round(gy - im.height + bob))), im)
    if glow > 0:   # soft gold bloom on the glow layer, around the chest crack only
        k = 0.5; cy = gy - H * 0.62
        ctx.g.ellipse([(x - 40 * sc) * k, (cy - 60 * sc) * k, (x + 40 * sc) * k, (cy + 60 * sc) * k],
                      fill=tuple(int(c * glow * 0.35) for c in (255, 180, 80)))
    return skel
