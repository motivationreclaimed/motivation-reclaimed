"""Render a cartoon spec: frame_fn(t) -> uint8 HxWx3; SFX + soft beatless pad."""
import subprocess, os, types, sys
import numpy as np
from PIL import Image
from engine import sfx
from engine3d import music
W, H, FPS = 1080, 1920, 30

def render(out, frame_fn, dur, payoff, sounds, music_level=0.16):
    tmpv = out + ".v.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-crf", "18", "-maxrate", "10M", "-bufsize", "20M", "-preset", "medium", "-tune", "film",
                           "-pix_fmt", "yuv420p", tmpv], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        ff.stdin.write(np.ascontiguousarray(frame_fn(i / FPS)).tobytes())
    ff.stdin.close(); ff.wait()
    wav = out + ".wav"; sfx.build(types.SimpleNamespace(DURATION=dur, PAYOFF=payoff, SOUNDS=sounds), wav)
    music.mix_into(wav, dur, level=music_level, lift=payoff)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmpv, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(tmpv); os.remove(wav)

def stills(path, frame_fn, ts):
    ims = [Image.fromarray(frame_fn(t)).resize((432, 768)) for t in ts]
    sh = Image.new("RGB", (432 * len(ims), 768))
    for i, im in enumerate(ims): sh.paste(im, (i * 432, 0))
    sh.save(path)
