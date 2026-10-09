"""Generate the narration with Kokoro-82M (free, open-source, runs locally via `hyperframes tts`),
deepen it, and write assets/vo/<id>.mp3 plus build/vo-lines.json (timings for captions).
Needs: pip install kokoro-onnx soundfile"""
import json, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(ROOT, "build/vo-script.json")))
raw_dir = os.path.join(ROOT, "build/vo-raw"); out_dir = os.path.join(ROOT, "assets/vo")
os.makedirs(raw_dir, exist_ok=True); os.makedirs(out_dir, exist_ok=True)
# Pitch down ~8% without changing speed, warm low end, soft room, trim silence, level.
DEEPEN = ("silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_threshold=-45dB:stop_duration=0.25,"
          "asetrate=24000*0.92,aresample=48000,atempo=1/0.92,"
          "equalizer=f=100:t=q:w=1:g=5,equalizer=f=3000:t=q:w=1.5:g=-1.5,"
          "acompressor=threshold=-20dB:ratio=3:attack=10:release=150,"
          "aecho=0.8:0.5:40:0.10,apad=pad_dur=0.15,loudnorm=I=-16:TP=-1.5:LRA=7")

def probe(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))

out = {}
for lid, start, text in cfg["lines"]:
    raw = os.path.join(raw_dir, f"{lid}.wav")
    subprocess.run(["npx", "--prefix", os.path.dirname(os.path.dirname(ROOT)), "hyperframes", "tts", text,
                    "-v", cfg["voice"], "-s", str(cfg["speed"]), "-o", raw], check=True, capture_output=True)
    dst = os.path.join(out_dir, f"{lid}.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", DEEPEN, "-ar", "48000", "-b:a", "192k", dst], check=True)
    dur = probe(dst)
    out[lid] = {"start": start, "text": text, "dur": round(dur, 3)}
    print(f"{lid} {start:6.2f} +{dur:5.2f} -> {start + dur:6.2f}  {text}")
json.dump(out, open(os.path.join(ROOT, "build/vo-lines.json"), "w"), indent=1)
