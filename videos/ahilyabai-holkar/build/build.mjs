// Generates ../index.html for "Punyashlok Ahilyabai Holkar" (Hindi VO, Hinglish captions).
//   node build/build.mjs
// Timing comes from the ElevenLabs voiceover (build/words.json, Scribe word timestamps).
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const words = JSON.parse(readFileSync(join(here, "words.json"), "utf8"));
const fmt = (n) => +(+n).toFixed(3);

// Scene starts (output seconds) — must match build/preprocess.sh
const S = [0, 4.44, 8.1, 12.62, 17.1, 21.02, 24.16, 28.3, 32.34, 36.48, 39.58, 43.4, 47.5, 51.62, 55.96];
const END = 61.4;
const HANDLE = 0.3; // each prepped clip starts 0.3s before its scene (crossfade handle)

// transition INTO scene i (i >= 1)
const TRANS = [null, "fade", "lightleak", "goldflash", "darkdip", "fade", "darkdip", "lightleak", "goldflash", "zoom", "whip", "lightleak", "zoom", "darkdip", "goldflash"];

const tl = [];
const sfx = []; // [file, time, volume, mediaStart?, duration?]

// ---------- footage ----------
const footage = S.map((s, i) => {
  const start = i === 0 ? 0 : fmt(s - HANDLE);
  const next = i < S.length - 1 ? S[i + 1] : END;
  const end = i < S.length - 1 ? next + HANDLE : END;
  const dur = fmt(end - start);
  const id = `s${i + 1}`;
  // slow Ken Burns on every scene, alternating push-in / drift
  const from = i % 2 ? 1.12 : 1.0;
  const to = i % 2 ? 1.04 : 1.08;
  tl.push(`tl.fromTo("#${id}-kb", {scale:${from}}, {scale:${to}, duration:${dur}, ease:"none"}, ${start});`);
  return `      <div class="seg" id="${id}-wrap" style="z-index:${i + 1}"><div class="kb" id="${id}-kb"><div class="tx" id="${id}-tx">
        <video id="${id}" class="clip" src="media/prepped/s${i + 1}.mp4" muted playsinline data-start="${start}" data-duration="${dur}" data-track-index="0"></video>
      </div></div></div>`;
}).join("\n");

// baselines for transition targets
S.forEach((_, i) => tl.push(`tl.set("#s${i + 1}-tx", {opacity:1, scale:1, xPercent:0, filter:"blur(0px)"}, 0);`));

