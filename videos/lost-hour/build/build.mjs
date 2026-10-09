// Generates index.html from build/edl.json (picture), build/vo-lines.json (voices) and the
// card / clock / sound plan below.
// Rebuild: bash build/preprocess.sh && python3 build/make-vo.py && node build/build.mjs
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const edl = JSON.parse(fs.readFileSync(path.join(root, "build/edl.json"), "utf8"));
const vo = JSON.parse(fs.readFileSync(path.join(root, "build/vo-lines.json"), "utf8"));
const D = edl.duration;
const r3 = (n) => Math.round(n * 1000) / 1000;

// ---------------------------------------------------------------- plan
// Title cards. "red" = gold serif on deep red (story beats); "black" = punch words in the montage.
const cards = [
  { start: 17.6, dur: 1.4, title: "FOR ONE HOUR", top: "HOLLOW CREEK · OCTOBER 9", bottom: "", style: "red" },
  { start: 24.0, dur: 1.6, title: "EXCEPT ONE", top: "", bottom: "", style: "red" },
  { start: 46.7, dur: 0.6, title: "THE CLOCKS", style: "black" },
  { start: 47.9, dur: 0.6, title: "WILL STOP", style: "black" },
  { start: 49.7, dur: 0.7, title: "AGAIN", style: "black" },
];
// The bedside clock: 3:16 flips to 3:17, then the display dies.
const CLOCK = { start: 11.0, dur: 2.6, flip: 12.3, die: 13.25 };
const TITLE = { start: 54.4, end: 57.3 };

// Lines whose words are already on screen (a card or the title) get no caption.
const NO_CAPTION = new Set(["n2", "n4", "n6"]);
const ITALIC = new Set(["b1", "b2"]); // the boy's voice

const sfx = [
  ["deepImpact", 10.6, 0.6],
  ["clockTick", 11.0, 0.55, 5.6],
  ["hitShort", 12.3, 0.45],
  ["trailerHit", 17.6, 0.8],
  ["horrorDrum", 24.0, 0.9],
  ["impact-bass-2", 28.0, 0.35],
  ["phoneRing", 37.4, 0.8, 2.1],
  ["riser", 41.4, 0.5, 2.1],
  ["whooshImpact", 43.45, 0.8],
  ["zoomHit", 46.7, 0.6],
  ["zoomHit", 47.9, 0.6],
  ["trailerHit", 49.7, 0.85],
  ["hitShort", 51.1, 0.6],
  ["heartbeat", 53.45, 0.85, 1.0],
  ["epicHit", 54.4, 0.75],
  ["horrorHit", 59.72, 1.0, 0.28],
];
const sfxLen = { deepImpact: 1.75, clockTick: 5.64, hitShort: 0.966, trailerHit: 2.507, horrorDrum: 4.344,
  "impact-bass-2": 2.592, phoneRing: 4.224, riser: 10.03, whooshImpact: 2.638, zoomHit: 0.94, heartbeat: 3.432,
  epicHit: 3.317, horrorHit: 4.128 };
const flashes = [43.5, 45.2, 47.3, 49.1, 51.1];

const MUSIC_END = 53.5;
const MUSIC_HI = 0.9, MUSIC_LO = 0.3, RAMP = 0.25;
const VO_PAD = 0.15; // silence padded onto the end of every voice clip

// ---------------------------------------------------------------- picture
const shotHtml = [];
const js = [];
edl.shots.forEach(([clip, , start, dur, , mode], i) => {
  const id = `sh${i}`;
  shotHtml.push(`      <div class="shot" id="${id}-wrap"><div class="push" id="${id}-push">
        <video id="${id}" class="clip" src="media/shots/${String(i).padStart(2, "0")}-${clip}.mp4" muted playsinline
          data-start="${start}" data-duration="${dur}" data-media-start="0" data-track-index="0"></video>
      </div></div>`);
  const soft = mode === "soft";
  js.push(`tl.fromTo("#${id}-push", { scale: 1 }, { scale: ${soft ? 1.07 : 1.04}, duration: ${dur}, ease: "none" }, ${start});`);
  if (soft) {
    const f = Math.min(0.35, dur / 4);
    js.push(`tl.fromTo("#${id}-push", { opacity: 0 }, { opacity: 1, duration: ${f}, ease: "power1.out" }, ${start});`);
    js.push(`tl.to("#${id}-push", { opacity: 0, duration: ${f}, ease: "power1.in" }, ${r3(start + dur - f)});`);
  }
});

