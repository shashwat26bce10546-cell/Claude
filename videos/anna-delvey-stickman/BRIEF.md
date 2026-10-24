---
workflow: general-video
flow: automation
storyboard: no
message: "Anna Delvey: the fake German heiress who talked New York into millions"
aspect: "9:16"
language: "English VO (ElevenLabs 'Drew'), English captions"
length: "60.2s (follows the voiceover)"
---

## Notes
- 15 stickman clips + the voiceover came from the user's Drive folder; the 15-line script was in chat.
  The folder's files were mostly generator names, not scene numbers (only 3 and 14 were numbered), so
  CLIPS in build/preprocess.py maps each file to its narration line by what the artwork shows.
  The generation order is NOT the scene order.
- Scene starts come from a local Whisper large-v3 transcript (no ElevenLabs credits used).
- Framing: the FULL frame is kept, no crop and no push-in. The sparkle watermark is erased in place -
  its alpha is measured per clip from the footage itself, un-composited frame by frame, edge feathered.
- Timing: the read already fits the clips, so the voiceover is untouched. Each clip plays once, slowed
  at most 1.6x (most near 1.1x), blended rather than motion-interpolated. No repeats, no held frames.
- Style: same as the other stickman reels - minimal, captions carry it, with a card only on the beats
  the artwork does not already letter (ANNA DELVEY / the name was fake, GRAND LARCENY, 4 TO 12 YEARS,
  "INVENTING ANNA"). EUR 60 MILLION, ANNA SOROKIN, ART CLUB, HOTEL, PROSECUTORS SAID, FORGED,
  $22M/$25M NO, $35,400 UNPAID, 2017, NO CRIME MEANT, APRIL 2019 GUILTY, 2021, 2022 and the closing
  question are all in the art. The ending is the artwork's own question.
- Music: original synthesized score (build/music.py) - brightest over the designer-clothes and hotel
  beats, sparser through the unpaid bill, the arrest and the trial.
- Rebuild: `python3 build/preprocess.py` -> `python3 build/music.py` -> `node build/build.mjs`
  -> `npx hyperframes render`.
