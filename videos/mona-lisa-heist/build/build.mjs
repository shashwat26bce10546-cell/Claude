// Generates ../index.html for "The Mona Lisa Heist" (vertical stick-figure explainer).
//   node build/build.mjs
// Timing comes from the user's ElevenLabs voiceover (build/words.json, Scribe word timestamps).
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const words = JSON.parse(readFileSync(join(here, "words.json"), "utf8"));
const fmt = (n) => +(+n).toFixed(3);

// Clip starts (output seconds) — must match build/preprocess.sh
const S = [0, 5.4, 10.78, 17.4, 22.54, 26.86, 32.96, 36.54];
const END = 41.4;
const HANDLE = 0.3;
// transition INTO clip i
const TRANS = [null, "slideUp", "zoom", "flash", "whipL", "slideUp", "whipR", "zoom"];

const tl = [];
const sfx = []; // [file, time, volume, mediaStart?, duration?]

// ---------- footage ----------
const footage = S.map((s, i) => {
  const start = i === 0 ? 0 : fmt(s - HANDLE);
  const end = i < S.length - 1 ? S[i + 1] + HANDLE : END;
  const dur = fmt(end - start);
  const id = `c${i + 1}`;
  const from = i === 99 ? 1.14 : i % 2 ? 1.08 : 1.0;
  const to = i === 99 ? 1.2 : i % 2 ? 1.02 : 1.06;
  tl.push(`tl.fromTo("#${id}-kb", {scale:${from}}, {scale:${to}, duration:${dur}, ease:"none"}, ${start});`);
  tl.push(`tl.set("#${id}-tx", {opacity:1, scale:1, xPercent:0, yPercent:0, filter:"blur(0px)"}, 0);`);
  return `      <div class="seg" style="z-index:${i + 1}"><div class="kb" id="${id}-kb"><div class="tx" id="${id}-tx">
        <video id="${id}" class="clip" src="media/prepped/s${i + 1}.mp4" muted playsinline data-start="${start}" data-duration="${dur}" data-track-index="0"></video>
      </div></div></div>`;
}).join("\n");

S.forEach((b, i) => {
  if (i === 0) return;
  const id = `c${i + 1}-tx`;
  const prev = `c${i}-tx`;
  const t0 = fmt(b - HANDLE);
  const k = TRANS[i];
  if (k === "whipL" || k === "whipR") {
    const d = k === "whipL" ? 1 : -1;
    tl.push(`tl.fromTo("#${id}", {xPercent:${100 * d}, filter:"blur(14px)"}, {xPercent:0, filter:"blur(0px)", duration:.4, ease:"power3.out", immediateRender:false}, ${t0});`);
    tl.push(`tl.fromTo("#${prev}", {xPercent:0, filter:"blur(0px)"}, {xPercent:${-60 * d}, filter:"blur(14px)", duration:.4, ease:"power3.out", immediateRender:false}, ${t0});`);
    sfx.push(["whoosh", b - 0.45, 0.4]);
  } else if (k === "zoom") {
    tl.push(`tl.fromTo("#${id}", {opacity:0, scale:1.35, filter:"blur(10px)"}, {opacity:1, scale:1, filter:"blur(0px)", duration:.45, ease:"power3.out", immediateRender:false}, ${t0});`);
    tl.push(`tl.fromTo("#${prev}", {scale:1, filter:"blur(0px)"}, {scale:1.3, filter:"blur(8px)", duration:.3, ease:"power2.in", immediateRender:false}, ${t0});`);
    sfx.push(["whoosh-short", b - 0.4, 0.4]);
  } else if (k === "slideUp") {
    tl.push(`tl.fromTo("#${id}", {yPercent:100}, {yPercent:0, duration:.45, ease:"power3.out", immediateRender:false}, ${t0});`);
    tl.push(`tl.fromTo("#${prev}", {yPercent:0}, {yPercent:-30, duration:.45, ease:"power3.out", immediateRender:false}, ${t0});`);
    sfx.push(["whoosh-short", b - 0.4, 0.35]);
  } else {
    tl.push(`tl.fromTo("#${id}", {opacity:0}, {opacity:1, duration:.01, immediateRender:false}, ${b});`);
    tl.push(`tl.fromTo("#flash", {opacity:0}, {opacity:1, duration:.12, ease:"power2.in", immediateRender:false}, ${fmt(b - 0.12)});`);
    tl.push(`tl.to("#flash", {opacity:0, duration:.4, ease:"power2.out"}, ${b});`);
    sfx.push(["whoosh", b - 0.4, 0.35]);
  }
});

