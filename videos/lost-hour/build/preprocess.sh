#!/usr/bin/env bash
# Trim, scope-crop (1920x804, 2.39:1), grade and grain every shot in build/edl.json.
# Columns: [clip id, source in-point, timeline start, duration, gamma lift]
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p media/shots
python3 - <<'PY'
import json, glob, subprocess
e = json.load(open('build/edl.json'))
for i, (clip, src_in, _start, dur, gamma, *_rest) in enumerate(e['shots']):
    src = glob.glob(f'media/raw/{clip}*.mp4')[0]
    out = f'media/shots/{i:02d}-{clip}.mp4'
    vf = (f"fps=24,scale=1920:804:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:804,"
          f"eq=contrast=1.08:saturation=0.88:gamma={gamma},"
          "colorbalance=rs=0.03:bs=-0.02:rh=0.04:bh=-0.04,"
          "unsharp=5:5:0.6,noise=alls=7:allf=t,vignette=PI/5,format=yuv420p")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(src_in), '-i', src,
                    '-t', str(dur + 0.1), '-an', '-vf', vf,
                    '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-g', '12',
                    '-movflags', '+faststart', out], check=True)
    print(out)
PY
