// Generates index.html from build/edl.json plus the card / line / sound plan below.
// Rebuild: bash build/preprocess.sh && node build/build.mjs
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const edl = JSON.parse(fs.readFileSync(path.join(root, "build/edl.json"), "utf8"));
const D = edl.duration;
const r3 = (n) => Math.round(n * 1000) / 1000;

// Act 1 dips through black between shots; act 3 hard-cuts with flash frames.
const SLOW_UNTIL = 43.5;

// Title cards: yellow serif on dark red, case-file text around them.
const cards = [
  { start: 15.0, dur: 2.0, title: "AT 3:17 A.M.", top: "HOLLOW CREEK SHERIFF'S DEPT.", bottom: "CASE FILE 10-09 · STATEMENT 01" },
  { start: 21.0, dur: 2.0, title: "EVERY CLOCK STOPPED", top: "INCIDENT DURATION", bottom: "60 MINUTES · 412 RESIDENTS" },
  { start: 33.0, dur: 1.5, title: "SOMETHING CAME BACK", top: "", bottom: "" },
  { start: 40.0, dur: 1.5, title: "NO ONE REMEMBERS", top: "", bottom: "" },
];

// Lower-third lines (italic serif), like the reference trailers.
const lines = [
  { start: 6.4, dur: 2.4, text: "It started with the quiet." },
  { start: 9.5, dur: 2.8, text: "Then came the light." },
  { start: 12.9, dur: 2.0, text: "Every night. Same hour." },
  { start: 25.8, dur: 2.0, text: "For one hour, the whole town was gone." },
  { start: 31.2, dur: 1.7, text: "And when it came back..." },
  { start: 41.7, dur: 1.7, text: "Where were you?" },
];

const sfx = [
  ["impact-bass-2", 2.5, 0.55],
  ["deepImpact", 15.0, 0.9],
  ...[17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 20.5].map((t) => ["clickClassic", t, 0.45]),
  ["trailerHit", 21.0, 0.85],
  ["glitch-1", 28.0, 0.35],
  ["trailerHit", 33.0, 0.8],
  ["hitShort", 36.0, 0.5],
  ["trailerHit", 40.0, 0.85],
  ["riser", 41.5, 0.55, 2.0],
  ["whooshImpact", 43.4, 0.8],
  ["zoomHit", 47.1, 0.6],
  ["hitShort", 49.2, 0.7],
  ["zoomHit", 50.5, 0.6],
  ["epicHit", 55.0, 1.0],
  ["trailerHit", 56.6, 1.0],
];
const sfxLen = { "impact-bass-2": 2.592, deepImpact: 1.75, clickClassic: 0.339, trailerHit: 2.507, "glitch-1": 2.638,
  hitShort: 0.966, riser: 10.03, whooshImpact: 2.638, zoomHit: 0.94, epicHit: 3.317 };

const flashes = [43.5, 47.1, 49.2, 50.5, 55.0];

const shotHtml = [];
const shotJs = [];
edl.shots.forEach(([clip, , start, dur], i) => {
  const id = `s${i}`;
  shotHtml.push(`      <div class="shot" id="${id}-wrap"><div class="push" id="${id}-push">
        <video id="${id}" class="clip" src="media/shots/${String(i).padStart(2, "0")}-${clip}.mp4" muted playsinline
          data-start="${start}" data-duration="${dur}" data-media-start="0" data-track-index="0"></video>
      </div></div>`);
  const slow = start < SLOW_UNTIL || start >= 55;
  const zoom = slow ? 0.07 : 0.035;
  shotJs.push(`tl.fromTo("#${id}-push", { scale: 1 }, { scale: ${1 + zoom}, duration: ${dur}, ease: "none" }, ${start});`);
  if (slow) {
    const f = Math.min(0.35, dur / 4);
    shotJs.push(`tl.fromTo("#${id}-push", { opacity: 0 }, { opacity: 1, duration: ${f}, ease: "power1.out" }, ${start});`);
    shotJs.push(`tl.to("#${id}-push", { opacity: 0, duration: ${f}, ease: "power1.in" }, ${r3(start + dur - f)});`);
  }
});

