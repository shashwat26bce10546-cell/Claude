#!/bin/bash
# Voice -> -15 LUFS. Clips placed in CORRECTED order (user numbering verified correct),
# fitted to each narration slot (slow up to 1.3x, then hold last frame), upscaled to 1080x1920.
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -v error -y -i assets/audio/voiceover.mp3 -af "highpass=f=70,acompressor=threshold=-22dB:ratio=2.5:attack=5:release=100:makeup=2,loudnorm=I=-15:TP=-1.5:LRA=8" -ar 48000 -c:a libmp3lame -b:a 192k assets/audio/voiceover-master.mp3
ORDER=(1 2 3 4 5 6 7 8)
STARTS=(0 5.4 10.78 17.4 22.54 26.86 32.96 36.54)
END=41.4
mkdir -p media/prepped
for i in $(seq 0 7); do
  n=${ORDER[$i]}; s=${STARTS[$i]}; pos=$((i+1))
  if [ $i -lt 7 ]; then e=${STARTS[$((i+1))]}; else e=$END; fi
  target=$(python3 -c "print(round($e-$s+0.6,3))")
  len=$(ffprobe -v error -show_entries format=duration -of csv=p=0 media/clips-ml/$n.mp4)
  f=$(python3 -c "print(round(min(max($target/$len,1.0),1.3),4))")
  ffmpeg -v error -y -i media/clips-ml/$n.mp4 -an -vf "setpts=${f}*PTS,fps=30,tpad=stop_mode=clone:stop_duration=10,scale=1080:1920:flags=lanczos,unsharp=5:5:0.5:5:5:0,eq=contrast=1.04:saturation=1.08,trim=duration=$target,setpts=PTS-STARTPTS,format=yuv420p" \
    -c:v libx264 -crf 18 -preset medium -movflags +faststart media/prepped/s$pos.mp4
  echo "slot $pos <- clip $n: ${len}s -> ${target}s (x$f)"
done
