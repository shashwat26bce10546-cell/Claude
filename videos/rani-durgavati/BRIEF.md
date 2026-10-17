---
workflow: general-video
flow: automation
storyboard: no
message: "Rani Durgavati: the Gond queen who never bowed to the Mughals"
aspect: "9:16"
language: "Hindi VO, Hinglish (Roman) captions"
length: "56.6s (follows the voiceover)"
---

## Notes
- No script file in the Drive folder; the Hindi voiceover transcript (ElevenLabs Scribe) is the script.
  build/words.json holds each word with its Devanagari original and Roman (Hinglish) caption text.
- Clip numbering did not follow the story; corrected sequence lives in build/preprocess.py (SEG):
  8a, 2, 3, 4, 5a (prosperity), 7b (fort), 6, 1, 7a (battle), 9, 8b (sacrifice, darker), 5b (statue), 10.
  Clips 5 and 7 each contain two shots joined by a dissolve; only the clean parts are used.
  Clip 8 is a square shot padded inside 9:16; shown full-width over a blurred copy so the face is visible.
- Music: original synthesized score (build/music.sh). SFX: bundled library (Pixabay license).
- Rebuild: `python3 build/preprocess.py` → `bash build/music.sh` → `node build/build.mjs` → `npx hyperframes render`.