const cardHtml = cards.map((c, i) => `      <div class="card clip" id="c${i}" data-start="${c.start}" data-duration="${c.dur}" data-track-index="2">
        <div class="card-in" id="c${i}-in">
          ${c.top ? `<div class="doc doc-top">${c.top}</div>` : ""}
          <div class="card-title">${c.title}</div>
          ${c.bottom ? `<div class="doc doc-bottom">${c.bottom}</div>` : ""}
        </div>
      </div>`);
const cardJs = cards.map((c, i) => [
  `tl.fromTo("#c${i}-in", { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: 0.3, ease: "power2.out" }, ${c.start});`,
  `tl.to("#c${i}-in", { scale: 1.03, duration: ${r3(c.dur - 0.3)}, ease: "none" }, ${r3(c.start + 0.3)});`,
  `tl.to("#c${i}-in", { opacity: 0, duration: 0.2, ease: "power1.in" }, ${r3(c.start + c.dur - 0.2)});`,
].join("\n"));

const lineHtml = lines.map((l, i) => `      <div class="line clip" id="l${i}" data-start="${l.start}" data-duration="${l.dur}" data-track-index="3"><span id="l${i}-t">${l.text}</span></div>`);
const lineJs = lines.map((l, i) => [
  `tl.fromTo("#l${i}-t", { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }, ${l.start});`,
  `tl.to("#l${i}-t", { opacity: 0, duration: 0.3, ease: "power1.in" }, ${r3(l.start + l.dur - 0.3)});`,
].join("\n"));

const flashJs = flashes.map((t) =>
  `tl.fromTo("#flash", { opacity: 0.85 }, { opacity: 0, duration: 0.12, ease: "power1.out", immediateRender: false }, ${t});`);

const vol = (v, len, fadeIn = 0, fadeOut = 0.08) => JSON.stringify({ version: 1, lanes: [{ target: "volume", points: [
  { t: 0, v: fadeIn ? 0 : v }, ...(fadeIn ? [{ t: fadeIn, v }] : []), { t: r3(len - fadeOut), v }, { t: r3(len), v: 0 }] }] });
const musicLen = 54.2;
const audioHtml = [
  `      <audio id="music" src="assets/music/silent-descent.mp3" data-start="0" data-duration="${musicLen}" data-media-start="${edl.musicOffset}" data-track-index="10" data-volume="1" data-automation='${vol(0.9, musicLen, 1.5, 0.12)}'></audio>`,
  ...sfx.map(([name, t, v, len], i) => {
    const L = r3(Math.min(len ?? sfxLen[name], D - t));
    return `      <audio id="fx${i}" src="assets/sfx/${name}.mp3" data-start="${t}" data-duration="${L}" data-track-index="${11 + (i % 4)}" data-volume="1" data-automation='${vol(v, L, 0, Math.min(0.3, L / 4))}'></audio>`;
  }),
];

