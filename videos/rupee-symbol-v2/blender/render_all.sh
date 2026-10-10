#!/usr/bin/env bash
# Render every shot and encode it to ../assets/shots/<scene>.mp4
#   ./render_all.sh draft|final [S01 S02 ...]   (default: all scenes, 2 parallel workers)
set -uo pipefail
cd "$(dirname "$0")"
Q=${1:-draft}; shift || true
SCENES=${*:-A C E F G I}
JOBS=${JOBS:-2}
mkdir -p ../assets/shots logs
one() {
  local s=$1 t=$SECONDS
  # frames already rendered are kept (resumable); delete renders/$Q/$s to force a re-render
  find "renders/$Q/$s" -name "*.png" -size 0 -delete 2>/dev/null
  python3 scenes_v2.py --render "$s" --quality "$Q" > "logs/$Q-$s.log" 2>&1
  ffmpeg -y -loglevel error -framerate 24 -i "renders/$Q/$s/%04d.png" \
    -c:v libx264 -pix_fmt yuv420p -crf "$([ "$Q" = final ] && echo 16 || echo 22)" -movflags +faststart \
    "../assets/shots/${s,,}.mp4" && echo "$s done in $((SECONDS - t))s"
}
for s in $SCENES; do
  one "$s" &
  while (( $(jobs -rp | wc -l) >= JOBS )); do wait -n; done
done
wait
echo ALL DONE
