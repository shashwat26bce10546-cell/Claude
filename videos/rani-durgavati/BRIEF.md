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

## Revision 2
- Opening now clip 1 (queen on her elephant, slow motion) with the title over the sky, Maurya-style; clip 8 removed entirely.
- Second half: clip 1 (army surge) → clip 7 (charge) → clip 9 (sunset, darkening, 39.1–46.4s) → clip 5 statue (Balidaan) → clip 10.
- Sound effects cut to 4 deep impacts (title, 1564 attack, Balidaan, finale); score + voiceover unchanged.