const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>The Lost Hour — Trailer</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Cinzel"; font-weight: 700; src: url("assets/fonts/cinzel-latin-700-normal.woff2") format("woff2"); }
      @font-face { font-family: "Cinzel"; font-weight: 900; src: url("assets/fonts/cinzel-latin-900-normal.woff2") format("woff2"); }
      @font-face { font-family: "Courier Prime"; font-weight: 400; src: url("assets/fonts/courier-prime-latin-400-normal.woff2") format("woff2"); }
      @font-face { font-family: "EB Garamond"; font-style: italic; font-weight: 400; src: url("assets/fonts/eb-garamond-latin-400-italic.woff2") format("woff2"); }
      :root { --gold: #F2C230; --red: #3B0707; --red-hi: #6E0F0B; }
      body { margin: 0; background: #000; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }
      .shot, .card, #title-card, #whisper { position: absolute; left: 0; right: 0; top: 138px; height: 804px; overflow: hidden; }
      .push { position: absolute; inset: 0; transform-origin: 50% 50%; }
      .shot video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      .card, #title-card { z-index: 20; background: radial-gradient(ellipse at 50% 50%, var(--red-hi) 0%, var(--red) 55%, #120101 100%); }
      .card-in, .title-in { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 34px; }
      .card-title { font-family: "Cinzel"; font-weight: 900; font-size: 104px; letter-spacing: 6px; color: var(--gold);
        text-shadow: 0 0 40px rgba(242,194,48,.25); text-align: center; }
      .doc { font-family: "Courier Prime"; font-size: 24px; letter-spacing: 6px; color: rgba(242,194,48,.75); text-transform: uppercase; }
      .line { position: absolute; left: 0; right: 0; top: 800px; height: 90px; z-index: 30;
        display: flex; align-items: center; justify-content: center; }
      .line span { display: block; font-family: "EB Garamond"; font-style: italic; font-size: 46px; color: #f3ead2;
        text-shadow: 0 2px 14px rgba(0,0,0,.9); }
      #whisper { z-index: 25; display: flex; align-items: center; justify-content: center; }
      #whisper span { display: block; font-family: "Courier Prime"; font-size: 38px; letter-spacing: 10px; color: var(--gold); }
      .t-main { font-family: "Cinzel"; font-weight: 900; font-size: 168px; letter-spacing: 14px; color: var(--gold); text-shadow: 0 0 60px rgba(242,194,48,.3); }
      .t-tag { font-family: "Courier Prime"; font-size: 30px; letter-spacing: 12px; color: rgba(242,194,48,.85); }
      .t-soon { font-family: "Cinzel"; font-weight: 700; font-size: 44px; letter-spacing: 18px; color: #f3ead2; }
      .bar { position: absolute; left: 0; right: 0; height: 138px; background: #000; z-index: 50; }
      #bar-top { top: 0; } #bar-bot { bottom: 0; }
      #flash { position: absolute; left: 0; right: 0; top: 138px; height: 804px; background: #fff; opacity: 0; z-index: 40; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="${D}">
${shotHtml.join("\n")}
${cardHtml.join("\n")}
${lineHtml.join("\n")}
      <div id="whisper" class="clip" data-start="54.25" data-duration="0.75" data-track-index="4"><span id="whisper-t">3:16 A.M.</span></div>
      <div id="title-card" class="clip" data-start="56.6" data-duration="${r3(D - 56.6)}" data-track-index="2">
        <div class="title-in" id="title-in">
          <div class="t-tag" id="t-tag">ONE HOUR. NO MEMORY.</div>
          <div class="t-main" id="t-main">THE LOST HOUR</div>
          <div class="t-soon" id="t-soon">COMING SOON</div>
        </div>
      </div>
      <div id="flash"></div>
      <div class="bar" id="bar-top"></div>
      <div class="bar" id="bar-bot"></div>
${audioHtml.join("\n")}
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
${[...shotJs, ...cardJs, ...lineJs, ...flashJs].map((s) => "      " + s.replace(/\n/g, "\n      ")).join("\n")}
      tl.fromTo("#whisper-t", { opacity: 0 }, { opacity: 1, duration: 0.2 }, 54.25);
      tl.to("#whisper-t", { opacity: 0, duration: 0.15 }, 54.85);
      tl.fromTo("#t-main", { opacity: 0, scale: 1.18 }, { opacity: 1, scale: 1, duration: 0.6, ease: "expo.out" }, 56.6);
      tl.fromTo("#t-tag", { opacity: 0 }, { opacity: 1, duration: 0.5 }, 57.0);
      tl.fromTo("#t-soon", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }, 58.0);
      tl.to("#title-in", { scale: 1.03, duration: ${r3(D - 56.6)}, ease: "none" }, 56.6);
      tl.to("#title-in", { opacity: 0, duration: 0.4 }, ${r3(D - 0.4)});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
`;
fs.writeFileSync(path.join(root, "index.html"), html);
console.log("wrote index.html");
