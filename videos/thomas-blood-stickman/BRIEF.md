---
workflow: general-video
flow: automation
storyboard: no
message: "Thomas Blood: the man who stole the Crown Jewels and was pardoned for it"
aspect: "9:16"
language: "English VO (ElevenLabs 'Drew'), English captions"
length: "70.2s (the voiceover, sped up 1.12x)"
---

## Notes
- 15 stickman clips + the voiceover came from the user's Drive folder; the 15-scene script was pasted
  in chat. Each clip's artwork matches its scene, so the numbering is correct and they play 1 -> 15.
- Scene starts come from a local Whisper large-v3 transcript (no ElevenLabs credits used);
  build/words.json holds the word timings.
- The delivered read was slower than the artwork's own animation, so the voiceover is sped up 1.12x
  (atempo, pitch unchanged) and every clip plays at its natural speed (capped at 1.08x). When a line
  still runs longer than one pass of the clip, the clip plays again with a 0.5s crossfade.
  build/words.json holds the word timings divided by that same 1.12.
  The stretch uses frame blending, not motion-compensated interpolation (mci warps flat cartoon art).
- The sparkle watermark sits in the bottom-right below y=1080 of the 720x1280 source, so each clip is
  reframed to its top 1080 rows (1.17x push-in).
- Style per the user: same as the Frank Abagnale reel — minimal, captions carry it, with a card only
  on the beats the artwork does not already letter (PRIEST DISGUISE, A NEPHEW who did not exist,
  CROWN · ORB · SCEPTRE, PARDONED and given land). 1671, COLONEL BLOOD, NERVE!, MAY 9 and
  WHY DID THE KING FORGIVE HIM? are in the art. The ending is the artwork's own question.
- Music: original synthesized score (build/music.py) - sparser through the break-in and the arrest,
  brightest on the pardon. SFX: a few whooshes on the harder cuts, pops/clicks on cards, one sparkle.
- Rebuild: `python3 build/preprocess.py` -> `python3 build/music.py` -> `node build/build.mjs`
  -> `npx hyperframes render`.
