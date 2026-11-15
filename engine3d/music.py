"""Soft, beatless ambient pad (no drums, no melody) — slow warm chords, mixed quietly under the SFX."""
import numpy as np, wave
SR = 44100
CHORDS = [[48, 55, 60, 64, 71], [45, 52, 57, 60, 67], [41, 48, 55, 57, 64], [43, 50, 55, 59, 62]]   # Cmaj7 Am7 Fmaj7 G6
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def pad(dur, seed=0, lift=None):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n, np.float32)
    seg = dur / len(CHORDS)
    for i, ch in enumerate(CHORDS):
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

def mix_into(wav_path, dur, level=0.16, lift=None):
    with wave.open(wav_path) as w:
        ch, sw, sr, nf = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        a = np.frombuffer(w.readframes(nf), np.int16).astype(np.float32).reshape(-1, ch) / 32768
    p = pad(nf / sr, lift=lift)
    if sr != SR: p = np.interp(np.linspace(0, len(p) - 1, nf), np.arange(len(p)), p)
    a += (p[:nf] * level)[:, None]
    a = np.clip(a, -0.98, 0.98)
    with wave.open(wav_path, "w") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32767).astype(np.int16).tobytes())
