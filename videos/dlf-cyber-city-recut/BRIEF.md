---
workflow: general-video
flow: automation
storyboard: no
message: "Ambrane's corporate sales offer in DLF Cyber City — 60 days, zero risk, pure upside"
aspect: "9:16"
language: hinglish
length: "~54s (trimmed from 61s)"
---

## Intent
Edit a friend's 61s vertical promo: motion graphics, sound effects, tighter pacing, better-looking
captions, quality enhancement and transitions. Keep the content original; make it engaging and professional.

## Customizations
- Captions: original burned-in captions hidden under a feathered blur band; new word-by-word captions on top.
- Audio: SFX from the bundled HyperFrames library (Pixabay license); no music bed (none available offline).
- Pacing: dead air trimmed (14 cuts), every word kept; punch-ins hide jump cuts.
- Review: just build it.

## Notes
- Transcript recovered by OCR of the original burned-in captions (no speech model reachable).
- Rebuild: `bash build/preprocess.sh` (footage) → `node build/build.mjs` (index.html) → `npx hyperframes render`.
