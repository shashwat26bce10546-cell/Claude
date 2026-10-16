---
workflow: general-video
flow: automation
storyboard: no
message: "The Mary Celeste: a ship found drifting with everyone gone"
aspect: "9:16 (matches the source clips)"
language: en
length: "40.4s (follows the voiceover)"
---

## Notes
- Clip numbering corrected against the voiceover: final order 6, 2, 3, 4, 5, 1, 7, 8 (clips 1 and 6 were swapped).
- No script file was in the Drive folder; the voiceover transcript (ElevenLabs Scribe, build/words.json) is the script.
- Same case-file style as videos/db-cooper-mystery. No music. SFX: bundled library (Pixabay license).
- Rebuild: `bash build/preprocess.sh` → `node build/build.mjs` → `npx hyperframes render`.
