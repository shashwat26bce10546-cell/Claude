"""Generate every voice in the trailer, apply a per-role treatment, and write
assets/vo/<id>.mp3 plus build/vo-lines.json (timings for captions and the mix).

Two free, local engines:
  * Chatterbox (Resemble AI, MIT) for the adults. It clones the timbre *and delivery* of a short
    reference clip (build/voice-refs/, public-domain LibriVox performances), and `ex` (emotion
    exaggeration) / `cfg` (pace) push the acting. Runs in its own Python env: set CHATTERBOX_PY to
    a python that has `chatterbox-tts` installed (torch CPU is fine, ~1 min per line).
  * Kokoro-82M for the boy (af_nicole pitched up), which needs kokoro-onnx + soundfile here.

Raw takes are cached in build/vo-raw/<id>.wav (gitignored); pass --regen to re-synthesize them.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(ROOT, "build/vo-script.json")))
raw_dir = os.path.join(ROOT, "build/vo-raw"); out_dir = os.path.join(ROOT, "assets/vo")
os.makedirs(raw_dir, exist_ok=True); os.makedirs(out_dir, exist_ok=True)
REGEN = "--regen" in sys.argv

TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:"
        "stop_threshold=-45dB:stop_duration=0.3")
LEVEL = "acompressor=threshold=-20dB:ratio=3:attack=10:release=150,apad=pad_dur=0.15,loudnorm=I={lufs}:TP=-1.5:LRA=7"
# The boy's filtered voice is spiky, so loudnorm alone stalls at the peak ceiling: squash it first.
SQUASH = "acompressor=threshold=-30dB:ratio=8:attack=3:release=80:makeup=12,alimiter=limit=0.8:level=false,"
LUFS = {"child-phone": -14, "child-whisper": -14}
FX = {
    # trailer narrator: warm low end, a little room
    "narrator": "aresample=48000,equalizer=f=100:t=q:w=1:g=4,equalizer=f=3000:t=q:w=1.5:g=-1,aecho=0.8:0.5:40:0.08",
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

# ---- synthesize missing raw takes
todo = [l for l in cfg["lines"] if REGEN or not os.path.exists(os.path.join(raw_dir, f"{l['id']}.wav"))]
cb_jobs = []
for l in todo:
    v = cfg["voices"][l["role"]]
    raw = os.path.join(raw_dir, f"{l['id']}.wav")
    if v["engine"] == "chatterbox":
        cb_jobs.append({"text": l["text"], "ref": os.path.join(ROOT, v["ref"]), "ex": l.get("ex", v["ex"]),
                        "cfg": l.get("cfg", v["cfg"]), "seed": l.get("seed", 7), "out": raw})
    else:
        import soundfile as sf
        from kokoro_onnx import Kokoro
        cache = os.path.expanduser("~/.cache/hyperframes/tts")
        k = Kokoro(f"{cache}/models/kokoro-v1.0.onnx", f"{cache}/voices/voices-v1.0.bin")
        audio, sr = k.create(l["text"], voice=v["voice"], speed=v["speed"], lang="en-us")
        sf.write(raw, audio, sr)
if cb_jobs:
    jobs = os.path.join(raw_dir, "chatterbox-jobs.json")
    json.dump(cb_jobs, open(jobs, "w"), indent=1)
    subprocess.run([os.environ.get("CHATTERBOX_PY", "python3"), os.path.join(ROOT, "build/cb_say.py"), jobs], check=True)

# ---- treat, level and time every line
out = {}
for l in cfg["lines"]:
    v = cfg["voices"][l["role"]]
    raw = os.path.join(raw_dir, f"{l['id']}.wav")
    dst = os.path.join(out_dir, f"{l['id']}.mp3")
    chain = f"{TRIM},{FX[v['fx']]},{SQUASH if v['fx'] in LUFS else ''}{LEVEL.format(lufs=LUFS.get(v['fx'], -16))}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", chain, "-ar", "48000", "-b:a", "192k", dst], check=True)
    dur = probe(dst)
    out[l["id"]] = {"role": l["role"], "start": l["start"], "text": l["text"], "dur": round(dur, 3)}
    print(f"{l['id']:3} {l['role']:16} {l['start']:6.2f} +{dur:5.2f} -> {l['start'] + dur:6.2f}  {l['text']}")
json.dump(out, open(os.path.join(ROOT, "build/vo-lines.json"), "w"), indent=1)
