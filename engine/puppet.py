"""Cut-out puppet of the owner's cartoon character (assets/puppet/*.png, side view facing right).

The same pose dictionaries as the stick figure drive it, so every existing pose/walk/climb works.
Parts are rotated around their joints (brown circles on the art) and pasted back-to-front.
"""
import math, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.join(HERE, "..", "assets", "puppet")

# local pivots in each part image (pixels): top joint, bottom joint
PIV = {
    "torso":        dict(hip=(133, 539), shoulder=(84, 96), collar=(150, 26)),
    "neck":         dict(bottom=(64, 200), top=(77, 35)),
    "head":         dict(neck=(168, 400)),
    "upperarm":     dict(top=(83, 70), bottom=(77, 359)),
    "forearm":      dict(top=(52, 39), bottom=(58, 405)),
    "forearm_fist": dict(top=(52, 39), bottom=(64, 362)),
    "thigh":        dict(top=(94, 34), bottom=(96, 556)),
    "shin":         dict(top=(79, 35), bottom=(78, 500)),
    "shoe":         dict(top=(79, 32)),
}
_src = {}
def src(name):
    if name not in _src:
        _src[name] = Image.open(os.path.join(PDIR, name + ".png")).convert("RGBA")
    return _src[name]

def seglen(name):
    p, q = PIV[name]["top"], PIV[name]["bottom"]
    return math.hypot(q[0] - p[0], q[1] - p[1])

_cache = {}
def place(canvas, name, pivot, world, angle_cw, S, flip=False, tint=1.0):
    """Paste part `name` so local `pivot` lands on `world`, rotated `angle_cw` degrees clockwise
    relative to how it is drawn, uniformly scaled by S."""
    key = (name, round(S, 3), flip, round(tint, 2))
    im = _cache.get(key)
    if im is None:
        im = src(name)
        if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        im = im.resize((max(1, int(im.width * S)), max(1, int(im.height * S))), Image.LANCZOS)
        if tint < 1:
            r, g, b, a = im.split()
            r = r.point(lambda v: int(v * tint)); g = g.point(lambda v: int(v * tint)); b = b.point(lambda v: int(v * tint))
            im = Image.merge("RGBA", (r, g, b, a))
        _cache[key] = im
    w0, h0 = src(name).size
    px = (w0 - pivot[0]) if flip else pivot[0]
    px, py = px * S, pivot[1] * S
    rot = im.rotate(-angle_cw, resample=Image.BICUBIC, expand=True)
    # where does the pivot end up after rotating around the image centre?
    cx, cy = im.width / 2, im.height / 2
    a = math.radians(angle_cw)
    dx, dy = px - cx, py - cy
    rx, ry = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
    nx, ny = rot.width / 2 + rx, rot.height / 2 + ry
    canvas.paste(rot, (int(round(world[0] - nx)), int(round(world[1] - ny))), rot)

def axis_angle(name, flip):
    p, q = PIV[name]["top"], PIV[name]["bottom"]
    dx, dy = q[0] - p[0], q[1] - p[1]
    if flip: dx = -dx
    return math.atan2(dy, dx)

