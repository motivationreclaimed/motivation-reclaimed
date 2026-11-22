"""Light, original motivational FUNK background grooves (sampled bass, muted guitar, clav/e-piano, soft kit, brass hit).

Dev-time tool, run once (output committed to assets/music/funk_<mood>_N.ogg):
    python3 tools/compose_funk.py /path/to/FluidR3_GM.sf2
Each track: 14 s, ~107 bpm (1 bar = 2.25 s). 4 bars of groove, then at RESOLVE_AT = 9.0 s a crash + brass hit on the
"gold" chord (engine3d/music.py lines it up with the video's PAYOFF); the groove continues softly and fades.
"""
import sys, os, subprocess, numpy as np, fluidsynth

SR = 44100; BAR = 2.25; STEP = BAR / 16; RESOLVE_AT = 9.0; LENGTH = 14.0
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "music")
FBASS, SLAP, MUTEGTR, CLEANGTR, CLAV, EPIANO, BRASS = 33, 36, 28, 27, 7, 4, 61
KICK, SNARE, HAT, OHAT, CRASH, SHAKER = 36, 38, 42, 46, 49, 70
IV = {"m9": [0, 3, 7, 10, 14], "13": [0, 4, 10, 14, 21], "maj9": [0, 4, 7, 11, 14], "9": [0, 4, 7, 10, 14], "m7": [0, 3, 7, 10, 15]}

# name: (bars of (root, kind) x4, resolve (root, kind), keys instrument, bass instrument)
SONGS = {
    "warm_1":    ([(40, "m9"), (45, "13"), (40, "m9"), (45, "13")], (40, "m9"), CLAV, FBASS),
    "warm_2":    ([(38, "m9"), (43, "13"), (38, "m9"), (43, "13")], (38, "m9"), EPIANO, FBASS),
    "hopeful_1": ([(43, "maj9"), (36, "maj9"), (45, "m9"), (38, "9")], (43, "maj9"), EPIANO, FBASS),
    "hopeful_2": ([(36, "maj9"), (41, "maj9"), (40, "m7"), (45, "9")], (38, "m9"), CLAV, SLAP),
    "tense_1":   ([(45, "m9"), (45, "m9"), (38, "9"), (40, "9")], (45, "m9"), CLAV, FBASS),
    "night_1":   ([(41, "m9"), (46, "13"), (41, "m9"), (46, "13")], (41, "m9"), EPIANO, FBASS),
}


class Score:
    def __init__(self, seed):
        self.ev = []; self.rng = np.random.default_rng(seed)

    def note(self, ch, t, key, dur, vel, jitter=0.004):
        t = max(0.0, t + self.rng.normal(0, jitter)); vel = int(np.clip(vel + self.rng.normal(0, 4), 1, 127))
        self.ev.append((t, 1, ("on", ch, key, vel))); self.ev.append((t + dur, 0, ("off", ch, key)))


def st(bar, step):                       # time of a 16th step with a light swing on the off-16ths
    return bar * BAR + step * STEP + (0.014 if step % 2 else 0.0)