S.forEach((b, i) => {
  if (i === 0) return;
  const id = `s${i + 1}-tx`;
  const t0 = fmt(b - HANDLE);
  const kind = TRANS[i];
  if (kind === "goldflash") {
    tl.push(`tl.fromTo("#${id}", {opacity:0}, {opacity:1, duration:.3, ease:"none", immediateRender:false}, ${t0});`);
    tl.push(`tl.fromTo("#flash", {opacity:0}, {opacity:.9, duration:.18, ease:"power2.in", immediateRender:false}, ${fmt(b - 0.18)});`);
    tl.push(`tl.to("#flash", {opacity:0, duration:.5, ease:"power2.out"}, ${b});`);
    sfx.push(["whoosh-cinematic", b - 0.6, 0.35]);
  } else if (kind === "zoom") {
    tl.push(`tl.fromTo("#${id}", {opacity:0, scale:1.35, filter:"blur(12px)"}, {opacity:1, scale:1, filter:"blur(0px)", duration:.5, ease:"power3.out", immediateRender:false}, ${t0});`);
    tl.push(`tl.fromTo("#s${i}-tx", {scale:1, filter:"blur(0px)"}, {scale:1.3, filter:"blur(10px)", duration:.3, ease:"power2.in", immediateRender:false}, ${t0});`);
    sfx.push(["whoosh", b - 0.45, 0.4]);
  } else if (kind === "whip") {
    tl.push(`tl.fromTo("#${id}", {opacity:1, xPercent:100, filter:"blur(16px)"}, {xPercent:0, filter:"blur(0px)", duration:.4, ease:"power3.out", immediateRender:false}, ${t0});`);
    tl.push(`tl.fromTo("#s${i}-tx", {xPercent:0, filter:"blur(0px)"}, {xPercent:-60, filter:"blur(16px)", duration:.4, ease:"power3.out", immediateRender:false}, ${t0});`);
    sfx.push(["whoosh", b - 0.5, 0.45]);
  } else if (kind === "darkdip") {
    tl.push(`tl.fromTo("#dip", {opacity:0}, {opacity:1, duration:.25, ease:"power2.in", immediateRender:false}, ${fmt(b - 0.25)});`);
    tl.push(`tl.to("#dip", {opacity:0, duration:.45, ease:"power2.out"}, ${b});`);
    tl.push(`tl.fromTo("#${id}", {opacity:0}, {opacity:1, duration:.01, immediateRender:false}, ${b});`);
    tl.push(`tl.fromTo("#${id}", {scale:1.12}, {scale:1, duration:.8, ease:"power3.out", immediateRender:false}, ${b});`);
    sfx.push(["impact-bass-2", b - 0.35, 0.5]);
  } else if (kind === "lightleak") {
    tl.push(`tl.fromTo("#${id}", {opacity:0}, {opacity:1, duration:.7, ease:"sine.inOut", immediateRender:false}, ${t0});`);
    tl.push(`tl.fromTo("#leak", {opacity:0, xPercent:-30}, {opacity:.85, xPercent:0, duration:.45, ease:"sine.out", immediateRender:false}, ${t0});`);
    tl.push(`tl.to("#leak", {opacity:0, xPercent:30, duration:.6, ease:"sine.in"}, ${fmt(b + 0.15)});`);
    sfx.push(["sparkle", b - 0.3, 0.35]);
  } else {
    tl.push(`tl.fromTo("#${id}", {opacity:0}, {opacity:1, duration:.6, ease:"sine.inOut", immediateRender:false}, ${t0});`);
    sfx.push(["whoosh-cinematic", b - 0.5, 0.25]);
  }
});

// ---------- motion graphics ----------
const G = [];
const gfx = (id, a, b, cls, html, anim) => {
  G.push(`      <div class="gfx ${cls} clip" id="${id}" data-start="${fmt(a)}" data-duration="${fmt(b - a)}" data-track-index="6">${html}</div>`);
  tl.push(anim(fmt(a), fmt(b - a)));
};
const outT = (sel, T, D, d = 0.3) => `tl.to("${sel}", {opacity:0, y:-24, duration:${d}, ease:"power2.in"}, ${fmt(T + D - d)});`;

