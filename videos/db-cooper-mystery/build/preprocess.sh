#!/bin/bash
# Voice: master to -15 LUFS. Clips: fit each 4s clip to its narration slot
# (slow down up to 1.3x, then hold the last frame), upscale to 1080x1920 @30fps, light sharpen.
# Each prepped clip = slot + 0.6s handle for transitions.
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -v error -y -i assets/audio/voiceover.mp3 -af "highpass=f=70,acompressor=threshold=-22dB:ratio=2.5:attack=5:release=100:makeup=2,loudnorm=I=-15:TP=-1.5:LRA=8" -ar 48000 -c:a libmp3lame -b:a 192k assets/audio/voiceover-master.mp3
STARTS=(0 5.56 10.7 15.46 20.3 25.38 28.54 33.22 36.62 40.54 44.6 50.1 55.82 57.48 63.0)
END=67.3
mkdir -p media/prepped
for i in $(seq 0 14); do
  n=$((i+1)); s=${STARTS[$i]}
  if [ $i -lt 14 ]; then e=${STARTS[$((i+1))]}; else e=$END; fi
  target=$(python3 -c "print(round($e-$s+0.6,3))")
  len=$(ffprobe -v error -show_entries format=duration -of csv=p=0 media/clips/$n.mp4)
  f=$(python3 -c "print(round(min(max($target/$len,1.0),1.3),4))")
  ffmpeg -v error -y -i media/clips/$n.mp4 -an -vf "setpts=${f}*PTS,fps=30,tpad=stop_mode=clone:stop_duration=10,scale=1080:1920:flags=lanczos,unsharp=5:5:0.5:5:5:0,eq=contrast=1.04:saturation=1.08,trim=duration=$target,setpts=PTS-STARTPTS,format=yuv420p" \
    -c:v libx264 -crf 18 -preset medium -movflags +faststart media/prepped/s$n.mp4
  echo "clip $n: ${len}s -> ${target}s (speed x$f)"
done
