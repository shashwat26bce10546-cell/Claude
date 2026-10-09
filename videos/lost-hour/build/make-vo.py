"""Generate every voice in the trailer with Kokoro-82M (free, open-source, runs locally),
apply a per-role treatment, and write assets/vo/<id>.mp3 plus build/vo-lines.json.
Needs: pip install kokoro-onnx soundfile (model files are fetched by `npx hyperframes tts` once)."""
import json, os, subprocess
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.expanduser("~/.cache/hyperframes/tts")
kokoro = Kokoro(f"{CACHE}/models/kokoro-v1.0.onnx", f"{CACHE}/voices/voices-v1.0.bin")
cfg = json.load(open(os.path.join(ROOT, "build/vo-script.json")))
raw_dir = os.path.join(ROOT, "build/vo-raw"); out_dir = os.path.join(ROOT, "assets/vo")
os.makedirs(raw_dir, exist_ok=True); os.makedirs(out_dir, exist_ok=True)

TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:"
        "stop_threshold=-45dB:stop_duration=0.3")
LEVEL = "acompressor=threshold=-20dB:ratio=3:attack=10:release=150,apad=pad_dur=0.15,loudnorm=I={lufs}:TP=-1.5:LRA=7"
# The boy's filtered voice is spiky, so loudnorm alone stalls at the peak ceiling: squash it first.
SQUASH = "acompressor=threshold=-30dB:ratio=8:attack=3:release=80:makeup=12,alimiter=limit=0.8:level=false,"
LUFS = {"child-phone": -14, "child-whisper": -14}
FX = {
    # trailer narrator: a touch lower, big low end, small room
    "deep": "asetrate=24000*0.95,aresample=48000,atempo=1/0.95,equalizer=f=90:t=q:w=1:g=5,"
            "equalizer=f=3000:t=q:w=1.5:g=-1,aecho=0.8:0.5:40:0.08",
    # on-screen dialogue: dry and close
    "close": "aresample=48000,equalizer=f=150:t=q:w=1:g=2,aecho=0.8:0.4:25:0.05",
    # a child's voice down a phone line: pitch up, band-limited, a little crushed
    "child-phone": "asetrate=24000*1.28,aresample=48000,atempo=1/1.28,highpass=f=380,lowpass=f=3200,"
                   "acrusher=bits=10:mix=0.25,equalizer=f=1500:t=q:w=1:g=4",
    # a child whispering in an empty hallway: pitch up, airy, long tail
    "child-whisper": "asetrate=24000*1.25,aresample=48000,atempo=1/1.25,highpass=f=200,"
                     "equalizer=f=6000:t=q:w=1:g=3,aecho=0.8:0.7:120|260:0.35|0.2",
}

def probe(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))

out = {}
for lid, role, start, text in cfg["lines"]:
    v = cfg["voices"][role]
    audio, sr = kokoro.create(text, voice=v["voice"], speed=v["speed"], lang="en-us")
    raw = os.path.join(raw_dir, f"{lid}.wav"); sf.write(raw, audio, sr)
    dst = os.path.join(out_dir, f"{lid}.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", f"{TRIM},{FX[v['fx']]},{SQUASH if v['fx'] in LUFS else ''}{LEVEL.format(lufs=LUFS.get(v['fx'], -16))}",
                    "-ar", "48000", "-b:a", "192k", dst], check=True)
    dur = probe(dst)
    out[lid] = {"role": role, "start": start, "text": text, "dur": round(dur, 3)}
    print(f"{lid:3} {role:9} {start:6.2f} +{dur:5.2f} -> {start + dur:6.2f}  {text}")
json.dump(out, open(os.path.join(ROOT, "build/vo-lines.json"), "w"), indent=1)
