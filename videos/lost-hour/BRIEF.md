---
workflow: general-video
flow: automation
storyboard: no
message: "A small town loses one hour every night at 3:17 A.M. — and something comes back with it"
aspect: "16:9 (2.39:1 scope letterbox)"
length: "60s"
destination: "Filmsupply Editfest 2026 — Movie Trailer category"
---

## Intent
Edit a 60s movie trailer "like the examples" in the user's screen recording: the Editfest Movie
Trailer past winners ("The Moon", "Three Nights Ago", "47 Seconds"). Their shared language: slow
moody build, italic lower-third lines, gold serif title cards on deep red with case-file text,
accelerating montage, cut to silence, title reveal.

## Assets
- Footage: Filmsupply clips from https://www.filmsupply.com/clips (user: "this is the only starter
  kit I got"). Only the public **watermarked 484p previews** are downloadable without a license, so
  this cut is a draft/animatic; swap in licensed masters with the same file names in `media/raw/`.
  Clip refs are in `media/CREDITS.md`.
- Music: "Silent Descent" (Mixkit, free license), from 0:26.
- SFX: Mixkit / HyperFrames library hits reused from `dlf-cyber-city-recut`.
- Narration: Kokoro-82M (free, open-source, Apache-2.0; runs locally via `hyperframes tts`), voice
  `am_michael`, pitched down ~8% with low-end EQ for a deep trailer read. Script: `build/vo-script.json`.
  (Microsoft Edge TTS was the first choice but needs a WebSocket, which the cloud proxy blocks.)

## Customizations
- Voiceover (user, follow-up): narrate the story (option A), keep 60s, deep male voice, English,
  with captions. Captions sit in the lower letterbox bar, words lighting up as spoken; they replace
  the earlier italic lower-third lines. Music ducks to ~35% under each narration line.

## Notes
- Story, title ("The Lost Hour") and on-screen copy were written to fit the available clips.
- Rebuild: `bash build/preprocess.sh` → `python3 build/make-vo.py` → `node build/build.mjs` → `npx hyperframes render -o renders/the-lost-hour.mp4`.
- Edit list: `build/edl.json` — [clip, source in, timeline start, duration, gamma].
