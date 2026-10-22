---
workflow: general-video
flow: automation
storyboard: no
message: "Rezang La, 1962: 120 men of 13 Kumaon hold a 16,000ft ridge above Chushul"
aspect: "9:16"
language: "Hindi VO (Rahul), Hinglish (Roman) captions"
length: "59.6s (follows the voiceover)"
---

## Notes
- 15 clips + the Hindi voiceover came from the user's Drive folder, with the 15-line script in chat.
  Each clip's artwork matches its line, so the numbering is correct and they play 1 -> 15.
- Scene starts come from a local Whisper large-v3 transcript (no ElevenLabs credits used).
  build/words.py maps each Hindi word to its Roman caption spelling, drops three phrases Whisper
  emitted twice, and fixes "saat" (seven) vs "saath" (with).
- Framing per the user: the FULL frame is kept, with no crop and no push-in. The sparkle watermark is
  erased in place instead - build/preprocess.py measures its alpha per clip (the mark is the one thing
  that holds still while the art moves), un-composites it frame by frame and feathers the edge.
- Timing: the read already fits the clips, so the voiceover is untouched. Each clip plays once, slowed
  at most 1.6x (most near 1.1x), blended rather than motion-interpolated. No repeats, no held frames.
- Style per the user: epic but few graphics - an opening title (LADAKH · 1962 / REZANG LA / 120 JAWAAN)
  and a closing card (114 SHAHEED / PARAM VIR CHAKRA), a cold tint over the cold-and-no-artillery line,
  a red wash on the 18 November attack and the seven assaults, and 5 deep impacts. Captions carry the rest.
- Music: original synthesized score (build/music.sh), minor -> major for the final line.
- Rebuild: `python3 build/preprocess.py` -> `bash build/music.sh` -> `python3 build/words.py`
  -> `node build/build.mjs` -> `npx hyperframes render`.
