---
workflow: general-video
flow: automation
storyboard: no
message: "The rise and fall of the Maurya Empire in 60 seconds"
aspect: "9:16"
language: hinglish
length: "58.6s (max 60s)"
---

## Intent
Full 60s Reel from the user's 10 AI clips + script (SCRIPT.md): ElevenLabs Hinglish voiceover,
motion graphics, sound effects, music, pacing, captions, quality enhancement, transitions.

## Customizations
- Voice: ElevenLabs "Rahul - Punchy Energetic Storyteller" (eleven_v4), energetic Indian male, Hinglish. Clip audio replaced.
- Word timing: ElevenLabs Scribe transcript of the voiceover (build/words.json).
- Music: original score synthesized with FFmpeg (build/music.sh) — free/royalty-free sites are unreachable from this environment.
- SFX: bundled HyperFrames library (Pixabay license, see assets/sfx/CREDITS.md).
- Clips: retimed to each narration line (motion-interpolated slow-mo or trim), upscaled 720p -> 1080x1920, sharpened, warm grade (build/preprocess.sh).

## Notes
- Script facts marked [VERIFY] in SCRIPT.md (dates are approximate, "lagbhag") — check before posting.
- Rebuild: `bash build/preprocess.sh` → `bash build/music.sh` → `node build/build.mjs` → `npx hyperframes render`.
