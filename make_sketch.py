"""Render a SKETCH-style spec:  python3 make_sketch.py specs/NNN_slug.py  [--stills t1 t2 ...]
A spec defines DUR (8-10 s), CAPTION and frame(t) -> PIL image (1080x1920, built with engine_sketch).
Audio: the owner's track (assets/music/owner/) from 0:00 on every video, faded out over the last 0.5 s."""
import sys, os, glob, importlib.util, subprocess
from PIL import Image
ROOT=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,ROOT)
from engine_sketch.sketch import W,H,FPS
def load(p):
    sp=importlib.util.spec_from_file_location("spec",p); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
if __name__=="__main__":
    path=sys.argv[1]; m=load(path); slug=os.path.splitext(os.path.basename(path))[0]
    if "--stills" in sys.argv:
        ts=[float(x) for x in sys.argv[sys.argv.index("--stills")+1:]]; ims=[m.frame(t) for t in ts]
        sh=Image.new("RGB",(270*len(ims),480))
        for i,im in enumerate(ims): sh.paste(im.resize((270,480)),(270*i,0))
        os.makedirs(os.path.join(ROOT,"previews"),exist_ok=True); out=os.path.join(ROOT,"previews",slug+"_stills.png"); sh.save(out); print(out); sys.exit()
    track=sorted(glob.glob(os.path.join(ROOT,"assets","music","owner","*.mp3")))[0]; DUR=m.DUR
    os.makedirs(os.path.join(ROOT,"videos"),exist_ok=True); out=os.path.join(ROOT,"videos",slug+".mp4"); tmp=out[:-4]+".part.mp4"
    p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",track,
        "-filter_complex",f"[1:a]atrim=0:{DUR},asetpts=N/SR/TB,volume=0.55,afade=t=out:st={DUR-0.5}:d=0.5[a]","-map","0:v","-map","[a]",
        "-c:v","libx264","-preset","medium","-tune","animation","-crf","16","-maxrate","16M","-bufsize","32M","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","192k","-t",str(DUR),"-movflags","+faststart",tmp],stdin=subprocess.PIPE)
    for i in range(int(round(DUR*FPS))): p.stdin.write(m.frame(i/FPS).convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    if p.returncode: sys.exit("ffmpeg failed")
    os.replace(tmp,out); print(out)
