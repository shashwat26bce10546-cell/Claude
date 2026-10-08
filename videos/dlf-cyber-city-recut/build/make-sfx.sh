#!/bin/bash
# Builds assets/sfx-low/: pitched-down, voice-friendly variants of the bundled SFX
# plus a few synthesized one-offs, so no effect repeats identically.
set -euo pipefail
cd "$(dirname "$0")/.."
IN=assets/sfx; OUT=assets/sfx-low; mkdir -p "$OUT"
# carve the speech band (2-3 kHz presence) and soften highs so the voice stays on top
EQ="highpass=f=45,equalizer=f=2500:t=q:w=1.2:g=-7,equalizer=f=1000:t=q:w=1:g=-3,lowpass=f=7000"
v() { # name src semitones extra-filter
  local r; r=$(python3 -c "print(round(2**($3/12),4))")
  ffmpeg -v error -y -i "$IN/$2.mp3" -af "asetrate=44100*$r,aresample=44100,$EQ${4:+,$4},afade=t=out:st=0:d=0.01:curve=tri,alimiter=limit=0.8" -ar 44100 -ac 2 -b:a 160k "$OUT/$1.mp3"
}
v whoosh-a        whoosh            -3
v whoosh-b        whoosh            -5  "atempo=1.15"
v whoosh-c        whoosh-short      -3
v whoosh-d        whoosh-short      -6
v whoosh-e        whoosh-cinematic  -3
v whoosh-f        whoosh-cinematic  -5  "aecho=0.6:0.4:60:0.3"
v hit-a           impact-bass-1     -3
v hit-b           impact-bass-2     -3
v hit-c           impact-bass-1     -5  "lowpass=f=3000"
v hit-d           impact-bass-2     -6
v pop-a           pop               -3
v pop-b           pop               -5
v pop-c           click             -4
v click-a         click             -3
v click-b         click-soft        -2
v ping-a          ping              -4
v ping-b          ping              -6
v sparkle-a       sparkle           -3
v chime-a         chime             -3
v glitch-a        glitch-1          -4  "volume=0.7"
v riser-a         riser             -3
# one-off for the AMBRANE reveal: deep sub drop + filtered noise burst + tail
ffmpeg -v error -y \
  -f lavfi -i "aevalsrc='0.9*sin(2*PI*(38*t+55*(1-exp(-6*t))/6*6))*exp(-2.2*t)':s=44100:d=2.2" \
  -f lavfi -i "anoisesrc=d=0.6:c=brown:a=0.5:r=44100" \
  -filter_complex "[1:a]lowpass=f=900,afade=t=out:st=0.05:d=0.5[n];[0:a][n]amix=inputs=2:weights='1 0.6':normalize=0,aecho=0.7:0.5:90|180:0.35|0.2,$EQ,alimiter=limit=0.8" \
  -ac 2 -b:a 160k "$OUT/ambrane-boom.mp3"
ls "$OUT" | wc -l
