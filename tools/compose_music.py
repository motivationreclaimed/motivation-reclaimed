"""Composes the channel's original background score library (real sampled instruments, no drums, no vocals).

Dev-time tool, run once (the result is committed to assets/music/, so video runs need nothing extra):
    python3 tools/compose_music.py /path/to/FluidR3_GM.sf2
FluidR3_GM (MIT licence) comes from the Ubuntu package fluid-soundfont-gm.

Every track is 14 s, 80 bpm (1 bar = 3 s). Bars 0-2 = the story chords, and at exactly RESOLVE_AT = 9.0 s
the piece lands on its warm "gold" chord (strings swell + celesta sparkle). engine3d/music.py lines that
moment up with the video's PAYOFF.
"""
import sys, os, subprocess, numpy as np, fluidsynth

SR = 44100
BEAT = 0.75; BAR = 3.0; RESOLVE_AT = 9.0; LENGTH = 14.0
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "music")

# General MIDI programs
PIANO, EPIANO, CELESTA, MUSICBOX, VIBES, HARP = 0, 4, 8, 10, 11, 46
CELLO, TREMOLO, PIZZ, STRINGS, SLOWSTR, PAD_WARM, PAD_NEW = 42, 44, 45, 48, 49, 89, 88


def chord(root, kind):
    iv = {"maj": [0, 4, 7, 11, 14], "add9": [0, 4, 7, 14, 16], "min": [0, 3, 7, 10, 14], "maj7": [0, 4, 7, 11, 16],
          "sus": [0, 5, 7, 12, 14], "dom": [0, 4, 7, 10, 14], "min9": [0, 3, 7, 10, 14]}[kind]
    return [root + i for i in iv]


# mood -> (story chords for bars 0-2, resolve chord). Roots are bass notes around C3 = 48.
SONGS = {
    "warm":    ([chord(48, "maj7"), chord(45, "min"), chord(41, "maj7")], chord(43, "sus"), chord(48, "add9")),
    "hopeful": ([chord(41, "maj7"), chord(43, "add9"), chord(45, "min")], chord(43, "add9"), chord(48, "add9")),
    "tense":   ([chord(45, "min"), chord(41, "maj7"), chord(38, "min9")], chord(40, "sus"), chord(45, "add9")),
    "night":   ([chord(38, "min9"), chord(46, "maj7"), chord(43, "min9")], chord(48, "sus"), chord(41, "add9")),
}
# per variant: arpeggio instrument, pad instrument, bass instrument, transpose, arpeggio pattern, melody on/off
VARIANTS = {
    "warm":    [(PIANO, SLOWSTR, CELLO, 0, "flow"), (HARP, STRINGS, CELLO, 2, "rise")],
    "hopeful": [(PIANO, STRINGS, CELLO, 0, "rise"), (PIANO, SLOWSTR, CELLO, -1, "flow")],
    "tense":   [(PIANO, TREMOLO, CELLO, 0, "pulse"), (PIZZ, SLOWSTR, CELLO, 1, "pulse")],
    "night":   [(EPIANO, PAD_WARM, CELLO, 0, "slow"), (VIBES, PAD_NEW, CELLO, 2, "slow")],
}


class Score:
    def __init__(self, seed):
        self.ev = []; self.rng = np.random.default_rng(seed)

    def note(self, ch, t, key, dur, vel):
        t = max(0.0, t + self.rng.normal(0, 0.008)); vel = int(np.clip(vel + self.rng.normal(0, 5), 1, 127))
        self.ev.append((t, 1, ("on", ch, key, vel))); self.ev.append((t + dur, 0, ("off", ch, key)))

    def cc(self, ch, t, num, val):
        self.ev.append((t, 2, ("cc", ch, num, int(np.clip(val, 0, 127)))))

    def swell(self, ch, t0, t1, v0, v1, num=11):
        for k in range(25):
            a = k / 24; self.cc(ch, t0 + (t1 - t0) * a, num, v0 + (v1 - v0) * a)


