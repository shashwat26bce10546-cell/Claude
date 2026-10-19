---
workflow: general-video
flow: automation
storyboard: no
message: "Frank Abagnale: the teenager who fooled airlines, banks and the FBI"
aspect: "9:16"
language: "English VO (ElevenLabs 'Drew'), English captions"
length: "59s (follows the voiceover)"
---

## Notes
- 15 stickman clips + the voiceover came from the user's Drive folder; the 15-scene script was pasted
  in chat. Each clip's artwork matches its scene, so the numbering is correct and they play 1 -> 15.
- The delivered voiceover is a tightened version of the script (same 15 beats, shorter wording).
  Scene starts in build/preprocess.py come from its Scribe word timings; build/words.json holds the words.
- Each clip is retimed to its narration line (0.84x-1.35x, motion-interpolated when slowed, then held).
- The Gemini sparkle watermark orbits the bottom-right below y=1095 of the 720x1280 source. A delogo
  blur smeared the flat artwork, so each clip is reframed to its top 1080 rows (1.17x push-in) instead.
- Style per the user: minimal — captions carry the video, with a card only on the key beats
  (AGE 16, FRANK ABAGNALE, PILOT, DOCTOR, LAWYER, 1969 - FRANCE, 5 YEARS). The money total and the
  closing "GENIUS OR FRAUD?" are already lettered into the artwork, so no card duplicates them.
- Music: original synthesized score (build/music.py) - plucked arpeggio, soft kick, sparser through
  the chase and prison scenes. SFX: a few only (whooshes on whip/zoom cuts, pops on cards, one sparkle).
- Rebuild: `python3 build/preprocess.py` -> `python3 build/music.py` -> `node build/build.mjs` -> `npx hyperframes render`.
