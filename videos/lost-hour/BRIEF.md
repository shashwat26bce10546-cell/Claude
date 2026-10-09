---
workflow: general-video
flow: automation
storyboard: no
message: "A small town loses one hour every night at 3:17 A.M. — and something comes back with it"
aspect: "16:9 (2.39:1 scope letterbox)"
length: "60s"
destination: "Filmsupply Editfest 2026 — Movie Trailer category"
---

## Intent
Rebuilt after feedback ("I cannot predict the story… make it look like an actual trailer"; the
"3:16" line was buried and the ending felt incomplete). Story A: one father, one missing son.
Logline: "Every child in Hollow Creek came home after the lost hour. Except one."
Structure: warm memories + father's promise (0–10s) → 3:16→3:17 clock, the town loses an hour
(11–18s) → every child came home / EXCEPT ONE (18–24s) → missing poster, police, sheriff
suspects the father, search party (24–37s) → phone call from the boy (37–43s) → montage with
THE CLOCKS / WILL STOP / AGAIN (43–53.5s) → heartbeat silence → title → stinger twist
("Dad. Why did you leave me there?").

## Assets
- Footage: watermarked Filmsupply previews (draft); refs in `media/CREDITS.md`.
- Voices (all free, local). Adults: Chatterbox (Resemble AI, MIT) cloning public-domain LibriVox
  performances so the delivery carries real emotion (`build/voice-refs/SOURCES.md`) — narrator from
  the Creature, father from Victor Frankenstein (tender / grieving / desperate), sheriff from
  Mr. Kirwin. Boy: Kokoro-82M af_nicole pitched up (phone-filtered / whispered).
  Script, chosen seeds and emotion settings: `build/vo-script.json`.
- Music: "Silent Descent" (Mixkit). SFX: Mixkit (phone ring, clock tick, heartbeat, horror
  drums) + HyperFrames library hits. Clock font: DSEG7 (OFL).

## Customizations
- 60s, narrator + character lines, English, captions in the lower letterbox bar (boy in italic blue).

## Notes
- Voice feedback: "Mr. Harper's voice has no emotion" → adults re-voiced with Chatterbox, 2–3 takes
  per line, picked after a speech-to-text check; middle section retimed to the new line lengths.
- Rebuild: `bash build/preprocess.sh` → `CHATTERBOX_PY=<venv python> python3 build/make-vo.py` → `node build/build.mjs` →
  `npx hyperframes render -o renders/the-lost-hour.mp4`.
