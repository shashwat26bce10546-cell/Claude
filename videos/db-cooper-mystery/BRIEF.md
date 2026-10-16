---
workflow: general-video
flow: automation
storyboard: no
message: "The unsolved D.B. Cooper hijacking, told in 67 seconds"
aspect: "9:16 (matches the source clips)"
language: en
length: "67.3s (follows the voiceover)"
---

## Intent
Arrange the user's 15 numbered stick-figure clips in order, synced to their ElevenLabs voiceover,
with captions, motion graphics, transitions and sound effects. Style matched to the mood: playful case-file mystery.

## Customizations
- Voiceover: user-supplied ElevenLabs "Drew" read, mastered to -15 LUFS.
- Word timing: ElevenLabs Scribe transcript (build/words.json); clip order follows STORYBOARD.jpg.
- Music: none (user choice). SFX: bundled HyperFrames library (Pixabay license, assets/sfx/CREDITS.md).
- Clips: 4s each, slowed up to 1.3x then held on the last frame to fit each line; upscaled 720p -> 1080x1920.

## Notes
- Rebuild: `bash build/preprocess.sh` → `node build/build.mjs` → `npx hyperframes render`.
