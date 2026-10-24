---
workflow: general-video
flow: automation
storyboard: no
message: "Lachit Borphukan: a sick general beats the Mughal navy at Saraighat, 1671"
aspect: "9:16"
language: "Hindi VO (Rahul), Hinglish (Roman) captions"
length: "57s (follows the voiceover)"
---

## Notes
- 15 clips + the Hindi voiceover came from the user's Drive folder, with the 15-scene script in chat.
- Two numbering problems are corrected in build/preprocess.py (CLIPS / SRC_IN):
  * clips 6 and 10 are swapped - clip 10 is the heavy Mughal boats with the glowing "weak point" arrow
    (line 6), clip 6 is the Mughal cavalry crossing by boat at dawn (line 10);
  * clip 9 is the same video as clip 15 (the sunset silhouette). Line 9, the close-up on Lachit's face,
    uses the back half of clip 1, which pushes in to that close-up.
- Transcript: Whisper large-v3, locally. The full pass skipped lines 9-12 (~15s), so that stretch was
  re-transcribed on its own and spliced in (build/transcript-merged.json). build/words.py maps the
  Hindi to Roman captions and fixes the ASR's "Mukhal" -> MUGHAL, 1687 -> 1667, "saath" -> SAAT naavon.
- Framing: full frame, no crop, no push-in; the sparkle watermark is erased in place.
- Timing: the read fits the clips, so the voiceover is untouched. Each clip plays once (at most 1.55x).
- Style per the user: same as Rezang La - an opening title (ASSAM · 1671 / LACHIT BORPHUKAN), a closing
  card (24 NOVEMBER / LACHIT DIVAS), a cold tint over the uncle-and-duty beat, a red wash on the
  seven-boat charge and the swarm, 5 deep impacts. Captions carry the rest.
- Music: original synthesized score (build/music.sh), minor -> major for the final line.
- Rebuild: `python3 build/preprocess.py` -> `bash build/music.sh` -> `python3 build/words.py`
  -> `node build/build.mjs` -> `npx hyperframes render`.
