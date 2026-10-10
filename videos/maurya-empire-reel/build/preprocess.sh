#!/bin/bash
# Fit each AI clip to its narration slot: slow-motion with motion interpolation when the
# clip is shorter than the slot, trim when longer; upscale to 1080x1920 @30fps, sharpen, warm grade.
# Each output = slot duration + 0.6s handle for crossfades.
set -euo pipefail
cd "$(dirname "$0")/.."
STARTS=(0 6.16 12.92 17.8 22.7 28.28 34.62 39.28 43.8 51.18)
END=58.6
mkdir -p media/prepped
for i in $(seq 0 9); do
  n=$((i+1)); s=${STARTS[$i]}
  if [ $i -lt 9 ]; then e=${STARTS[$((i+1))]}; else e=$END; fi
  target=$(python3 -c "print(round($e-$s+0.6,3))")
  len=$(ffprobe -v error -show_entries format=duration -of csv=p=0 media/clips/$n.mp4)
  f=$(python3 -c "print(round($target/$len,4))")
  if python3 -c "import sys; sys.exit(0 if $f>1.0 else 1)"; then
    speed="setpts=${f}*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1"
  else
    speed="fps=30"
  fi
  ffmpeg -v error -y -i media/clips/$n.mp4 -an -vf "$speed,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6:5:5:0,eq=contrast=1.06:saturation=1.08,colorbalance=rm=0.02:gm=0.005:bm=-0.025,trim=duration=$target,setpts=PTS-STARTPTS,format=yuv420p" \
    -c:v libx264 -crf 18 -preset medium -movflags +faststart media/prepped/s$n.mp4
  echo "scene $n: clip ${len}s -> ${target}s (x$f)"
done
