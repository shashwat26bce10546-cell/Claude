// Generates ../index.html for the Anna Delvey stickman explainer (English VO).
//   node build/build.mjs
// Timing comes from the ElevenLabs Scribe word timestamps in build/words.json.
// Style brief: minimal — captions carry the video, with a card only on the key beats.
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const words = JSON.parse(readFileSync(join(here, "words.json"), "utf8"));
const fmt = (n) => +(+n).toFixed(3);

// Scene starts (output seconds) — must match build/preprocess.py
const S = [0, 5.20, 8.95, 12.68, 16.10, 20.06, 23.35, 26.75, 31.06, 34.95, 38.32, 41.28, 45.50, 50.76, 55.76];
const END = 60.2;
const HANDLE = 0.3; // each prepped clip starts 0.3s early so transitions have something to work with

// transition INTO scene i (i >= 1) — kept light: cut-like fades, a couple of whips and zooms
const TRANS = [null, "whip", "fade", "pop", "fade", "zoom", "fade", "whip", "fade", "dip", "fade", "dip", "fade", "zoom", "whip"];

const tl = [];
const sfx = []; // [file, time, volume]

// ---------- footage ----------
const footage = S.map((s, i) => {
  const start = i === 0 ? 0 : fmt(s - HANDLE);
  const end = i < S.length - 1 ? S[i + 1] + HANDLE : END;
  const dur = fmt(end - start);
  const id = `s${i + 1}`;
  // no push-in on the artwork: the frame sits still (the flat 2% only keeps the whip/zoom cuts
  // from showing an edge for a few frames)
  tl.push(`tl.set("#${id}-kb", {scale:1.02}, ${start});`);
  return `      <div class="seg" id="${id}-wrap" style="z-index:${i + 1}"><div class="kb" id="${id}-kb"><div class="tx" id="${id}-tx">
        <video id="${id}" class="clip" src="media/prepped/s${i + 1}.mp4" muted playsinline data-start="${start}" data-duration="${dur}" data-track-index="0"></video>
      </div></div></div>`;
}).join("\n");

S.forEach((_, i) => tl.push(`tl.set("#s${i + 1}-tx", {opacity:1, scale:1, xPercent:0, filter:"blur(0px)"}, 0);`));

S.forEach((b, i) => {
  if (i === 0) return;
  const id = `s${i + 1}-tx`;
  const t0 = fmt(b - HANDLE);
  const kind = TRANS[i];
  if (kind === "whip") {
    tl.push(`tl.fromTo("#${id}", {opacity:1, xPercent:100, filter:"blur(14px)"}, {xPercent:0, filter:"blur(0px)", duration:.32, ease:"power3.out", immediateRender:false}, ${t0});`);
    tl.push(`tl.fromTo("#s${i}-tx", {xPercent:0, filter:"blur(0px)"}, {xPercent:-55, filter:"blur(14px)", duration:.32, ease:"power3.out", immediateRender:false}, ${t0});`);
    sfx.push(["whoosh-short", b - 0.36, 0.33]);
  } else if (kind === "zoom") {
    tl.push(`tl.fromTo("#${id}", {opacity:0, scale:1.25, filter:"blur(8px)"}, {opacity:1, scale:1, filter:"blur(0px)", duration:.4, ease:"power3.out", immediateRender:false}, ${t0});`);
    sfx.push(["whoosh-short", b - 0.34, 0.28]);
  } else if (kind === "pop") {
    tl.push(`tl.fromTo("#${id}", {opacity:0, scale:.88}, {opacity:1, scale:1, duration:.38, ease:"back.out(1.7)", immediateRender:false}, ${t0});`);
  } else if (kind === "dip") {
    tl.push(`tl.fromTo("#dip", {opacity:0}, {opacity:1, duration:.2, ease:"power2.in", immediateRender:false}, ${fmt(b - 0.2)});`);
    tl.push(`tl.to("#dip", {opacity:0, duration:.35, ease:"power2.out"}, ${b});`);
    tl.push(`tl.fromTo("#${id}", {opacity:0}, {opacity:1, duration:.01, immediateRender:false}, ${b});`);
  } else {
    tl.push(`tl.fromTo("#${id}", {opacity:0}, {opacity:1, duration:.45, ease:"sine.inOut", immediateRender:false}, ${t0});`);
  }
});

