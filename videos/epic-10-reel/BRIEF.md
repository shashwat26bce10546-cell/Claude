---
workflow: general-video
flow: automation
storyboard: no
message: "Agra 1666: Shivaji walks out of Aurangzeb's captivity in a basket of sweets"
aspect: "9:16"
language: "Hindi VO (Rahul), Hinglish (Roman) captions"
length: "45.6s (follows the voiceover)"
---

## Notes
- 10 clips + the Hindi voiceover came from the user's Drive folder; no script. The voiceover itself is
  the script: the clips follow it beat for beat in order 1 -> 10, so the numbering is correct.
- ElevenLabs credits ran out mid-project, so the transcript comes from Whisper large-v3 run locally
  (the model is fetched through the session proxy into ~/.cache/hyperframes/whisper/models).
  build/words.py maps each Hindi word to its Roman caption spelling, fixing the ASR's mis-hearings.
- Each clip is retimed to its narration line (0.74x-2.16x, motion-interpolated when slowed, then held).
- The generator's sparkle watermark orbits the bottom-right below y=1080 of the 720x1280 source, so
  each clip is reframed to its top 1080 rows (1.17x push-in) rather than blurred.
- Style follows the Rani Durgavati reel: gold Cinzel titles, ribbons, red chips for the tense beats,
  cold tint through the escape, and only 7 deep impacts (no small SFX).
- Music: original synthesized score (build/music.sh), D minor -> D major at the empty bed / sunrise.
- The folder's silhouette JPG is unused, per the user.
- Rebuild: `python3 build/preprocess.py` -> `bash build/music.sh` -> `python3 build/words.py`
  -> `node build/build.mjs` -> `npx hyperframes render`.
