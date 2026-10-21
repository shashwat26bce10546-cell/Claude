---
workflow: general-video
flow: automation
storyboard: no
message: "Thomas Blood: the man who stole the Crown Jewels and was pardoned for it"
aspect: "9:16"
language: "English VO (ElevenLabs 'Drew'), English captions"
length: "64.3s (the voiceover, sped up 1.22x)"
---

## Notes
- 15 stickman clips + the voiceover came from the user's Drive folder; the 15-scene script was pasted
  in chat. Each clip's artwork matches its scene, so the numbering is correct and they play 1 -> 15.
- Scene starts come from a local Whisper large-v3 transcript (no ElevenLabs credits used);
  build/words.json holds the word timings.
- The voiceover is sped up 1.22x (atempo, pitch unchanged) so the clips barely have to stretch; each
  clip then plays ONCE, slowed at most 1.65x (average 1.23x). No repeated passes and no held frames —
  the user disliked both. build/words.json holds the word timings divided by that same 1.22.
- No push-in on the artwork either: scenes sit still (a flat 2% scale only keeps the whip/zoom cuts
  from showing an edge).
  The stretch uses frame blending, not motion-compensated interpolation (mci warps flat cartoon art).
- The FULL frame is kept (no crop). The sparkle watermark is erased in place instead: it is a fixed
  semi-transparent star, so build/preprocess.py measures its alpha per clip from the footage itself
  (the mark is the one thing that holds still while the art moves), un-composites it frame by frame
  and feathers the edge. The measured maps are cached in build/watermark-alpha.npy. Over flat art it
  is invisible; on one or two clips where the mark sat on a dark character a faint trace remains.
- Style per the user: same as the Frank Abagnale reel — minimal, captions carry it, with a card only
  on the beats the artwork does not already letter (PRIEST DISGUISE, A NEPHEW who did not exist,
  CROWN · ORB · SCEPTRE, PARDONED and given land). 1671, COLONEL BLOOD, NERVE!, MAY 9 and
  WHY DID THE KING FORGIVE HIM? are in the art. The ending is the artwork's own question.
- Music: original synthesized score (build/music.py) - sparser through the break-in and the arrest,
  brightest on the pardon. SFX: a few whooshes on the harder cuts, pops/clicks on cards, one sparkle.
- Rebuild: `python3 build/preprocess.py` -> `python3 build/music.py` -> `node build/build.mjs`
  -> `npx hyperframes render`.