// ---------- motion graphics: key beats only ----------
const G = [];
const gfx = (id, a, b, cls, html, anim) => {
  G.push(`      <div class="gfx ${cls} clip" id="${id}" data-start="${fmt(a)}" data-duration="${fmt(b - a)}" data-track-index="6">${html}</div>`);
  tl.push(anim(fmt(a), fmt(b - a)));
};
// a card in the stickman world: off-white, thick black outline, slight tilt
const card = (id, a, b, cls, html, tilt = -2) => gfx(id, a, b, cls,
  `<div class="card" style="transform:rotate(${tilt}deg)">${html}</div>`,
  (T, D) => `tl.fromTo("#${id} .card", {opacity:0, y:26, scale:.88}, {opacity:1, y:0, scale:1, duration:.34, ease:"back.out(2)"}, ${T});` +
    `tl.to("#${id} .card", {opacity:0, y:-18, duration:.26, ease:"power2.in"}, ${fmt(T + D - 0.26)});`);

// EUR 60 MILLION, ANNA SOROKIN, ART CLUB, HOTEL, PROSECUTORS SAID, FORGED, $22M/$25M NO,
// $35,400 UNPAID, 2017, NO CRIME MEANT, APRIL 2019 GUILTY, 2021, 2022 and WOULD YOU HAVE
// BELIEVED HER? are already lettered into the artwork, so no card repeats them.
card("g-name", 5.6, 8.85, "g-top", `<b>ANNA DELVEY</b><span>the name was fake</span>`, -1.5);
sfx.push(["pop", 5.6, 0.4]);
sfx.push(["sparkle", 16.3, 0.4]);   // the hotel-life reveal is in the artwork; just accent it
card("g-larceny", 43.0, 45.4, "g-topright", `<b>GRAND LARCENY</b>`, 2.5);
sfx.push(["click-soft", 43.0, 0.45]);
card("g-years", 46.1, 48.8, "g-topright", `<b>4 TO 12 YEARS</b>`, -3);
sfx.push(["click-soft", 46.1, 0.45]);
card("g-show", 53.3, 55.65, "g-top", `<b>&ldquo;INVENTING ANNA&rdquo;</b><span>her story on screen</span>`, 2);
sfx.push(["pop", 53.3, 0.4]);

// final fade
tl.push(`tl.fromTo("#fade", {opacity:0}, {opacity:1, duration:.6, ease:"power1.in", immediateRender:false}, ${fmt(END - 0.6)});`);

// ---------- captions ----------
const groups = [];
let cur = [];
words.forEach((w, i) => {
  cur.push(w);
  const nxt = words[i + 1];
  const punct = /[.,!?]$/.test(w.text);
  const gap = nxt ? nxt.start - w.end : 1;
  if (cur.length >= 3 || punct || gap > 0.25 || !nxt) {
    groups.push(cur);
    cur = [];
  }
});
const caps = groups.map((g, gi) => {
  const id = `cap-${gi}`;
  const start = fmt(g[0].start - 0.05);
  const nextStart = groups[gi + 1] ? groups[gi + 1][0].start - 0.05 : END - 0.7;
  const end = fmt(Math.min(nextStart, g[g.length - 1].end + 0.55));
  tl.push(`tl.fromTo("#${id} .cap-in", {opacity:0, y:18, scale:.95}, {opacity:1, y:0, scale:1, duration:.13, ease:"back.out(2)"}, ${start});`);
  const spans = g.map((w, j) => {
    const clean = w.text.replace(/[.,!?]$/, "").toUpperCase();
    tl.push(`tl.fromTo("#${id}-w${j}", {scale:1, y:0}, {scale:1.1, y:-4, duration:.08, ease:"power2.out", immediateRender:false}, ${fmt(w.start)});`);
    tl.push(`tl.to("#${id}-w${j}", {scale:1, y:0, duration:.12}, ${fmt(Math.max(w.start + 0.09, w.end))});`);
    return `<span class="cw" id="${id}-w${j}">${clean}</span>`;
  }).join(" ");
  return `      <div class="cap clip" id="${id}" data-start="${start}" data-duration="${fmt(end - start)}" data-track-index="5"><div class="cap-in">${spans}</div></div>`;
}).join("\n");