// ---------- motion graphics ----------
const G = [];
const gfx = (id, a, b, cls, html, anim) => {
  G.push(`      <div class="gfx ${cls} clip" id="${id}" data-start="${fmt(a)}" data-duration="${fmt(b - a)}" data-track-index="6">${html}</div>`);
  tl.push(anim(fmt(a), fmt(b - a)));
};
const out = (sel, T, D, d = 0.25) => `tl.to("${sel}", {opacity:0, duration:${d}, ease:"power2.in"}, ${fmt(T + D - d)});`;
const popIn = (sel, t, rot = -4) =>
  `tl.fromTo("${sel}", {opacity:0, scale:.4, rotate:${rot - 12}}, {opacity:1, scale:1, rotate:${rot}, duration:.35, ease:"back.out(2.2)", immediateRender:false}, ${fmt(t)});`;
const stampIn = (sel, t, rot = -8) =>
  `tl.fromTo("${sel}", {opacity:0, scale:2.4, rotate:${rot + 6}}, {opacity:1, scale:1, rotate:${rot}, duration:.22, ease:"power4.in", immediateRender:false}, ${fmt(t)});`;
const CHECK = `<svg class="ic" viewBox="0 0 40 40"><path d="M8 21 L17 30 L33 10" /></svg>`;
const CROSS = `<svg class="ic ic-x" viewBox="0 0 40 40"><path d="M9 9 L31 31 M31 9 L9 31" /></svg>`;
const CHUTE = `<svg class="chute" viewBox="0 0 60 70"><path d="M4 28 Q30 -8 56 28 Z" fill="#E8463A" stroke="#1d1d1d" stroke-width="3"/><path d="M4 28 L30 58 M56 28 L30 58 M22 28 L30 58 M38 28 L30 58" stroke="#1d1d1d" stroke-width="2" fill="none"/><rect x="25" y="56" width="10" height="10" rx="2" fill="#1d1d1d"/></svg>`;

// 1 — title + STOLEN
gfx("g1", 0.14, 5.3, "g-top", `<div class="folder"><div class="tab">CASE FILE</div><div class="folder-body">THE MONA LISA<br>HEIST</div></div><div class="stamp" id="g1-st" style="opacity:0">STOLEN!</div>`,
  (T, D) => `tl.fromTo("#g1 .folder", {opacity:0, y:-80, rotate:-6}, {opacity:1, y:0, rotate:-2, duration:.5, ease:"back.out(1.7)"}, ${T});
    ${stampIn("#g1-st", 4.56)}${out("#g1 .folder, #g1-st", T, D)}`);
sfx.push(["pop", 0.14, 0.35], ["impact-bass-1", 4.56, 0.4]);

// 2 — nobody around
gfx("g2", 9.1, 10.65, "g-low", `<div class="note note-y" id="g2-n">ALMOST NOBODY<br>AROUND...</div>`,
  (T, D) => `${popIn("#g2-n", T, -4)}${out("#g2-n", T, D, 0.2)}`);
sfx.push(["pop", 9.1, 0.3]);