const cardHtml = cards.map((c, i) => `      <div class="card card-${c.style} clip" id="c${i}" data-start="${c.start}" data-duration="${c.dur}" data-track-index="2">
        <div class="card-in" id="c${i}-in">${c.top ? `
          <div class="doc">${c.top}</div>` : ""}
          <div class="card-title">${c.title}</div>${c.bottom ? `
          <div class="doc">${c.bottom}</div>` : ""}
        </div>
      </div>`);
cards.forEach((c, i) => {
  if (c.style === "red") {
    js.push(`tl.fromTo("#c${i}-in", { opacity: 0, scale: 0.96 }, { opacity: 1, scale: 1, duration: 0.3, ease: "power2.out" }, ${c.start});`);
    js.push(`tl.to("#c${i}-in", { scale: 1.03, duration: ${r3(c.dur - 0.3)}, ease: "none" }, ${r3(c.start + 0.3)});`);
    js.push(`tl.to("#c${i}-in", { opacity: 0, duration: 0.2, ease: "power1.in" }, ${r3(c.start + c.dur - 0.2)});`);
  } else {
    js.push(`tl.fromTo("#c${i}-in", { scale: 1.25, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.12, ease: "power3.out" }, ${c.start});`);
    js.push(`tl.to("#c${i}-in", { scale: 0.96, duration: ${r3(c.dur - 0.12)}, ease: "none" }, ${r3(c.start + 0.12)});`);
  }
});

const clockHtml = `      <div id="clock" class="clip" data-start="${CLOCK.start}" data-duration="${CLOCK.dur}" data-track-index="2">
        <div class="clock-in" id="clock-in">
          <div class="clock-face">
            <span class="seg ghost">88:88</span>
            <span class="seg lit" id="clock-a">3:16</span>
            <span class="seg lit" id="clock-b">3:17</span>
          </div>
          <div class="clock-am" id="clock-am">AM</div>
        </div>
      </div>`;
js.push(`tl.fromTo("#clock-in", { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "power1.out" }, ${CLOCK.start});`);
js.push(`tl.fromTo("#clock-in", { scale: 1 }, { scale: 1.08, duration: ${CLOCK.dur}, ease: "none" }, ${CLOCK.start});`);
js.push(`tl.fromTo("#clock-b", { opacity: 0 }, { opacity: 1, duration: 0.01 }, ${CLOCK.flip});`);
js.push(`tl.to("#clock-a", { opacity: 0, duration: 0.01 }, ${CLOCK.flip});`);
// flicker, then the display goes dark
[[0, 0.3], [0.08, 1], [0.16, 0.2], [0.22, 0.9], [0.3, 0]].forEach(([dt, v]) =>
  js.push(`tl.to("#clock-b, #clock-am", { opacity: ${v}, duration: 0.03 }, ${r3(CLOCK.die + dt)});`));

const titleHtml = `      <div id="title-card" class="clip" data-start="${TITLE.start}" data-duration="${r3(TITLE.end - TITLE.start)}" data-track-index="2">
        <div class="title-in" id="title-in">
          <div class="t-tag" id="t-tag">ONE HOUR. ONE CHILD. ONE LIE.</div>
          <div class="t-main" id="t-main">THE LOST HOUR</div>
          <div class="t-soon" id="t-soon">COMING SOON</div>
        </div>
      </div>`;
js.push(`tl.fromTo("#t-main", { opacity: 0, scale: 1.18 }, { opacity: 1, scale: 1, duration: 0.6, ease: "expo.out" }, ${TITLE.start});`);
js.push(`tl.fromTo("#t-tag", { opacity: 0 }, { opacity: 1, duration: 0.5 }, ${r3(TITLE.start + 0.5)});`);
js.push(`tl.fromTo("#t-soon", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }, ${r3(TITLE.start + 1.3)});`);
js.push(`tl.to("#title-in", { scale: 1.03, duration: ${r3(TITLE.end - TITLE.start)}, ease: "none" }, ${TITLE.start});`);
js.push(`tl.to("#title-in", { opacity: 0, duration: 0.3 }, ${r3(TITLE.end - 0.3)});`);