// ---------- audio ----------
const SFX_LEN = { "whoosh-short": 0.9, pop: 0.5, "click-soft": 0.4, sparkle: 1.5, chime: 2.5 };
const sfxHtml = sfx.sort((a, b) => a[1] - b[1]).map(([f, t, v], i) => {
  const start = Math.max(0, fmt(t));
  const dur = fmt(Math.min(SFX_LEN[f] ?? 1, END - start));
  return `      <audio id="sfx-${i}" src="assets/sfx/${f}.mp3" data-start="${start}" data-duration="${dur}" data-track-index="${20 + (i % 4)}" data-volume="${v}"></audio>`;
}).join("\n");

const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Anna Delvey — stickman explainer</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Montserrat"; font-weight: 900; src: url("assets/fonts/montserrat-latin-900-normal.woff2") format("woff2"); }
      @font-face { font-family: "Anton"; src: url("assets/fonts/anton-latin-400-normal.woff2") format("woff2"); }
      :root { --ink: #16120E; --paper: #FFF8EC; --orange: #F08A24; }
      body { margin: 0; background: #000; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; font-family: "Montserrat", sans-serif; color: #fff; }
      .seg { position: absolute; inset: 0; overflow: hidden; }
      .kb, .tx { position: absolute; inset: 0; transform-origin: 50% 45%; }
      .seg video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      /* the artwork is bright and flat, so only a soft shelf behind the captions is darkened */
      #grade { position: absolute; inset: 0; z-index: 100; pointer-events: none;
        background: linear-gradient(0deg, rgba(14,10,6,.5) 0%, rgba(14,10,6,.15) 18%, rgba(14,10,6,0) 30%); }
      #dip { position: absolute; inset: 0; z-index: 401; opacity: 0; background: #000; }
      #fade { position: absolute; inset: 0; z-index: 500; opacity: 0; background: #000; }

      .gfx { position: absolute; left: 0; right: 0; z-index: 300; display: flex; justify-content: center; }
      .g-top { top: 110px; }
      .g-topright { top: 120px; justify-content: flex-end; padding-right: 60px; }
      .g-mid { top: 620px; }
      .card { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 22px 42px;
        background: var(--paper); border: 7px solid var(--ink); border-radius: 26px;
        box-shadow: 10px 12px 0 rgba(22,18,14,.35); }
      .card b { display: block; font-size: 62px; line-height: 1; letter-spacing: 1px; color: var(--ink); }
      .card span { display: block; font-family: "Montserrat"; font-weight: 900; font-size: 30px; letter-spacing: 2px; color: #7A6B57; text-transform: uppercase; }
      .money { display: flex; flex-direction: column; align-items: center; padding: 26px 56px;
        background: var(--orange); border: 8px solid var(--ink); border-radius: 30px; box-shadow: 12px 14px 0 rgba(22,18,14,.4); }
      .money { font-family: "Anton"; font-size: 160px; line-height: .95; color: var(--paper); -webkit-text-stroke: 4px var(--ink); }
      .money span { display: block; font-size: 62px; letter-spacing: 6px; -webkit-text-stroke: 3px var(--ink); }

      .cap { position: absolute; left: 60px; right: 60px; top: 1430px; height: 290px; z-index: 350;
        display: flex; align-items: center; justify-content: center; }
      .cap-in { display: block; max-width: 940px; text-align: center; font-weight: 900; font-size: 74px; line-height: 1.12;
        color: #fff; -webkit-text-stroke: 11px var(--ink); paint-order: stroke fill; text-shadow: 0 6px 18px rgba(0,0,0,.55); }
      .cw { display: inline-block; margin: 0 .18em; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="${END}">
${footage}
      <div id="grade"></div>
${G.join("\n")}
${caps}
      <div id="dip"></div>
      <div id="fade"></div>
      <audio id="voiceover" src="assets/audio/voiceover-master.mp3" data-start="0" data-duration="59.3" data-track-index="10" data-volume="1"></audio>
      <audio id="score" src="assets/audio/score.mp3" data-start="0" data-duration="${END}" data-track-index="11" data-volume="0.3"></audio>
${sfxHtml}
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      ${tl.join("\n      ")}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
`;
writeFileSync(join(here, "..", "index.html"), html);
console.log(`scenes=${S.length} captions=${groups.length} graphics=${G.length} sfx=${sfx.length} duration=${END}s`);
