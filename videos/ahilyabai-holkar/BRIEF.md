---
workflow: general-video
flow: automation
storyboard: no
message: "Ahilyabai Holkar: the village girl who became Malwa's 'Maa'"
aspect: "9:16"
language: "Hindi VO (Rahul), Hinglish (Roman) captions"
length: "61.4s (follows the voiceover)"
---

## Notes
- 15 clips + voiceover from the user's Drive folder; the user's 15-scene script was pasted in chat.
  Clip numbering matched the script, so clips play 1→15 in order, each fitted to its narration line
  (slowed up to 1.3x with motion interpolation, then held) in build/preprocess.py.
- The Gemini sparkle watermark orbits the bottom-right corner, so every clip is reframed to its top
  1080 rows (1.18x) instead of a delogo blur.
- Voiceover transcribed with ElevenLabs Scribe; build/words.json holds the Hinglish caption words + timings.
- Style follows the Maurya reel: gold Cinzel titles, timeline 1725→1795, name plates, ribbons.
- Music: original synthesized score (build/music.sh), minor → major at Maheshwar (28.3s).
  SFX: only 4 deep impacts (title, 1754 loss, 1767 loss, finale), bundled Pixabay library.
- Rebuild: `python3 build/preprocess.py` → `bash build/music.sh` → `node build/build.mjs` → `npx hyperframes render`.

## Thumbnail
- thumbnail/ahilyabai-holkar-thumbnail.jpg (1080x1920), built from thumbnail/thumbnail.html over a clip 1 frame (bg.jpg).
- Hook: VIDHWA (struck out) -> MAHARANI, "Pati gaya, beta gaya... phir poore Malwa par raj? KAISE?"