flashes.forEach((t) =>
  js.push(`tl.fromTo("#flash", { opacity: 0.85 }, { opacity: 0, duration: 0.12, ease: "power1.out", immediateRender: false }, ${t});`));

// ---------------------------------------------------------------- voices + captions
const lines = Object.entries(vo).map(([id, v]) => ({ id, ...v })).sort((a, b) => a.start - b.start);
const blockers = [...cards.map((c) => c.start), TITLE.start];
const captionEnd = (l) => {
  const end = l.start + l.dur - VO_PAD + 0.3;
  const hit = blockers.find((t) => t > l.start && t < end);
  return Math.min(hit ?? end, D);
};
const caps = lines.filter((l) => !NO_CAPTION.has(l.id));
const capHtml = caps.map((l) => {
  const words = l.text.split(" ").map((w, j) => `<span class="w" id="${l.id}-w${j}">${w}</span>`).join(" ");
  return `      <div class="cap clip" id="${l.id}-cap" data-start="${l.start}" data-duration="${r3(captionEnd(l) - l.start)}" data-track-index="3"><div class="cap-in${ITALIC.has(l.id) ? " cap-boy" : ""}" id="${l.id}-in">${words}</div></div>`;
});
// Words light up in step with the speech, timed by character share of the spoken length.
caps.forEach((l) => {
  const words = l.text.split(" ");
  const spoken = l.dur - VO_PAD;
  const total = words.reduce((n, w) => n + w.length + 1, 0);
  let acc = 0;
  js.push(`tl.fromTo("#${l.id}-in", { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "power1.out" }, ${l.start});`);
  words.forEach((w, j) => {
    js.push(`tl.fromTo("#${l.id}-w${j}", { opacity: 0.35 }, { opacity: 1, duration: 0.15, ease: "none" }, ${r3(l.start + (acc / total) * spoken)});`);
    acc += w.length + 1;
  });
  js.push(`tl.to("#${l.id}-in", { opacity: 0, duration: 0.2, ease: "power1.in" }, ${r3(captionEnd(l) - 0.2)});`);
});

// ---------------------------------------------------------------- audio
const env = (pts) => JSON.stringify({ version: 1, lanes: [{ target: "volume", points: pts }] });
const flat = (v, len, fadeOut) => env([{ t: 0, v }, { t: r3(len - fadeOut), v }, { t: r3(len), v: 0 }]);

// Music: fades in, dips under every voice line, hard-stops at MUSIC_END for the silence beat.
const musicPts = [{ t: 0, v: 0 }, { t: 2.0, v: MUSIC_HI }];
for (const l of lines) {
  if (l.start >= MUSIC_END - 0.3) continue;
  const a = l.start - RAMP, b = l.start + l.dur - VO_PAD;
  const last = musicPts[musicPts.length - 1];
  if (a <= last.t) last.v = MUSIC_LO; else musicPts.push({ t: r3(a), v: MUSIC_HI });
  musicPts.push({ t: r3(Math.max(a + RAMP, last.t + 0.01)), v: MUSIC_LO }, { t: r3(Math.min(b, MUSIC_END - 0.2)), v: MUSIC_LO });
  if (b + RAMP < MUSIC_END - 0.12) musicPts.push({ t: r3(b + RAMP), v: MUSIC_HI });
}
musicPts.push({ t: r3(MUSIC_END - 0.1), v: musicPts[musicPts.length - 1].v }, { t: MUSIC_END, v: 0 });

const audioHtml = [
  `      <audio id="music" src="assets/music/silent-descent.mp3" data-start="0" data-duration="${MUSIC_END}" data-media-start="${edl.musicOffset}" data-track-index="10" data-volume="1" data-automation='${env(musicPts)}'></audio>`,
  ...lines.map((l) => `      <audio id="${l.id}" src="assets/vo/${l.id}.mp3" data-start="${l.start}" data-duration="${l.dur}" data-track-index="9" data-volume="1"></audio>`),
  ...sfx.map(([name, t, v, len], i) => {
    const L = r3(Math.min(len ?? sfxLen[name], sfxLen[name], D - t));
    return `      <audio id="fx${i}" src="assets/sfx/${name}.mp3" data-start="${t}" data-duration="${L}" data-track-index="${11 + (i % 4)}" data-volume="1" data-automation='${flat(v, L, Math.min(0.3, L / 4))}'></audio>`;
  }),
];

