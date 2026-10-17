---
workflow: general-video
flow: automation
storyboard: no
message: "In 1911 the Mona Lisa walked out of the Louvre under a worker's coat"
aspect: "9:16 (matches the source clips)"
language: en
length: "41.4s (follows the voiceover)"
---

## Notes
- Clip numbering checked against the voiceover: all 8 clips were already in the right order (1-8).
- No script file was in the Drive folder; the voiceover transcript (ElevenLabs Scribe, build/words.json) is the script.
- Same case-file series style as db-cooper-mystery and mary-celeste-mystery. No music. SFX: bundled library (Pixabay license).
- Rebuild: `bash build/preprocess.sh` → `node build/build.mjs` → `npx hyperframes render`.

## Revision: real Mona Lisa in every frame
- User supplied the real painting (assets/mona-lisa.png, cropped from their reference photo) and asked that every
  picture frame show it — no empty or fake frames.
- build/compose_mona.py tracks each frame per video frame (gold-border / white-frame detection, temporal smoothing,
  flood-fill of the opening) and composites a softened Mona Lisa (bilateral smoothing + light ink lines).
  Configs per clip: build/mona_configs.json. Output: media/clips-ml/ (preprocess.sh now reads these).
- Clip 1: painting peeks out under the coat (coat/legs stay in front). Clip 3: back of frame kept (user choice).
- Clip 4: painting shown, then vanishes with a "poof" on "the empty wall" (user choice). Clip 5: red X kept on top.