// 3 — suspect file + hid / took / left
gfx("g3", 12.28, 17.25, "g-top", `<div class="ticket" id="g3-card"><span>SUSPECT</span><b>VINCENZO PERUGGIA</b><i>LOUVRE WORKER</i></div><div class="steps">${[["a","HID"],["b","TOOK"],["c","LEFT"]].map(([k,t]) => `<div class="note note-o" id="g3-${k}" style="opacity:0">${t}</div>`).join("")}</div>`,
  (T, D) => `tl.fromTo("#g3-card", {opacity:0, x:300, rotate:10}, {opacity:1, x:0, rotate:-2, duration:.45, ease:"power3.out"}, ${T});
    ${popIn("#g3-a", 14.22, -4)}
    ${popIn("#g3-b", 15.32, 3)}
    ${popIn("#g3-c", 16.52, -3)}${out("#g3-card, #g3 .steps", T, D)}`);
sfx.push(["key-press", 12.28, 0.4], ["pop", 14.22, 0.3], ["pop", 15.32, 0.3], ["pop", 16.52, 0.3]);

// 4 — empty wall, Paris in shock
gfx("g4", 19.4, 22.4, "g-low", `<div class="stamp" id="g4-s">EMPTY WALL</div><div class="note note-y" id="g4-n" style="opacity:0">PARIS IN SHOCK!</div>`,
  (T, D) => `${stampIn("#g4-s", T, -6)}
    ${popIn("#g4-n", 20.56, 4)}${out("#g4-s, #g4-n", T, D)}`);
sfx.push(["impact-bass-1", 19.4, 0.4], ["pop", 20.56, 0.3]);

// 5 — painting gone
gfx("g5", 25.9, 26.75, "g-low", `<div class="stamp stamp-sm" id="g5-s">STILL MISSING</div>`,
  (T, D) => `${stampIn("#g5-s", T, 5)}${out("#g5-s", T, D, 0.15)}`);
sfx.push(["impact-bass-1", 25.9, 0.35]);

// 6 — Italy, dealer calls police
gfx("g6", 30.36, 32.85, "g-low", `<div class="pin-tag" id="g6-p"><span class="pin"></span>ITALY</div><div class="note note-o note-sm" id="g6-n" style="opacity:0">DEALER CALLS<br>THE POLICE</div>`,
  (T, D) => `tl.fromTo("#g6-p", {opacity:0, y:-60}, {opacity:1, y:0, duration:.4, ease:"back.out(2)"}, ${T});
    ${popIn("#g6-n", 31.32, -3)}${out("#g6-p, #g6-n", T, D)}`);
sfx.push(["pop", 30.36, 0.3], ["notification", 31.32, 0.3]);

// 7 — caught, returned to Paris
gfx("g7", 33.26, 36.4, "g-low", `<div class="stamp" id="g7-s">CAUGHT!</div><div class="checks"><div class="chk" id="g7-c" style="opacity:0">${CHECK}<span>BACK HOME IN PARIS</span></div></div>`,
  (T, D) => `${stampIn("#g7-s", T, -6)}
    tl.fromTo("#g7-c", {opacity:0, x:-60}, {opacity:1, x:0, duration:.3, ease:"power3.out", immediateRender:false}, 35.0);
    tl.fromTo("#g7-c .ic path", {strokeDashoffset:60}, {strokeDashoffset:0, duration:.3, immediateRender:false}, 35.08);${out("#g7-s, #g7 .checks", T, D)}`);
sfx.push(["impact-bass-1", 33.26, 0.4], ["ping", 35.0, 0.3]);

// 8 — CTA
gfx("g8", 39.32, END, "g-low", `<div class="bubble" id="g8-b">TELL ME IN THE COMMENTS</div>`,
  (T) => `tl.fromTo("#g8-b", {opacity:0, y:40, scale:.7}, {opacity:1, y:0, scale:1, duration:.4, ease:"back.out(2)"}, ${T});
    tl.to("#g8-b", {scale:1.06, duration:.35, yoyo:true, repeat:1, ease:"sine.inOut"}, ${T + 0.6});`);
sfx.push(["notification", 39.32, 0.3]);

tl.push(`tl.fromTo("#fade", {opacity:0}, {opacity:1, duration:.5, immediateRender:false}, ${fmt(END - 0.5)});`);