// ---------------------------------------------------------------- page
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
      @font-face { font-family: "EB Garamond"; font-weight: 500; src: url("assets/fonts/eb-garamond-latin-500-normal.woff2") format("woff2"); }
      @font-face { font-family: "EB Garamond"; font-style: italic; font-weight: 400; src: url("assets/fonts/eb-garamond-latin-400-italic.woff2") format("woff2"); }
      @font-face { font-family: "DSEG7"; font-weight: 700; src: url("assets/fonts/DSEG7Classic-Bold.woff2") format("woff2"); }
      :root { --gold: #F2C230; --red: #3B0707; --red-hi: #6E0F0B; --led: #ff2a1a; --cream: #f3ead2; }
      body { margin: 0; background: #000; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; }
      .shot, .card, #title-card, #clock { position: absolute; left: 0; right: 0; top: 138px; height: 804px; overflow: hidden; }
      .push { position: absolute; inset: 0; transform-origin: 50% 50%; }
      .shot video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      .card, #title-card, #clock { z-index: 20; }
      .card-red, #title-card { background: radial-gradient(ellipse at 50% 50%, var(--red-hi) 0%, var(--red) 55%, #120101 100%); }
      .card-black { background: #000; }
      .card-in, .title-in, .clock-in { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 34px; }
      .card-title { font-family: "Cinzel"; font-weight: 900; font-size: 112px; letter-spacing: 8px; color: var(--gold);
        text-shadow: 0 0 40px rgba(242,194,48,.25); text-align: center; }
      .card-black .card-title { font-size: 150px; color: var(--cream); text-shadow: 0 0 50px rgba(255,255,255,.18); }
      .doc { font-family: "Courier Prime"; font-size: 26px; letter-spacing: 8px; color: rgba(242,194,48,.8); text-transform: uppercase; }
      #clock { background: radial-gradient(ellipse at 50% 55%, #1a0503 0%, #000 60%); }
      .clock-in { flex-direction: row; gap: 28px; }
      .clock-face { position: relative; width: 760px; height: 260px; }
      .seg { position: absolute; right: 0; top: 0; font-family: "DSEG7"; font-weight: 700; font-size: 220px; line-height: 260px; }
      .ghost { color: rgba(255,42,26,.07); }
      .lit { color: var(--led); text-shadow: 0 0 18px rgba(255,42,26,.85), 0 0 60px rgba(255,42,26,.45); }
      .clock-am { font-family: "Courier Prime"; font-size: 44px; color: var(--led); align-self: flex-end; margin-bottom: 40px;
        text-shadow: 0 0 14px rgba(255,42,26,.8); }
      .cap { position: absolute; left: 0; right: 0; top: 946px; height: 128px; z-index: 60;
        display: flex; align-items: center; justify-content: center; }
      .cap-in { display: block; max-width: 1600px; text-align: center; font-family: "EB Garamond"; font-weight: 500;
        font-size: 44px; line-height: 1.15; color: var(--cream); letter-spacing: 0.5px; }
      .cap-in.cap-boy { font-style: italic; font-weight: 400; color: #cfe3ff; }
      .cap-in .w { display: inline-block; }
      .t-main { font-family: "Cinzel"; font-weight: 900; font-size: 168px; letter-spacing: 14px; color: var(--gold); text-shadow: 0 0 60px rgba(242,194,48,.3); }
      .t-tag { font-family: "Courier Prime"; font-size: 30px; letter-spacing: 12px; color: rgba(242,194,48,.85); }
      .t-soon { font-family: "Cinzel"; font-weight: 700; font-size: 44px; letter-spacing: 18px; color: var(--cream); }
      .bar { position: absolute; left: 0; right: 0; height: 138px; background: #000; z-index: 50; }
      #bar-top { top: 0; } #bar-bot { bottom: 0; }
      #flash { position: absolute; left: 0; right: 0; top: 138px; height: 804px; background: #fff; opacity: 0; z-index: 40; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="${D}">
${shotHtml.join("\n")}
${clockHtml}
${cardHtml.join("\n")}
${titleHtml}
      <div id="flash"></div>
      <div class="bar" id="bar-top"></div>
      <div class="bar" id="bar-bot"></div>
${capHtml.join("\n")}
${audioHtml.join("\n")}
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
${js.map((s) => "      " + s).join("\n")}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
`;
fs.writeFileSync(path.join(root, "index.html"), html);
console.log("wrote index.html");