def draw(ctx, x, gy, pose, facing, sc, glow=0.0, fist=False):
    S = 0.165 * sc
    flip = facing < 0
    r = math.radians
    TH, SH = seglen("thigh") * S, seglen("shin") * S
    UA, FA = seglen("upperarm") * S, seglen("forearm" if not fist else "forearm_fist") * S
    tp = PIV["torso"]
    TORSO = math.hypot(tp["shoulder"][0] - tp["hip"][0], tp["shoulder"][1] - tp["hip"][1]) * S
    shoe_h = (src("shoe").height - PIV["shoe"]["top"][1]) * S
    hip_h = pose["hip"] / 136.0 * (TH + SH + shoe_h * 0.85)
    hip = (x, gy - hip_h)
    def v(a): return (math.sin(r(a)) * facing, math.cos(r(a)))
    def chain(o, a1, l1, a2, l2):
        v1 = v(a1); p1 = (o[0] + v1[0] * l1, o[1] + v1[1] * l1)
        v2 = v(a2); return p1, (p1[0] + v2[0] * l2, p1[1] + v2[1] * l2)
    lean = pose["lean"]
    kL, aL = chain(hip, pose["thL"], TH, pose["shL"], SH)
    kR, aR = chain(hip, pose["thR"], TH, pose["shR"], SH)
    # torso: rotate the art so hip->shoulder follows the lean
    tdx, tdy = tp["shoulder"][0] - tp["hip"][0], tp["shoulder"][1] - tp["hip"][1]
    if flip: tdx = -tdx
    art_ang = math.atan2(tdy, tdx)
    want = math.atan2(-math.cos(r(lean)), math.sin(r(lean)) * facing)
    t_rot = math.degrees(want - art_ang)
    def torso_pt(local):
        lx, ly = local[0] - tp["hip"][0], local[1] - tp["hip"][1]
        if flip: lx = -lx
        a = r(t_rot)
        return (hip[0] + (lx * math.cos(a) - ly * math.sin(a)) * S, hip[1] + (lx * math.sin(a) + ly * math.cos(a)) * S)
    sh = torso_pt(tp["shoulder"]); collar = torso_pt(tp["collar"])
    eL, wL = chain(sh, pose["uaL"], UA, pose["faL"], FA)
    eR, wR = chain(sh, pose["uaR"], UA, pose["faR"], FA)
    fa = "forearm_fist" if fist else "forearm"
    canvas = ctx.img

    def limb(name, P, Q, tint):
        ang = math.degrees(math.atan2(Q[1] - P[1], Q[0] - P[0]) - axis_angle(name, flip))
        place(canvas, name, PIV[name]["top"], P, ang, S, flip, tint)

    if glow > 0:  # warm halo BEHIND him (crisp layer) so he stays readable at the payoff
        R = int(150 * sc)
        key = ("halo", R)
        halo = _cache.get(key)
        if halo is None:
            from PIL import ImageFilter, ImageDraw
            halo = Image.new("L", (R * 4, R * 6), 0)
            ImageDraw.Draw(halo).ellipse([R, R, R * 3, R * 5], fill=255)
            halo = halo.filter(ImageFilter.GaussianBlur(R * 0.45)); _cache[key] = halo
        col = Image.new("RGB", halo.size, (255, 175, 70))
        m = halo.point(lambda v: int(v * 0.55 * glow))
        canvas.paste(col, (int(hip[0] - R * 2), int(hip[1] - R * 3.6)), m)
    # back limbs (slightly darker for depth)
    limb("upperarm", sh, eL, 0.72); limb(fa, eL, wL, 0.72)
    limb("thigh", hip, kL, 0.72); limb("shin", kL, aL, 0.72)
    place(canvas, "shoe", PIV["shoe"]["top"], aL, 0, S, flip, 0.8)
    # torso, neck, head
    place(canvas, "torso", tp["hip"], hip, t_rot, S, flip)
    place(canvas, "neck", PIV["neck"]["bottom"], collar, t_rot, S, flip)
    nk = PIV["neck"]
    a = r(t_rot); lx = (nk["top"][0] - nk["bottom"][0]) * (-1 if flip else 1); ly = nk["top"][1] - nk["bottom"][1]
    neck_top = (collar[0] + (lx * math.cos(a) - ly * math.sin(a)) * S, collar[1] + (lx * math.sin(a) + ly * math.cos(a)) * S)
    place(canvas, "head", PIV["head"]["neck"], neck_top, t_rot * 0.6, S, flip)
    # front limbs
    limb("thigh", hip, kR, 1.0); limb("shin", kR, aR, 1.0)
    place(canvas, "shoe", PIV["shoe"]["top"], aR, 0, S, flip)
    limb("upperarm", sh, eR, 1.0); limb(fa, eR, wR, 1.0)
    if glow > 0:  # gold shimmer on the shirt's crack
        k = 0.5
        ctx.g.line([(collar[0] * k, collar[1] * k), ((hip[0] + 8 * facing * sc) * k, (hip[1] - 20 * sc) * k)],
                   fill=tuple(int(c * glow) for c in (255, 190, 80)), width=int(4 + 4 * glow))
    return dict(hip=hip, neck=collar, head=neck_top, sh=sh, kL=kL, fL=aL, kR=kR, fR=aR,
                eL=eL, hL=wL, eR=eR, hR=wR, facing=facing, pose=pose, sc=sc)
