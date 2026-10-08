# HyperFrames video workspace

This repo is for creating and editing videos with [HyperFrames](https://github.com/heygen-com/hyperframes)
(HTML/CSS/GSAP compositions rendered to deterministic MP4).

## How to work here

- For any video request, start with the `/hyperframes` skill. It routes to the right workflow
  (`/embedded-captions`, `/talking-head-recut`, `/general-video`, `/motion-graphics`,
  `/music-to-video`, `/slideshow`, …). All 21 skills are vendored in `.agents/skills`
  (symlinked into `.claude/skills`, pinned in `skills-lock.json`).
- Put each video project in its own folder under `videos/`:
  `npx hyperframes init videos/<name> --non-interactive`
- Source footage, audio, and rendered MP4s are committed with the project (GitHub rejects
  files over 100 MB, so keep individual files below that).
- CLI loop: `npx hyperframes lint` → `npx hyperframes check` → `npx hyperframes render -o <file>.mp4`
  (run inside the project folder). `npm run doctor` checks the environment.

## Cloud sessions: no CDN access

The cloud egress policy blocks `cdn.jsdelivr.net` (and similar CDNs), so compositions that load
GSAP or other libraries from a CDN fail to render with `sub_timeline_script_failure`.
Load libraries from local files instead. GSAP is a dev dependency here:

```bash
mkdir -p videos/<name>/vendor
cp node_modules/gsap/dist/gsap.min.js videos/<name>/vendor/
# in index.html: <script src="vendor/gsap.min.js"></script>
```

Do the same for any other library a composition needs (install it from npm, which is reachable).

## Setup

`.claude/hooks/session-start.sh` runs in cloud sessions: `npm install` (pinned `hyperframes`
CLI + `gsap`) and `hyperframes browser ensure` (Chrome headless shell for rendering). FFmpeg
comes with the container. Optional local tools that are not installed: whisper-cpp
(transcription, needed for caption workflows), Kokoro TTS, and MusicGen.

Update the skills with `npm run skills:update`.