// ---------- captions ----------
const KEY = /^(1911|louvre|mona|lisa|coat|monday|closed|nobody|thief|vincenzo|peruggia|hid|took|left|empty|wall|paris|shock|police|two|years|gone|1913|italy|dealer|caught|home|stolen|comments)$/i;
const groups = [];
let cur = [];
words.forEach((w, i) => {
  cur.push(w);
  const nxt = words[i + 1];
  const punct = /[.,!?:]$/.test(w.text);
  const gap = nxt ? nxt.start - w.end : 1;
  if (cur.length >= 3 || punct || gap > 0.3 || !nxt) {
    groups.push(cur);
    cur = [];
  }
});
const caps = groups.map((g, gi) => {
  const id = `cap-${gi}`;
  const start = fmt(g[0].start - 0.05);
  const nextStart = groups[gi + 1] ? groups[gi + 1][0].start - 0.05 : END - 0.5;
  const end = fmt(Math.min(nextStart, g[g.length - 1].end + 0.5));
  tl.push(`tl.fromTo("#${id} .cap-in", {opacity:0, y:20, scale:.9}, {opacity:1, y:0, scale:1, duration:.13, ease:"back.out(2)"}, ${start});`);
  const spans = g
    .map((w, j) => {
      const clean = w.text.replace(/[.,!?:]$/, "").toUpperCase();
      const key = KEY.test(clean);
      const base = key ? "#FFB21A" : "#FFFFFF";
      tl.push(`tl.fromTo("#${id}-w${j}", {color:"${base}", scale:1}, {color:"#FF7A1A", scale:1.14, duration:.08, ease:"power2.out", immediateRender:false}, ${fmt(w.start)});`);
      tl.push(`tl.to("#${id}-w${j}", {color:"${base}", scale:1, duration:.12}, ${fmt(Math.max(w.start + 0.09, w.end))});`);
      return `<span class="cw" id="${id}-w${j}" style="color:${base}">${clean}</span>`;
    })
    .join(" ");
  return `      <div class="cap clip" id="${id}" data-start="${start}" data-duration="${fmt(end - start)}" data-track-index="5"><div class="cap-in">${spans}</div></div>`;
}).join("\n");

// ---------- audio ----------
const LEN = { whoosh: 1.2, "whoosh-short": 0.8, pop: 0.72, click: 0.37, ping: 1.32, error: 1.62, "impact-bass-1": 2.12, riser: 2.42, "key-press": 0.4, sparkle: 1.5, notification: 2.46 };
const sfxHtml = sfx
  .sort((a, b) => a[1] - b[1])
  .map(([f, t, v, ms, d], i) => {
    const start = Math.max(0, fmt(t));
    const dur = fmt(Math.min(d ?? LEN[f] ?? 1, END - start));
    return `      <audio id="sfx-${i}" src="assets/sfx/${f}.mp3" data-start="${start}" data-duration="${dur}"${ms ? ` data-media-start="${ms}"` : ""} data-track-index="${20 + (i % 4)}" data-volume="${v}"></audio>`;
  })
  .join("\n");