const pop = (sel, t) => `tl.fromTo("${sel}", {opacity:0, y:30, scale:.9}, {opacity:1, y:0, scale:1, duration:.4, ease:"back.out(1.8)", immediateRender:false}, ${fmt(t)});`;
const ribbon = (id, a, b, text, alt) => gfx(id, a, b, "g-top2", `<div class="ribbon${alt ? " ribbon2" : ""}">${text}</div>`,
  (T, D) => `tl.fromTo("#${id} .ribbon", {opacity:0, scaleX:0}, {opacity:1, scaleX:1, duration:.45, ease:"power3.out"}, ${T});${outT(`#${id} .ribbon`, T, D, 0.2)}`);
const plate = (id, a, b, side, name, sub, red) => gfx(id, a, b, side === "l" ? "g-plate-l" : "g-plate-r",
  `<div class="plate${side === "r" ? " plate-r" : ""}${red ? " plate-red" : ""}"><b>${name}</b><span>${sub}</span></div>`,
  (T, D) => `tl.fromTo("#${id} .plate", {opacity:0, x:${side === "l" ? -80 : 80}}, {opacity:1, x:0, duration:.45, ease:"power3.out"}, ${T});${outT(`#${id} .plate`, T, D, 0.25)}`);
const year = (id, a, b, y, red, extraHtml = "", extraAnim = "") => gfx(id, a, b, "g-top2 col", `<div class="year${red ? " year-red" : ""}">${y}</div>${extraHtml}`,
  (T, D) => `tl.fromTo("#${id} .year", {opacity:0, scale:2.2}, {opacity:1, scale:1, duration:.4, ease:"power4.out"}, ${T});${extraAnim}${outT(`#${id} > *`, T, D)}`);

// 1 — hook title
gfx("g-title", 0.3, 4.3, "g-top", `<div class="title-wrap"><div class="kicker">MALWA KI 'MAA'</div><div class="title">AHILYABAI</div><div class="title title2">HOLKAR</div><div class="rule"></div></div>`,
  (T, D) => `
    tl.fromTo("#g-title .kicker", {opacity:0, y:20}, {opacity:1, y:0, duration:.5, ease:"power3.out"}, ${T});
    tl.fromTo("#g-title .title", {opacity:0, scale:1.6, filter:"blur(10px)"}, {opacity:1, scale:1, filter:"blur(0px)", duration:.6, ease:"power4.out", stagger:.18}, ${T + 0.15});
    tl.fromTo("#g-title .rule", {scaleX:0}, {scaleX:1, duration:.7, ease:"power3.inOut"}, ${T + 0.6});
    tl.to("#g-title .title-wrap", {scale:1.05, duration:${D}, ease:"none"}, ${T});
    tl.fromTo("#g-title .title-wrap", {opacity:1}, {opacity:0, duration:.35, ease:"power2.in", immediateRender:false}, ${T + D - 0.35});`);
sfx.push(["impact-bass-1", 0.3, 0.4]);

// timeline 1725 -> 1795
gfx("g-timeline", 5.44, 55.8, "g-bar", `<div class="tbar"><span class="tlabel">1725</span><div class="track"><div class="fill" id="g-fill"></div><div class="rail" id="g-dot"><div class="dot"></div></div></div><span class="tlabel">1795</span></div>`,
  (T, D) => `
    tl.fromTo("#g-timeline .tbar", {opacity:0, y:-20}, {opacity:1, y:0, duration:.5, ease:"power3.out"}, ${T});
    tl.fromTo("#g-fill", {scaleX:0}, {scaleX:1, duration:${fmt(51.62 - T)}, ease:"none"}, ${T});
    tl.fromTo("#g-dot", {xPercent:0}, {xPercent:100, duration:${fmt(51.62 - T)}, ease:"none"}, ${T});
    tl.to("#g-timeline .tbar", {opacity:0, duration:.4}, ${T + D - 0.4});`);

// 2 — born 1725, Chondi
year("g-1725", 5.44, 8.0, "1725", false, `<div class="loc" id="g-chondi" style="opacity:0"><span class="pin"></span><div><b>CHONDI</b><span>Ek chhota sa gaon</span></div></div>`, pop("#g-chondi", 4.44 + 0.05 > 5.44 ? 5.9 : 5.9));

// 3 — Malhar Rao Holkar
plate("g-malhar", 10.44, 12.55, "l", "MALHAR RAO HOLKAR", "Holkar raj ke sansthapak");
ribbon("g-seva", 8.5, 10.3, "SEVA · SADGI");

// 4 — marriage
plate("g-khande", 12.62, 16.95, "r", "KHANDE RAO HOLKAR", "Pati");
ribbon("g-bahu", 15.2, 16.95, "HOLKAR PARIVAR KI BAHU");

// 5 — 1754, husband lost in war
year("g-1754", 17.34, 20.95, "1754", true, `<div class="chip-red" id="g-yuddh" style="opacity:0">PATI KHANDE RAO · YUDDH</div>`, pop("#g-yuddh", 19.06));
sfx.push(["impact-bass-2", 17.34, 0.35]);

// 6 — trained by Malhar Rao
plate("g-sasur", 21.4, 24.05, "l", "MALHAR RAO", "Sasur · Guru");
ribbon("g-kaam", 22.72, 24.05, "RAJ KE KAAM", true);

// 7 — 1767, son Male Rao
year("g-1767", 24.16, 28.2, "1767", true);
plate("g-male", 26.92, 28.2, "r", "MALE RAO HOLKAR", "Beta", true);
sfx.push(["impact-bass-2", 24.16, 0.35]);

// 8 — she takes charge
ribbon("g-bagdor", 30.38, 32.25, "RAJ KI BAGDOR KHUD SAMBHALI", true);

// 9 — Maheshwar on the Narmada
gfx("g-mahesh", 34.06, 36.4, "g-top2", `<div class="loc"><span class="pin"></span><div><b>MAHESHWAR</b><span>Narmada ke kinare · Rajdhani</span></div></div>`,
  (T, D) => `tl.fromTo("#g-mahesh .loc", {opacity:0, y:-40}, {opacity:1, y:0, duration:.5, ease:"back.out(1.8)"}, ${T});${outT("#g-mahesh .loc", T, D)}`);

// 10 — justice in the darbar
ribbon("g-nyay", 37.08, 39.5, "ROZ DARBAR · KHUD NYAY");

// 11 — wells, roads, rest houses
gfx("g-build", 40.54, 43.3, "g-top2 col", `${[["a","KUEN"],["b","SADKEIN"],["c","DHARAMSHALAYEIN"]].map(([k,t]) => `<div class="ribbon ribbon2" id="g-b${k}" style="opacity:0">${t}</div>`).join("")}`,
  (T, D) => `${pop("#g-ba", 40.54)}${pop("#g-bb", 41.12)}${pop("#g-bc", 41.92)}${outT("#g-build > *", T, D)}`);

// 12 — Kashi to Somnath
gfx("g-route", 43.4, 47.4, "g-top2 col", `<div class="route-row"><span>KASHI</span><i></i><span>SOMNATH</span></div><div class="ribbon ribbon2" id="g-mandir" style="opacity:0">MANDIR · GHAT</div>`,
  (T, D) => `tl.fromTo("#g-route .route-row", {opacity:0, y:-30}, {opacity:1, y:0, duration:.45, ease:"power3.out"}, ${T});
    tl.fromTo("#g-route .route-row i", {scaleX:0}, {scaleX:1, duration:.6, ease:"power2.inOut"}, 43.8);${pop("#g-mandir", 45.58)}${outT("#g-route > *", T, D)}`);

// 13 — Maheshwar weavers
ribbon("g-bunkar", 48.22, 51.5, "MAHESHWAR KE BUNKAR");

// 14 — 1795, name immortal
year("g-1795", 51.62, 55.85, "1795", false, `<div class="ribbon" id="g-amar" style="opacity:0">NAAM AMAR HO GAYA</div>`, pop("#g-amar", 55.0));

// 15 — Punyashlok
gfx("g-fin", 56.4, END, "g-top2", `<div class="finale"><div class="fin-k">AAJ BHI YAAD KARTE HAIN</div><div class="fin-t" id="g-fin-t" style="opacity:0">PUNYASHLOK<br>AHILYABAI</div></div>`,
  (T, D) => `tl.fromTo("#g-fin .fin-k", {opacity:0, y:20}, {opacity:1, y:0, duration:.5, ease:"power3.out"}, ${T});
    tl.fromTo("#g-fin-t", {opacity:0, scale:1.5, filter:"blur(8px)"}, {opacity:1, scale:1, filter:"blur(0px)", duration:.6, ease:"power4.out", immediateRender:false}, 57.16);`);
sfx.push(["impact-bass-2", 56.8, 0.45]);

// grief tints for the two losses
tl.push(`tl.fromTo("#cold", {opacity:0}, {opacity:.3, duration:.8, immediateRender:false}, 17.1);`);
tl.push(`tl.to("#cold", {opacity:0, duration:.6}, 20.9);`);
tl.push(`tl.fromTo("#cold", {opacity:0}, {opacity:.35, duration:.8, immediateRender:false}, 24.16);`);
tl.push(`tl.to("#cold", {opacity:0, duration:1.2}, 28.2);`);

// final fade
tl.push(`tl.fromTo("#fade", {opacity:0}, {opacity:1, duration:.7, ease:"power1.in", immediateRender:false}, ${fmt(END - 0.7)});`);

// ---------- captions ----------
const KEY = /^(malwa|'maa'|chondi|1725|ahilyabai|seva|sadgi|malhar|holkar|khande|bahu|1754|yuddh|1767|male|bagdor|narmada|maheshwar|rajdhani|darbar|nyay|kuen|sadkein|dharamshalayein|kashi|somnath|mandir|ghat|bunkaron|kala|1795|amar|'punyashlok')$/i;
const groups = [];
let cur = [];
words.forEach((w, i) => {
  cur.push(w);
  const nxt = words[i + 1];
  const punct = /[.,!?…—]$|\.\.\.$/.test(w.text);
  const gap = nxt ? nxt.start - w.end : 1;
  if (cur.length >= 3 || punct || gap > 0.25 || !nxt) {
    groups.push(cur);
    cur = [];
  }
});
const caps = groups.map((g, gi) => {
  const id = `cap-${gi}`;
  const start = fmt(g[0].start - 0.05);
  const nextStart = groups[gi + 1] ? groups[gi + 1][0].start - 0.05 : END - 0.8;
  const end = fmt(Math.min(nextStart, g[g.length - 1].end + 0.6));
  tl.push(`tl.fromTo("#${id} .cap-in", {opacity:0, y:24, scale:.92}, {opacity:1, y:0, scale:1, duration:.14, ease:"back.out(2)"}, ${start});`);
  const spans = g
    .map((w, j) => {
      const clean = w.text.replace(/\.\.\.$/, "").replace(/[.,!?]$/, "").toUpperCase();
      const key = KEY.test(clean.replace(/[^A-Z0-9-]/gi, ""));
      tl.push(`tl.fromTo("#${id}-w${j}", {color:"${key ? "#F2C14E" : "#FFFFFF"}", scale:1}, {color:"#FFD86B", scale:1.12, duration:.08, ease:"power2.out", immediateRender:false}, ${fmt(w.start)});`);
      tl.push(`tl.to("#${id}-w${j}", {color:"${key ? "#F2C14E" : "#FFFFFF"}", scale:1, duration:.12}, ${fmt(Math.max(w.start + 0.09, w.end))});`);
      return `<span class="cw" id="${id}-w${j}" style="color:${key ? "#F2C14E" : "#FFFFFF"}">${clean}</span>`;
    })
    .join(" ");
  return `      <div class="cap clip" id="${id}" data-start="${start}" data-duration="${fmt(end - start)}" data-track-index="5"><div class="cap-in">${spans}</div></div>`;
}).join("\n");

// ---------- audio ----------
const SFX_LEN = { whoosh: 1.2, "whoosh-cinematic": 1.6, "impact-bass-1": 2.12, "impact-bass-2": 2.59, riser: 4, sparkle: 1.5, chime: 2.5, "glitch-3": 1.5 };
const KEEP_SFX = [[0.3, "impact-bass-1"], [17.34, "impact-bass-2"], [24.16, "impact-bass-2"], [56.8, "impact-bass-2"]];
const sfxKept = sfx.filter(([f, t]) => KEEP_SFX.some(([kt, kf]) => Math.abs(kt - t) < 0.05 && kf === f));
const sfxHtml = sfxKept
  .sort((a, b) => a[1] - b[1])
  .map(([f, t, v, ms, d], i) => {
    const start = Math.max(0, fmt(t));
    const dur = fmt(Math.min(d ?? SFX_LEN[f] ?? 1, END - start));
    return `      <audio id="sfx-${i}" src="assets/sfx/${f}.mp3" data-start="${start}" data-duration="${dur}"${ms ? ` data-media-start="${ms}"` : ""} data-track-index="${20 + (i % 4)}" data-volume="${v}"></audio>`;
  })
  .join("\n");

const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>Ahilyabai Holkar</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Cinzel"; font-weight: 700; src: url("assets/fonts/cinzel-latin-700-normal.woff2") format("woff2"); }
      @font-face { font-family: "Cinzel"; font-weight: 900; src: url("assets/fonts/cinzel-latin-900-normal.woff2") format("woff2"); }
      @font-face { font-family: "Montserrat"; font-weight: 800; src: url("assets/fonts/montserrat-latin-800-normal.woff2") format("woff2"); }
      @font-face { font-family: "Montserrat"; font-weight: 900; src: url("assets/fonts/montserrat-latin-900-normal.woff2") format("woff2"); }
      :root { --gold: #F2C14E; --gold2: #FFE29A; --red: #B3261E; --ink: #120C06; }
      body { margin: 0; background: #000; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; font-family: "Montserrat", sans-serif; color: #fff; }
      .seg { position: absolute; inset: 0; overflow: hidden; }
      .kb, .tx { position: absolute; inset: 0; transform-origin: 50% 45%; }
      .seg video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      #grade { position: absolute; inset: 0; z-index: 100; pointer-events: none;
        background: linear-gradient(180deg, rgba(10,6,2,.55) 0%, rgba(10,6,2,0) 22%, rgba(10,6,2,0) 58%, rgba(10,6,2,.7) 100%); }
      #vignette { position: absolute; inset: 0; z-index: 101; background: radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 50%, rgba(0,0,0,.55) 100%); }
      #redwash { position: absolute; inset: 0; z-index: 102; opacity: 0; background: radial-gradient(ellipse at 50% 50%, rgba(140,10,10,.2) 30%, rgba(120,0,0,.85) 100%); mix-blend-mode: multiply; }
      #cold { position: absolute; inset: 0; z-index: 102; opacity: 0; background: #2a3a55; mix-blend-mode: color; }
      #leak { position: absolute; inset: -10%; z-index: 103; opacity: 0;
        background: radial-gradient(ellipse at 30% 40%, rgba(255,200,90,.9) 0%, rgba(255,140,40,.5) 30%, rgba(255,120,0,0) 65%); mix-blend-mode: screen; }
      #flash { position: absolute; inset: 0; z-index: 400; opacity: 0; background: radial-gradient(circle at 50% 45%, #FFF6D8 0%, #F2C14E 70%); }
      #dip { position: absolute; inset: 0; z-index: 401; opacity: 0; background: #000; }
      #fade { position: absolute; inset: 0; z-index: 500; opacity: 0; background: #000; }

      .gfx { position: absolute; left: 0; right: 0; z-index: 300; display: flex; justify-content: center; }
      .g-top { top: 300px; height: 700px; align-items: flex-start; }
      .g-top2 { top: 200px; height: 560px; align-items: flex-start; }
      .g-bar { top: 90px; height: 80px; align-items: center; }
      .g-plate-l { top: 1020px; height: 160px; justify-content: flex-start; padding-left: 60px; }
      .g-plate-r { top: 1190px; height: 160px; justify-content: flex-end; padding-right: 60px; }

      .title-wrap { display: flex; flex-direction: column; align-items: center; padding: 40px 60px; border-radius: 40px; filter: drop-shadow(0 8px 20px rgba(0,0,0,.95)); background: radial-gradient(ellipse at 50% 50%, rgba(10,6,2,.75) 0%, rgba(10,6,2,.45) 55%, rgba(10,6,2,0) 75%); }
      .kicker { display: block; font-weight: 800; font-size: 38px; letter-spacing: 10px; color: var(--gold2); text-shadow: 0 4px 20px rgba(0,0,0,.8); }
      .title { display: block; font-family: "Cinzel"; font-weight: 900; font-size: 136px; line-height: 1; color: var(--gold);
        background: linear-gradient(180deg, #FFF1C4 0%, #F2C14E 45%, #B57A1A 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
      .title2 { font-size: 132px; }
      .rule { display: block; width: 640px; height: 6px; margin-top: 18px; background: linear-gradient(90deg, rgba(242,193,78,0), #F2C14E, rgba(242,193,78,0)); }

      .tbar { display: flex; align-items: center; gap: 20px; width: 920px; }
      .tlabel { display: block; font-weight: 900; font-size: 28px; color: var(--gold2); letter-spacing: 2px; text-shadow: 0 2px 10px rgba(0,0,0,.9); flex: none; }
      .track { position: relative; flex: 1; height: 8px; border-radius: 4px; background: rgba(255,255,255,.25); }
      .fill { position: absolute; left: 0; top: 0; width: 100%; height: 100%; border-radius: 4px; background: var(--gold); transform-origin: 0 50%; }
      .rail { position: absolute; left: 0; top: 0; width: 100%; height: 100%; }
      .dot { position: absolute; left: 0; top: 50%; width: 26px; height: 26px; margin: -13px 0 0 -13px; border-radius: 50%; background: #FFF1C4; box-shadow: 0 0 18px #F2C14E; }

      .year { display: block; font-family: "Cinzel"; font-weight: 900; font-size: 170px; color: var(--gold); text-shadow: 0 10px 40px rgba(0,0,0,.85); }
      .year small { font-size: 80px; }
      .year-red { color: #FF6A4D; }
      .plate { display: flex; flex-direction: column; gap: 6px; padding: 20px 30px; border-left: 8px solid var(--gold); background: rgba(12,8,4,.78); box-shadow: 0 12px 30px rgba(0,0,0,.5); }
      .plate b { display: block; font-family: "Cinzel"; font-weight: 900; font-size: 50px; color: #fff; }
      .plate span { display: block; font-weight: 800; font-size: 28px; color: var(--gold2); letter-spacing: 1px; }
      .plate-r { border-left: 0; border-right: 8px solid var(--gold); text-align: right; align-items: flex-end; }
      .plate-red { border-color: #FF6A4D; }
      .loc { display: flex; align-items: center; gap: 24px; padding: 22px 40px; border-radius: 20px; background: rgba(12,8,4,.78); border: 2px solid rgba(242,193,78,.6); }
      .loc b { display: block; font-family: "Cinzel"; font-weight: 900; font-size: 76px; color: var(--gold); line-height: 1; }
      .loc span { display: block; font-weight: 800; font-size: 30px; color: #eee; margin-top: 8px; }
      .pin { display: block; flex: none; width: 52px; height: 52px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); background: var(--gold); }
      .ribbon { display: block; padding: 18px 44px; margin: 0 auto 18px; font-family: "Cinzel"; font-weight: 900; font-size: 60px; color: var(--ink);
        background: linear-gradient(90deg, #B57A1A, #F2C14E, #FFF1C4, #F2C14E, #B57A1A); box-shadow: 0 12px 30px rgba(0,0,0,.5); }
      #g-sel { flex-direction: column; align-items: center; justify-content: flex-start; }
      .ribbon2 { font-size: 46px; white-space: nowrap; background: rgba(12,8,4,.85); color: var(--gold); border: 2px solid var(--gold); }
      #g-ash { flex-direction: column; align-items: center; }
      .name-big { display: block; font-family: "Cinzel"; font-weight: 900; font-size: 190px; line-height: 1; color: #fff; text-shadow: 0 10px 50px rgba(0,0,0,.9), 0 0 30px rgba(242,193,78,.5); }
      .chip-red { display: block; margin-top: 16px; padding: 14px 36px; border-radius: 999px; background: var(--red); font-weight: 900; font-size: 44px; letter-spacing: 6px; }
      .dhamma { display: flex; flex-direction: column; align-items: center; }
      .chakra { display: block; width: 300px; height: 300px; fill: none; stroke: #6FA8FF; stroke-width: 5; filter: drop-shadow(0 0 18px rgba(111,168,255,.8)); }
      .dh-word { display: block; font-family: "Cinzel"; font-weight: 900; font-size: 150px; line-height: 1.1; color: #FFF1C4; text-shadow: 0 0 40px rgba(242,193,78,.9), 0 8px 30px rgba(0,0,0,.8); }
      .dh-sub { display: block; font-weight: 800; font-size: 32px; color: #fff; text-shadow: 0 4px 16px rgba(0,0,0,.9); }
      .decline { display: flex; align-items: center; gap: 24px; padding: 22px 40px; border-radius: 20px; background: rgba(8,10,16,.8); border: 2px solid rgba(160,180,220,.5); }
      .decline b { display: block; font-family: "Cinzel"; font-weight: 900; font-size: 60px; color: #DDE6F5; }
      .decline span { display: block; font-weight: 800; font-size: 30px; color: #9FB0CC; margin-top: 6px; }
      .arrow-dn { display: block; font-size: 80px; color: #FF6A4D; }
      .stats { display: flex; flex-direction: column; gap: 16px; width: 640px; }
      .stat { display: flex; align-items: center; justify-content: space-between; padding: 18px 34px; border-radius: 18px; background: rgba(8,10,16,.82); border: 2px solid rgba(160,180,220,.4); }
      .stat b { display: block; font-family: "Cinzel"; font-weight: 900; font-size: 58px; color: #EEF2FA; }
      .stat i { display: block; font-style: normal; font-weight: 900; font-size: 56px; }
      .up { color: #FF6A4D; } .dn { color: #7FB0FF; }
      .finale { display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 36px 50px; border-radius: 36px; filter: drop-shadow(0 8px 20px rgba(0,0,0,.95)); background: radial-gradient(ellipse at 50% 50%, rgba(10,6,2,.8) 0%, rgba(10,6,2,.5) 55%, rgba(10,6,2,0) 78%); }
      .fin-k { display: block; font-weight: 900; font-size: 40px; letter-spacing: 6px; color: #fff; text-shadow: 0 4px 20px rgba(0,0,0,.9); }
      .fin-t { display: block; text-align: center; font-family: "Cinzel"; font-weight: 900; font-size: 86px; line-height: 1.1;
        background: linear-gradient(180deg, #FFF1C4 0%, #F2C14E 50%, #B57A1A 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }

      .cap { position: absolute; left: 50px; right: 50px; top: 1330px; height: 260px; z-index: 350; display: flex; align-items: center; justify-content: center; }
      .cap-in { display: block; max-width: 960px; text-align: center; font-weight: 900; font-size: 78px; line-height: 1.1; letter-spacing: -1px;
        -webkit-text-stroke: 10px #120C06; paint-order: stroke fill; text-shadow: 0 8px 24px rgba(0,0,0,.7); }
      .g-hook { top: 10px; height: 430px; align-items: flex-start; }
      #g-title .title2 { font-size: 104px; }
      .route-row { display: flex; align-items: center; gap: 22px; padding: 20px 40px; border-radius: 20px; background: rgba(12,8,4,.78); border: 2px solid rgba(242,193,78,.6); }
      .route-row span { display: block; font-family: "Cinzel"; font-weight: 900; font-size: 64px; color: var(--gold); }
      .route-row i { display: block; width: 200px; height: 6px; background: linear-gradient(90deg, #F2C14E, #FFF1C4); transform-origin: 0 50%; }
      .col { flex-direction: column; align-items: center; gap: 18px; }
      .year-sm { font-size: 96px; }
      .name-mid { font-size: 92px; margin-top: 10px; }
      .name-glow { color: #FFF1C4; text-shadow: 0 0 40px rgba(242,193,78,.9), 0 8px 30px rgba(0,0,0,.85); }
      .cw { display: inline-block; margin: 0 .2em; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="${END}">
${footage}
      <div id="grade"></div>
      <div id="vignette"></div>
      <div id="redwash"></div>
      <div id="cold"></div>
      <div id="leak"></div>
${G.join("\n")}
${caps}
      <div id="flash"></div>
      <div id="dip"></div>
      <div id="fade"></div>
      <audio id="voiceover" src="assets/audio/voiceover-master.mp3" data-start="0" data-duration="60.3" data-track-index="10" data-volume="1"></audio>
      <audio id="score" src="assets/audio/score.mp3" data-start="0" data-duration="${END}" data-track-index="11" data-volume="0.32"></audio>
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
