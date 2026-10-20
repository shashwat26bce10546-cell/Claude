---
workflow: general-video
flow: automation
storyboard: no
message: "Saragarhi, 1897: 21 soldiers hold a signal post against thousands"
aspect: "9:16"
language: "Hindi VO (Rahul), Hinglish (Roman) captions"
length: "49s (follows the voiceover)"
---

## Notes
- 15 clips + the Hindi voiceover came from the user's Drive folder; no script. The voiceover is the
  script: transcribed locally with Whisper large-v3 (no ElevenLabs credits used). build/words.py maps
  each Hindi word to its Roman caption spelling and drops a phrase Whisper emitted twice.
- Clip order is the user's, with three corrections in build/preprocess.py:
  * clip 3 (the signal beam between the two hill forts) covers two narration lines, so it runs long;
  * clip 9 (the two Afridi/Orakzai chiefs) moved ahead of the charge in clip 5, to the line naming them;
  * clip 7 is a three-panel collage for its whole length, never a full-frame shot, so it is unused;
    the "madad door thi" line uses clip 2's distant dawn ridge from 1.5s in instead.
- Segments shorter than the 4.01s source are trimmed rather than sped up; longer ones are slowed with
  motion interpolation and held. Watermark removed by reframing each clip to its top 1080 rows.
- Style per the user: epic look but few graphics — an opening title and a closing card only, plus a
  red wash on the charge and the breach and a cold tint for the silence. Captions carry the rest.
- Music: original synthesized score (build/music.sh), minor -> major for the final line.
- The folder's soldier JPG is untouched and unused, per the user.
- Rebuild: `python3 build/preprocess.py` -> `bash build/music.sh` -> `python3 build/words.py`
  -> `node build/build.mjs` -> `npx hyperframes render`.