const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Mona Lisa Heist</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Permanent Marker"; font-weight: 400; src: url("assets/fonts/permanent-marker-latin-400-normal.woff2") format("woff2"); }
      @font-face { font-family: "Montserrat"; font-weight: 800; src: url("assets/fonts/montserrat-latin-800-normal.woff2") format("woff2"); }
      @font-face { font-family: "Montserrat"; font-weight: 900; src: url("assets/fonts/montserrat-latin-900-normal.woff2") format("woff2"); }
      :root { --ink: #1d1d1d; --orange: #FF7A1A; --red: #D7263D; --green: #1E9E5A; --paper: #FFF8E7; }
      body { margin: 0; background: #fff; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #fff; font-family: "Montserrat", sans-serif; color: var(--ink); }
      .seg { position: absolute; inset: 0; overflow: hidden; }
      .kb, .tx { position: absolute; inset: 0; transform-origin: 50% 50%; }
      .seg video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      #night { position: absolute; inset: 0; z-index: 100; opacity: 0; background: #0B1638; mix-blend-mode: multiply; }
      #vignette { position: absolute; inset: 0; z-index: 101; background: radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 62%, rgba(0,0,0,.22) 100%); }
      #capfade { position: absolute; left: 0; right: 0; top: 1300px; height: 620px; z-index: 102;
        background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,.28) 45%, rgba(0,0,0,.4) 100%); }
      #flash { position: absolute; inset: 0; z-index: 400; opacity: 0; background: #fff; }
      #fade { position: absolute; inset: 0; z-index: 500; opacity: 0; background: #000; }

      .gfx { position: absolute; left: 0; right: 0; z-index: 300; display: flex; flex-direction: column; align-items: center; gap: 22px; }
      .g-low { top: 330px; height: 700px; justify-content: flex-start; }
      .g-top { top: 150px; height: 760px; justify-content: flex-start; }
      .hand, .note, .stamp, .big, .label, .tag-dark, .bubble, .folder-body, .tab, .ticket b, .counter b, .money b { font-family: "Permanent Marker", cursive; }

      .folder { display: block; width: 760px; transform-origin: 50% 50%; }
      .tab { display: inline-block; padding: 10px 34px; border-radius: 18px 18px 0 0; background: #E9B949; font-size: 38px; color: var(--ink); border: 4px solid var(--ink); border-bottom: 0; }
      .folder-body { display: block; padding: 34px 40px; background: #F4CE6A; border: 4px solid var(--ink); border-radius: 0 18px 18px 18px; font-size: 84px; line-height: 1.05; text-align: center; box-shadow: 10px 12px 0 rgba(0,0,0,.18); }
      .note { display: block; padding: 22px 40px; font-size: 68px; line-height: 1.1; text-align: center; border: 4px solid var(--ink); box-shadow: 8px 10px 0 rgba(0,0,0,.2); }
      .note-y { background: #FFE680; }
      .note-o { background: #FFC08A; font-size: 54px; }
      .stamp { display: block; padding: 12px 36px; border: 9px solid var(--red); border-radius: 16px; color: var(--red); font-size: 92px; letter-spacing: 3px; background: rgba(255,255,255,.88); }
      .stamp-sm { font-size: 70px; }
      .stamp-g { border-color: var(--green); color: var(--green); font-size: 66px; }
      .ticket { display: flex; flex-direction: column; align-items: flex-start; gap: 4px; padding: 22px 46px; background: var(--paper); border: 4px dashed var(--ink); box-shadow: 8px 10px 0 rgba(0,0,0,.2); }
      .ticket span { display: block; font-weight: 900; font-size: 26px; letter-spacing: 6px; color: #777; }
      .ticket b { display: block; font-weight: 400; font-size: 76px; color: var(--ink); }
      .ticket i { display: block; font-style: normal; font-weight: 800; font-size: 28px; color: var(--orange); }
      .paper { display: flex; flex-direction: column; align-items: center; padding: 34px 60px; background: var(--paper); border: 4px solid var(--ink); box-shadow: 10px 12px 0 rgba(0,0,0,.2); }
      .hand { display: block; font-size: 84px; line-height: 1.05; }
      .red { color: var(--red); font-size: 130px; }
      .money b { display: block; font-weight: 400; font-size: 150px; color: var(--green); -webkit-text-stroke: 4px var(--ink); paint-order: stroke fill; text-shadow: 8px 10px 0 rgba(0,0,0,.2); }
      .chutes { display: flex; gap: 30px; }
      .chute-w { display: block; width: 120px; height: 140px; }
      .chute { display: block; width: 100%; height: 100%; }
      .pin-tag { display: flex; align-items: center; gap: 22px; padding: 18px 44px; background: #fff; border: 4px solid var(--ink); border-radius: 999px; font-family: "Permanent Marker"; font-size: 76px; box-shadow: 8px 10px 0 rgba(0,0,0,.2); }
      .pin { display: block; width: 46px; height: 46px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); background: var(--red); border: 4px solid var(--ink); }
      .checks { display: flex; flex-direction: column; gap: 14px; }
      .chk { display: flex; align-items: center; gap: 20px; padding: 14px 32px; background: #fff; border: 4px solid var(--ink); border-radius: 16px; font-weight: 900; font-size: 44px; box-shadow: 6px 8px 0 rgba(0,0,0,.18); }
      .ic { display: block; width: 54px; height: 54px; fill: none; stroke: var(--green); stroke-width: 7; stroke-linecap: round; stroke-linejoin: round; stroke-dasharray: 60; }
      .ic-x { stroke: var(--red); stroke-dasharray: none; }
      .route { display: flex; flex-direction: column; align-items: center; width: 860px; }
      .route svg { display: block; width: 760px; height: 152px; }
      .label { display: block; padding: 16px 40px; background: rgba(10,18,40,.85); color: #fff; font-size: 52px; border-radius: 14px; }
      .big { display: block; font-size: 150px; line-height: 1; color: #fff; -webkit-text-stroke: 12px var(--ink); paint-order: stroke fill; text-shadow: 10px 12px 0 rgba(0,0,0,.25); text-align: center; }
      .big-q { color: var(--orange); font-size: 110px; }
      #g15 .big { font-size: 112px; color: var(--orange); max-width: 960px; }
      .counter { display: flex; align-items: baseline; gap: 22px; padding: 20px 50px; background: #fff; border: 5px solid var(--ink); border-radius: 22px; box-shadow: 10px 12px 0 rgba(0,0,0,.2); }
      .counter b { display: block; font-weight: 400; font-size: 170px; line-height: 1; color: var(--orange); }
      .counter span { display: block; font-weight: 900; font-size: 64px; }
      .tag-dark { display: block; padding: 14px 40px; background: var(--ink); color: #fff; font-size: 52px; border-radius: 12px; }
      .bubble { position: relative; display: block; padding: 26px 48px; background: #fff; border: 5px solid var(--ink); border-radius: 40px; font-size: 56px; box-shadow: 8px 10px 0 rgba(0,0,0,.2); }

      .cap { position: absolute; left: 50px; right: 50px; top: 1440px; height: 260px; z-index: 350; display: flex; align-items: center; justify-content: center; }
      .cap-in { display: block; max-width: 960px; text-align: center; font-weight: 900; font-size: 80px; line-height: 1.1; letter-spacing: -1px;
        -webkit-text-stroke: 12px var(--ink); paint-order: stroke fill; text-shadow: 0 6px 0 rgba(0,0,0,.35); }
      .who { display: flex; flex-wrap: wrap; justify-content: center; gap: 14px; max-width: 980px; }
      .chip-x { position: relative; display: block; padding: 12px 26px; background: #fff; border: 4px solid var(--ink); border-radius: 14px; font-weight: 900; font-size: 44px; box-shadow: 6px 8px 0 rgba(0,0,0,.18); }
      .chip-x span { display: block; }
      .chip-x i { position: absolute; left: 10px; right: 10px; top: 50%; height: 8px; margin-top: -4px; background: var(--red); border-radius: 4px; transform-origin: 0 50%; }
      .steps { display: flex; align-items: center; gap: 14px; justify-content: center; }
      .steps .note { font-size: 48px; padding: 14px 26px; }
      .note-sm { font-size: 40px; padding: 12px 24px; }
      .arr { display: block; font-weight: 900; font-size: 50px; }
      .theories { display: flex; gap: 18px; justify-content: center; }
      .theories .note { font-size: 44px; padding: 16px 24px; }
      .cw { display: inline-block; margin: 0 .18em; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="${END}">
${footage}
      <div id="night"></div>
      <div id="vignette"></div>
      <div id="capfade"></div>
${G.join("\n")}
${caps}
      <div id="flash"></div>
      <div id="fade"></div>
      <audio id="voiceover" src="assets/audio/voiceover-master.mp3" data-start="0" data-duration="40.5" data-track-index="10" data-volume="1"></audio>
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
console.log(`clips=${S.length} captions=${groups.length} graphics=${G.length} sfx=${sfx.length} duration=${END}s`);
