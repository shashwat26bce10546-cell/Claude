#!/bin/bash
# media/source.mp4 -> media/enhanced.mp4
# 1080x1920 @30fps upscale, denoise, sharpen, light grade; feathered blur over the
# original burned-in captions (only while they are on screen); voice EQ + loudness.
set -euo pipefail
cd "$(dirname "$0")/.."
ffmpeg -v error -y -f lavfi -i "color=c=black:s=1080x380,format=gray" -frames:v 1 -vf "geq=lum='255*min(1,min(Y/70,(379-Y)/70))'" build/mask1.png
ffmpeg -v error -y -f lavfi -i "color=c=black:s=1080x220,format=gray" -frames:v 1 -vf "geq=lum='255*min(1,min(Y/50,(219-Y)/50))'" build/mask2.png
ffmpeg -v error -y -i media/source.mp4 -loop 1 -i build/mask1.png -loop 1 -i build/mask2.png -filter_complex "\
[0:v]fps=30,hqdn3d=1.5:1.5:4:4,scale=1080:1920:flags=lanczos,unsharp=5:5:0.75:5:5:0,eq=contrast=1.07:saturation=1.16:gamma=0.98,colorbalance=rm=0.015:bm=-0.015,format=yuv420p,split=3[base][c1][c2];\
[c1]crop=1080:380:0:1260,boxblur=30:3,eq=brightness=-0.06,format=rgba[b1];[1:v]format=gray[m1];[b1][m1]alphamerge[band1];\
[c2]crop=1080:220:0:965,boxblur=30:3,eq=brightness=-0.06,format=rgba[b2];[2:v]format=gray[m2];[b2][m2]alphamerge[band2];\
[base][band1]overlay=0:1260:shortest=1:enable='between(t,0.3,14.3)+between(t,14.9,24.2)+between(t,24.8,28.7)+between(t,31.4,60.8)'[v1];\
[v1][band2]overlay=0:965:shortest=1:enable='between(t,29.3,31.0)',format=yuv420p[v]" \
  -map "[v]" -map 0:a -af "highpass=f=80,afftdn=nf=-28,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2,loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000" \
  -c:v libx264 -crf 17 -preset medium -profile:v high -movflags +faststart -c:a aac -b:a 192k -ar 48000 media/enhanced.mp4
