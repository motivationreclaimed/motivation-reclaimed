"""Synthesised sound design. Calm ambient bed + spec events + the sound logo.

Spec may define SOUNDS = [(time, kind, gain), ...] with kinds:
  thud, whoosh, step, hit, crack, rumble, tick, chime
The SOUND LOGO (deep swell + golden bell) plays automatically at spec.PAYOFF.
"""
import numpy as np, wave

SR = 44100

def _lp(x, a):
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y

def _env(n, att, dec):
    tt = np.arange(n) / SR
    return np.minimum(1, tt / max(att, 1e-4)) * np.exp(-tt / dec)

def _noise(n, seed):
    return np.random.default_rng(seed).normal(0, 1, n).astype(np.float32)

def bell(d=3.0, f0=392.0, seed=1):
    n = int(SR * d); tt = np.arange(n) / SR
    parts = [(1.0, 1.0, 1.2), (2.0, 0.5, 0.9), (2.76, 0.35, 0.7), (5.4, 0.18, 0.4), (8.9, 0.08, 0.25)]
    s = sum(a * np.sin(2*np.pi*f0*m*tt + i) * np.exp(-tt / (dec * d / 2.2)) for i, (m, a, dec) in enumerate(parts))
    return s * _env(n, 0.002, d)

def swell(d=2.6, seed=2):
    n = int(SR * d); tt = np.arange(n) / SR
    f = 32 + 60 * np.exp(-tt * 5)
    s = np.sin(2*np.pi*np.cumsum(f)/SR) * _env(n, 0.004, d/3)
    return s + _lp(_noise(n, seed), 0.05) * _env(n, 0.002, 0.12) * 0.8

def thud(seed=3):
    n = int(SR*0.5); tt = np.arange(n)/SR
    f = 50 + 90*np.exp(-tt*18)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*_env(n, 0.002, 0.12) + _lp(_noise(n, seed), 0.2)*_env(n, 0.001, 0.03)

def whoosh(d=0.5, seed=4, rev=False):
    n = int(SR*d); tt = np.arange(n)/SR
    s = _lp(_noise(n, seed), 0.12) * np.sin(np.pi*tt/d)**2
    return s[::-1] if rev else s

def step(seed=5):
    n = int(SR*0.12)
    return _lp(_noise(n, seed), 0.3) * _env(n, 0.001, 0.02)

def hit(seed=6):
    n = int(SR*0.8); tt = np.arange(n)/SR
    m = sum(np.sin(2*np.pi*f*tt + i)*np.exp(-tt*(6+i*3))/(i+1) for i, f in enumerate([220, 547, 893, 1310]))
    return 0.5*m + thud(seed)[:n] if n <= int(SR*0.5) else np.concatenate([0.5*m[:int(SR*0.5)] + thud(seed), 0.5*m[int(SR*0.5):]])

def crack(seed=7):
    n = int(SR*0.35)
    return _noise(n, seed) * _env(n, 0.0005, 0.04) * (np.random.default_rng(seed).random(n) > 0.6)

def rumble(d=1.5, seed=8):
    n = int(SR*d); tt = np.arange(n)/SR
    return _lp(_noise(n, seed), 0.02)*3 * np.sin(np.pi*tt/d)

def tick(seed=9):
    n = int(SR*0.06); tt = np.arange(n)/SR
    return np.sin(2*np.pi*2400*tt)*_env(n, 0.0005, 0.01)

KINDS = dict(thud=thud, whoosh=whoosh, step=step, hit=hit, crack=crack, rumble=rumble, tick=tick,
             chime=lambda seed=10: bell(1.6, 587.33, seed))

def build(spec, path):
    dur = spec.DURATION; N = int(SR * dur); t = np.arange(N) / SR
    out = np.zeros((N, 2), np.float32)
    def add(sig, at, g=1.0, pan=0.0):
        i = int(at * SR); j = min(N, i + len(sig))
        if i >= N or j <= i: return
        out[i:j, 0] += sig[:j-i] * g * (1 - pan) ** 0.5
        out[i:j, 1] += sig[:j-i] * g * (1 + pan) ** 0.5
    # calm bed: soft minor-ish pad + air
    pad = sum(np.sin(2*np.pi*f*t + k) * a for k, (f, a) in enumerate([(55, .22), (82.4, .12), (110, .07), (164.8, .04)]))
    pad *= (0.75 + 0.25*np.sin(2*np.pi*0.18*t)) * np.minimum(1, t/0.6)
    out += pad[:, None] * 0.5
    out += (_lp(_noise(N, 11), 0.03) * 0.25)[:, None]
    for k, ev in enumerate(getattr(spec, "SOUNDS", [])):
        at, kind = ev[0], ev[1]; g = ev[2] if len(ev) > 2 else 0.6
        add(KINDS[kind](seed=20 + k), at, g, pan=((k % 3) - 1) * 0.3)
    p = getattr(spec, "PAYOFF", None)
    if p is not None:  # SOUND LOGO
        add(whoosh(0.7, 30, rev=True), p - 0.7, 0.7)
        add(swell(), p, 1.2)
        add(bell(3.2, 392.0, 31), p + 0.02, 0.9, -0.15)
        add(bell(3.0, 587.33, 32), p + 0.1, 0.45, 0.2)
    out /= max(1e-6, np.abs(out).max()) / 0.89
    out *= np.clip((dur - t) / 0.35, 0, 1)[:, None]
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())