def compose(mood, vi):
    story, lead_in, resolve = SONGS[mood]
    arp_prog, pad_prog, bass_prog, tr, pattern = VARIANTS[mood][vi]
    story = [[n + tr for n in c] for c in story] + [[n + tr for n in lead_in]]
    resolve = [n + tr for n in resolve]
    S = Score(hash((mood, vi)) % 2**32)
    progs = {0: arp_prog, 1: pad_prog, 2: bass_prog, 3: CELESTA, 4: SLOWSTR}
    # bars 0-2: three story chords; the last two beats of bar 2 lean into the lead-in chord
    bars = [(0.0, BAR, story[0]), (BAR, BAR, story[1]), (2 * BAR, BAR - 2 * BEAT, story[2]), (3 * BAR - 2 * BEAT, 2 * BEAT, story[3])]
    for t0, dur, c in bars:
        root, rest = c[0], c[1:]
        # bass: long cello root (an octave down)
        S.note(2, t0, root - 12, dur + 0.05, 62 if mood != "tense" else 70)
        # pad: sustained mid voicing
        for k in rest[:3]: S.note(1, t0, k + 12, dur + 0.1, 52)
        # arpeggio
        upper = [root + 12] + [k + 12 for k in rest] + [rest[1] + 24]
        if pattern == "flow":      seq, step = [upper[0], upper[2], upper[4], upper[1], upper[3], upper[2], upper[4], upper[1]], BEAT / 2
        elif pattern == "rise":    seq, step = [upper[0], upper[1], upper[2], upper[3], upper[4], upper[5], upper[4], upper[2]], BEAT / 2
        elif pattern == "pulse":   seq, step = [root, root + 7, root, root + 7], BEAT
        else:                      seq, step = [upper[1], upper[3], upper[2], upper[4]], BEAT
        n = int(round(dur / step))
        for i in range(n):
            k = seq[i % len(seq)]
            vel = 58 + 10 * (i % 4 == 0) + int(8 * (t0 / RESOLVE_AT))       # slowly grows towards the payoff
            S.note(0, t0 + i * step, k, step * (2.5 if pattern != "pulse" else 0.9), vel)
        # sparse top melody (piano/e-piano voices only): one long note per half bar from chord tones
        if pattern in ("flow", "rise", "slow") and dur >= BAR - 0.01:
            for j, k in enumerate([rest[2] + 24, rest[3] + 12]):
                S.note(0, t0 + j * BAR / 2 + BEAT * 0.5, k, BAR / 2, 64)
    # build-up: pad + bass grow into the resolve
    S.swell(1, 0.0, RESOLVE_AT, 70, 112); S.swell(2, 0.0, RESOLVE_AT, 80, 110)
    S.cc(4, 0.0, 11, 0); S.swell(4, RESOLVE_AT - 2.2, RESOLVE_AT, 0, 90)
    for k in resolve[1:4]: S.note(4, RESOLVE_AT - 2.2, k + 12, 2.25, 60)          # string swell lifting into it
    # ---- RESOLVE (the gold payoff) ----
    R = RESOLVE_AT; tail = LENGTH - R
    S.note(2, R, resolve[0] - 12, tail, 82); S.note(2, R, resolve[0] - 24, tail, 64)
    for k in resolve[1:]: S.note(1, R, k + 12, tail, 70); S.note(4, R, k + 12, tail, 78)
    S.swell(4, R, R + 1.2, 90, 118); S.swell(4, R + 2.5, LENGTH, 118, 40); S.swell(1, R + 2.5, LENGTH, 112, 50)
    for i, k in enumerate([resolve[0] + 12] + [x + 12 for x in resolve[1:]] + [resolve[2] + 24]):   # rolled chord
        S.note(0, R + i * 0.06, k, tail, 80 - i * 3)
    for i, k in enumerate([resolve[0] + 36, resolve[2] + 36, resolve[3] + 36, resolve[4] + 36, resolve[1] + 48]):  # celesta sparkle
        S.note(3, R + 0.15 + i * 0.18, k, 1.6, 66)
    return S, progs


def render(S, progs, sf2):
    fs = fluidsynth.Synth(gain=0.5, samplerate=SR)
    for key, val in (("synth.reverb.active", 1), ("synth.chorus.active", 1)):
        try: fs.setting(key, val)
        except Exception: pass
    sfid = fs.sfload(sf2)
    for ch, p in progs.items(): fs.program_select(ch, sfid, 0, p); fs.cc(ch, 91, 100); fs.cc(ch, 93, 30)
    try: fs.set_reverb(roomsize=0.85, damping=0.4, width=0.9, level=0.9)
    except Exception: pass
    fs.cc(0, 64, 0)
    out = []; now = 0.0
    for t, _, e in sorted(S.ev, key=lambda x: (x[0], x[1])):
        t = min(t, LENGTH)
        if t > now:
            n = int(t * SR) - int(now * SR)
            if n > 0: out.append(np.asarray(fs.get_samples(n), np.int16))
            now = t
        if e[0] == "on": fs.noteon(e[1], e[2], e[3])
        elif e[0] == "off": fs.noteoff(e[1], e[2])
        else: fs.cc(e[1], e[2], e[3])
    n = int(LENGTH * SR) - int(now * SR)
    if n > 0: out.append(np.asarray(fs.get_samples(n), np.int16))
    fs.delete()
    a = np.concatenate(out).astype(np.float32).reshape(-1, 2) / 32768
    a = a[: int(LENGTH * SR)]
    fade = np.clip((LENGTH - np.arange(len(a)) / SR) / 1.5, 0, 1)[:, None]
    a *= fade
    return a * (0.89 / (np.abs(a).max() + 1e-9))


if __name__ == "__main__":
    sf2 = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
    for mood in SONGS:
        for vi in range(len(VARIANTS[mood])):
            S, progs = compose(mood, vi)
            a = render(S, progs, sf2)
            raw = f"/tmp/{mood}_{vi + 1}.raw"; (a * 32767).astype("<i2").tofile(raw)
            dst = os.path.join(OUT, f"{mood}_{vi + 1}.ogg")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", raw,
                            "-c:a", "libvorbis", "-q:a", "6", dst], check=True)
            print("wrote", dst)
