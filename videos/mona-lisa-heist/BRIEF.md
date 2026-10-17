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
