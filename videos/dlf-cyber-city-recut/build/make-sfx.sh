#!/bin/bash
# Mixkit SFX (Mixkit Sound Effects Free License: free for commercial use, no attribution)
# -> assets/sfx-mk/<name>.mp3, trimmed around the hit, pitched down 2 semitones,
# with a small dip in the voice presence band, peak-normalized. Writes build/sfx-meta.json
# (duration + time of the loudest point) so the composition can land each hit on its cue.
set -euo pipefail
cd "$(dirname "$0")/.."
RAW=build/mixkit-raw; OUT=assets/sfx-mk; mkdir -p "$RAW" "$OUT"
# name id lead(s before peak kept) tail_end(s)
SFX="
sweepA 166 0.3 0.6
sweepB 168 0.3 0.75
sweepC 175 0.3 0.6
sweepD 3115 0.1 0.35
swooshFast 174 0.3 0.75
whooshA 1490 0.4 0.95
whooshB 1492 0.7 1.4
whooshC 1489 0.5 1.4
whooshD 1471 0.2 0.95
logo 2900 1.3 7.4
hitShort 2299 0.1 0.7
hitFuture 2303 0.2 0.95
zoomHit 772 0.3 0.8
trailerHit 2908 0.5 2.5
epicHit 2901 0.6 3.6
deepImpact 1143 0.35 1.6
whooshImpact 2903 0.6 2.5
popLight 3005 0.05 0.25
popHard 2364 0.02 0.35
popLong 2358 0.03 0.4
popDry 2356 0.15 0.3
popMsg 2354 0.05 0.5
clickBox 1120 0.1 0.25
clickCool 2568 0.02 0.2
clickTech 3124 0.02 0.3
clickClassic 1117 0.12 0.3
tickCorrect 2870 0.03 0.6
positive 951 0.2 1.4
confirm 2867 0.17 0.6
sparkle 2350 0.75 2.2
negTap 2569 0.05 0.5
buzzer 948 0.02 1.2
bells 937 1.15 2.2
"
EQ="highpass=f=40,equalizer=f=2600:t=q:w=1.2:g=-4"
R=0.8909  # 2^(-2/12)
echo "{" > build/sfx-meta.json
first=1
while read -r name id lead tail; do
  [ -z "$name" ] && continue
  [ -f "$RAW/$id.mp3" ] || curl -sf -m 30 -o "$RAW/$id.mp3" "https://assets.mixkit.co/active_storage/sfx/$id/$id-preview.mp3"
  peak=$(ffmpeg -nostdin -v error -i "$RAW/$id.mp3" -ac 1 -ar 8000 -f s16le - | python3 -I -c "
import sys,array
a=array.array('h',sys.stdin.buffer.read()); w=80
env=[max(abs(x) for x in a[i:i+w]) for i in range(0,len(a),w)]
print(env.index(max(env))*w/8000)")
  ss=$(python3 -c "print(max(0,$peak-$lead))"); to=$(python3 -c "print(max($tail,$peak+0.05)+0.12)")
  ffmpeg -nostdin -v error -y -i "$RAW/$id.mp3" -af "atrim=$ss:$to,asetpts=PTS-STARTPTS,asetrate=44100*$R,aresample=44100,$EQ,afade=t=in:d=0.01,areverse,afade=t=in:d=0.12,areverse,loudnorm=I=-16:TP=-1:LRA=11,alimiter=limit=0.89" -ar 44100 -ac 2 -b:a 192k "$OUT/$name.mp3"
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$name.mp3")
  pk=$(python3 -c "print(round(min($peak,$lead) / $R, 3))")
  [ $first = 1 ] || echo "," >> build/sfx-meta.json; first=0
  printf '  "%s": {"id": %s, "dur": %s, "peak": %s}' "$name" "$id" "$dur" "$pk" >> build/sfx-meta.json
done <<< "$SFX"
echo "}" >> build/sfx-meta.json
ls "$OUT" | wc -l
