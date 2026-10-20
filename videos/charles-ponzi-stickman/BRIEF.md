---
workflow: general-video
flow: automation
storyboard: no
message: "Charles Ponzi: the postal-coupon idea that became the scheme named after him"
aspect: "9:16"
language: "English VO (ElevenLabs 'Drew'), English captions"
length: "82.3s (follows the voiceover)"
---

## Notes
- 15 stickman clips + the voiceover came from the user's Drive folder; the 15-scene script was pasted
  in chat. Each clip's artwork matches its scene, so the numbering is correct and they play 1 -> 15.
- The voiceover matches the script almost word for word. Scene starts come from a local Whisper
  large-v3 transcript (ElevenLabs credits are exhausted); build/words.json holds the word timings.
- Each clip is slowed at most 1.3x to fit its narration line; when the line runs longer than one
  pass of the clip, the clip plays again with a 0.5s crossfade. Earlier versions stretched single
  clips up to 1.96x, which looked sluggish, and held frames, which read as a freeze.
- The stretch uses frame BLENDING, not motion-compensated interpolation: mci guessed motion badly on
  flat cartoon art, warping moving props and leaving an uneven cadence that read as stutter.
- The generator's sparkle watermark sits in the bottom-right below y=1080 of the 720x1280 source, so
  each clip is reframed to its top 1080 rows (1.17x push-in) rather than blurred.
- Style matches the Frank Abagnale reel: minimal, captions carry it, and a card only on the beats the
  artwork does not already letter (POSTAL COUPON, TOO MUCH PAPERWORK, $1,000s A DAY, AUDITORS).
  1920, CHARLES PONZI, 50% BACK, PONZI & CO., NEW/OLD, HOW?, CLOSED, PONZI SCHEME and
  WOULD YOU INVEST? are in the art, so nothing repeats them. The ending is the artwork's own question.
- Music: original synthesized score (build/music.py) - brightest while the money pours in, sparser
  through the collapse. SFX: a few whooshes on the harder cuts, pops/clicks on cards, one sparkle.
- Rebuild: `python3 build/preprocess.py` -> `python3 build/music.py` -> `node build/build.mjs`
  -> `npx hyperframes render`.
