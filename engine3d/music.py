"""Soft, beatless ambient pad (no drums, no melody) — slow warm chords, mixed quietly under the SFX."""
import numpy as np, wave
SR = 44100
CHORDS = [[48, 55, 60, 64, 71], [45, 52, 57, 60, 67], [41, 48, 55, 57, 64], [43, 50, 55, 59, 62]]   # Cmaj7 Am7 Fmaj7 G6
# scene moods (all beatless, no melody): the score follows the story and resolves warm at the payoff
MOODS = {
    "warm":    CHORDS,                                                                              # calm, everyday
    "hopeful": [[41, 48, 57, 60, 64], [43, 50, 55, 59, 66], [45, 52, 57, 60, 64], [48, 55, 59, 64, 67]],  # Fmaj7 G Am Cmaj7: rising
    "tense":   [[45, 52, 57, 60, 64], [41, 48, 53, 57, 60], [38, 45, 50, 53, 57], [40, 47, 52, 56, 59]],  # Am F Dm E: struggle, setbacks
    "night":   [[38, 45, 50, 53, 60], [43, 50, 55, 58, 62], [36, 43, 48, 51, 55], [41, 48, 53, 56, 60]],  # Dm9 Gm Cm Fm: late night, phone, sleep
}
RESOLVE = [36, 43, 48, 52, 55, 62]                                                                  # Cadd9: the gold payoff
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def pad(dur, seed=0, lift=None, mood="warm"):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n, np.float32)
    chords = list(MOODS.get(mood, CHORDS))
    end = lift if lift else dur
    seg = end / len(chords)
    if lift:                                                       # resolve to a warm chord at the payoff
        env = np.clip((t - lift + 0.4) / 0.8, 0, 1).astype(np.float32)
        for m in RESOLVE:
            for det in (-0.1, 0.1):
                f = hz(m + det); out += (np.sin(2 * np.pi * f * t) * 0.7 + np.sin(4 * np.pi * f * t) * 0.1).astype(np.float32) * env / len(RESOLVE)
    for i, ch in enumerate(chords):
        env = np.clip(1 - np.abs((t - (i + 0.5) * seg) / (seg * 0.95)), 0, 1) ** 1.2   # long cross-fades
        for m in ch:
            for det in (-0.12, 0.12):
                f = hz(m + det); out += (np.sin(2 * np.pi * f * t + i) * 0.6 + np.sin(4 * np.pi * f * t) * 0.12).astype(np.float32) * env / len(ch)
    k = np.exp(-np.arange(0, 0.25, 1 / SR) / 0.08).astype(np.float32); k /= k.sum()         # soften (low-pass)
    out = np.convolve(out, k, mode="same")
    for dly, g in ((0.11, 0.35), (0.23, 0.25), (0.37, 0.15)):                                # airy echo
        sft = int(dly * SR); out[sft:] += out[:-sft] * g
    fade = np.minimum(1, np.minimum(t / 1.2, (dur - t) / 1.5)).astype(np.float32)
    if lift is not None: out *= (1 + 0.6 * np.clip((t - lift) / 1.0, 0, 1)).astype(np.float32)   # gentle swell at payoff
    return out * fade / (np.abs(out).max() + 1e-9)

LIB = __import__("os").path.join(__import__("os").path.dirname(__file__), "..", "assets", "music")
RESOLVE_AT = 9.0          # where every library track lands its gold chord (tools/compose_music.py)

def track(dur, lift=None, mood="warm"):
    """A real composed track for this mood (assets/music/<mood>_N.ogg), aligned so its resolve hits the PAYOFF.
    Falls back to the synth pad if the library is missing."""
    import os, glob, random, subprocess
    files = sorted(glob.glob(os.path.join(LIB, f"{mood}_*.ogg"))) or sorted(glob.glob(os.path.join(LIB, "warm_*.ogg")))
    if not files: return None
    f = random.choice(files)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32).copy()
    off = RESOLVE_AT - (lift if lift else 8.0)
    n = int(dur * SR); i0 = int(off * SR); out = np.zeros(n, np.float32)
    src0, dst0 = max(0, i0), max(0, -i0)
    seg = a[src0: src0 + n - dst0]; out[dst0: dst0 + len(seg)] = seg
    out[:int(0.03 * SR)] *= np.linspace(0, 1, int(0.03 * SR))          # click-free start (no audible fade-in)
    t = np.arange(n) / SR; out *= np.clip((dur - t) / 0.5, 0, 1)       # short fade-out with the picture
    print("music:", os.path.basename(f))
    return out

def mix_into(wav_path, dur, level=0.34, lift=None, mood="warm"):
    with wave.open(wav_path) as w:
        ch, sw, sr, nf = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        a = np.frombuffer(w.readframes(nf), np.int16).astype(np.float32).reshape(-1, ch) / 32768
    p = track(nf / sr, lift=lift, mood=mood)
    if p is None: p = pad(nf / sr, lift=lift, mood=mood); level = 0.38
    if sr != SR: p = np.interp(np.linspace(0, len(p) - 1, nf), np.arange(len(p)), p)
    a += (p[:nf] * level)[:, None]
    a = np.clip(a, -0.98, 0.98)
    with wave.open(wav_path, "w") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32767).astype(np.int16).tobytes())