def compose(name):
    bars, (rr, rk), keys_prog, bass_prog = SONGS[name]
    S = Score(abs(hash(name)) % 2**32)
    nbars = int(np.ceil(LENGTH / BAR))
    res_bar = int(round(RESOLVE_AT / BAR))            # 4
    for b in range(nbars):
        after = b >= res_bar
        root, kind = (bars[b % 4] if not after else ((rr, rk) if b == res_bar else bars[(b - res_bar) % 4]))
        ch = [root + i for i in IV[kind]]
        soft = 0.75 if after else min(1.0, 0.7 + 0.1 * b)     # builds gently into the payoff, relaxes after
        # --- drums (channel 9) -------------------------------------------------
        for s in (0, 7, 10): S.note(9, st(b, s), KICK, 0.1, int(78 * soft))
        for s in (4, 12): S.note(9, st(b, s), SNARE, 0.1, int(64 * soft))
        for s in (7, 14): S.note(9, st(b, s), SNARE, 0.05, int(20 * soft))           # ghost notes
        for s in range(16):
            if s == 14 and b % 2: S.note(9, st(b, s), OHAT, 0.2, int(40 * soft)); continue
            S.note(9, st(b, s), HAT, 0.05, int((46 if s % 2 == 0 else 26) * soft))
        # --- bass ---------------------------------------------------------------
        bl = [(0, 0, 0.22), (3, 0, 0.1), (6, 12, 0.1), (8, 10, 0.18), (10, 0, 0.12), (11, 7, 0.1), (14, 12, 0.1)]
        for s, iv, d in bl: S.note(0, st(b, s), root - 12 + iv, d, int(92 * soft))
        # --- muted guitar scratch on the off-beats ------------------------------
        for s in (2, 6, 10, 14, 15):
            for k in ch[1:4]: S.note(1, st(b, s), k + 12, 0.07, int(52 * soft), jitter=0.002)
        # --- clav / e-piano stabs -------------------------------------------------
        for s, d in ((2, 0.12), (5, 0.1), (10, 0.25)):
            for k in ch[1:]: S.note(2, st(b, s), k + 12, d, int(58 * soft))
    # --- the PAYOFF hit at RESOLVE_AT -------------------------------------------
    R = RESOLVE_AT; rch = [rr + i for i in IV[rk]]
    S.note(9, R, CRASH, 1.5, 84); S.note(9, R, KICK, 0.1, 96)
    for k in rch[1:]: S.note(3, R, k + 12, 0.35, 92); S.note(3, R + 0.42, k + 12, 1.4, 70)
    S.note(0, R, rr - 12, 0.4, 110)
    # pickup into the hit: a short brass fall-in on the last two 16ths before it
    for k in rch[1:4]: S.note(3, R - 2 * STEP, k + 10, STEP * 0.9, 64); S.note(3, R - STEP, k + 11, STEP * 0.9, 70)
    return S, {0: bass_prog, 1: MUTEGTR, 2: keys_prog, 3: BRASS}


def render(S, progs, sf2):
    fs = fluidsynth.Synth(gain=0.45, samplerate=SR)
    sfid = fs.sfload(sf2)
    for ch, p in progs.items(): fs.program_select(ch, sfid, 0, p); fs.cc(ch, 91, 35)
    fs.program_select(9, sfid, 128, 0); fs.cc(9, 91, 25)
    try: fs.set_reverb(roomsize=0.5, damping=0.5, width=0.8, level=0.6)
    except Exception: pass
    out = []; now = 0.0
    for t, _, e in sorted(S.ev, key=lambda x: (x[0], x[1])):
        t = min(t, LENGTH)
        if t > now:
            n = int(t * SR) - int(now * SR)
            if n > 0: out.append(np.asarray(fs.get_samples(n), np.int16))
            now = t
        if e[0] == "on": fs.noteon(e[1], e[2], e[3])
        else: fs.noteoff(e[1], e[2])
    n = int(LENGTH * SR) - int(now * SR)
    if n > 0: out.append(np.asarray(fs.get_samples(n), np.int16))
    fs.delete()
    a = np.concatenate(out).astype(np.float32).reshape(-1, 2)[: int(LENGTH * SR)] / 32768
    a *= np.clip((LENGTH - np.arange(len(a)) / SR) / 1.8, 0, 1)[:, None]
    return a * (0.89 / (np.abs(a).max() + 1e-9))


if __name__ == "__main__":
    sf2 = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
    for name in SONGS:
        S, progs = compose(name); a = render(S, progs, sf2)
        raw = f"/tmp/funk_{name}.raw"; (a * 32767).astype("<i2").tofile(raw)
        dst = os.path.join(OUT, f"funk_{name}.ogg")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", raw,
                        "-c:a", "libvorbis", "-q:a", "6", dst], check=True)
        print("wrote", dst)
