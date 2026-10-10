// Generates ../index.html for "Maurya Samrajya — Rise & Fall" (60s Hinglish Reel).
//   node build/build.mjs
// Timing comes from the ElevenLabs voiceover (build/words.json, Scribe word timestamps).
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const words = JSON.parse(readFileSync(join(here, "words.json"), "utf8"));
const fmt = (n) => +(+n).toFixed(3);

// Scene starts (output seconds) — must match build/preprocess.sh
const S = [0, 6.16, 12.92, 17.8, 22.7, 28.28, 34.62, 39.28, 43.8, 51.18];
const END = 58.6;
const HANDLE = 0.3; // each prepped clip starts 0.3s before its scene (crossfade handle)

// transition INTO scene i (i >= 1)
const TRANS = [null, "goldflash", "zoom", "whip", "darkdip", "lightleak", "fade", "zoom", "darkdip", "goldflash"];

const tl = [];
const sfx = []; // [file, time, volume, mediaStart?, duration?]

// ---------- footage ----------
const footage = S.map((s, i) => {
  const start = i === 0 ? 0 : fmt(s - HANDLE);
  const next = i < 9 ? S[i + 1] : END;
  const end = i < 9 ? next + HANDLE : END;
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

// 1 — hook title
gfx("g-title", 0.25, 5.95, "g-top", `<div class="title-wrap"><div class="kicker">THE RISE &amp; FALL OF THE</div><div class="title">MAURYA</div><div class="title title2">SAMRAJYA</div><div class="rule"></div></div>`,
  (T, D) => `
    tl.fromTo("#g-title .kicker", {opacity:0, y:20}, {opacity:1, y:0, duration:.5, ease:"power3.out"}, ${T});
    tl.fromTo("#g-title .title", {opacity:0, scale:1.6, filter:"blur(10px)"}, {opacity:1, scale:1, filter:"blur(0px)", duration:.6, ease:"power4.out", stagger:.18}, ${T + 0.15});
    tl.fromTo("#g-title .rule", {scaleX:0}, {scaleX:1, duration:.7, ease:"power3.inOut"}, ${T + 0.6});
    tl.to("#g-title .title-wrap", {scale:1.05, duration:${D}, ease:"none"}, ${T});
    tl.fromTo("#g-title .title-wrap", {opacity:1}, {opacity:0, duration:.35, ease:"power2.in", immediateRender:false}, ${T + D - 0.35});`);
sfx.push(["impact-bass-1", 0.3, 0.45]);

// timeline bar (321 BCE -> 185 BCE) across the story
gfx("g-timeline", 6.4, 56.9, "g-bar", `<div class="tbar"><span class="tlabel">321 BCE</span><div class="track"><div class="fill" id="g-fill"></div><div class="rail" id="g-dot"><div class="dot"></div></div></div><span class="tlabel">185 BCE</span></div>`,
  (T, D) => `
    tl.fromTo("#g-timeline .tbar", {opacity:0, y:-20}, {opacity:1, y:0, duration:.5, ease:"power3.out"}, ${T});
    tl.fromTo("#g-fill", {scaleX:0}, {scaleX:1, duration:${fmt(51.18 - T)}, ease:"none"}, ${T});
    tl.fromTo("#g-dot", {xPercent:0}, {xPercent:100, duration:${fmt(51.18 - T)}, ease:"none"}, ${T});
    tl.to("#g-timeline .tbar", {opacity:0, duration:.4}, ${T + D - 0.4});`);

// 2 — 321 BCE + name plates
gfx("g-321", 6.9, 12.7, "g-top2", `<div class="year">321 <small>BCE</small></div>`,
  (T, D) => `tl.fromTo("#g-321 .year", {opacity:0, scale:2.2}, {opacity:1, scale:1, duration:.4, ease:"power4.out"}, ${T});${outT("#g-321 .year", T, D)}`);
sfx.push(["impact-bass-1", 6.9, 0.3]);
gfx("g-cg", 8.88, 12.7, "g-plate-l", `<div class="plate"><b>CHANDRAGUPTA MAURYA</b><span>Maurya vansh ke sansthapak</span></div>`,
  (T, D) => `tl.fromTo("#g-cg .plate", {opacity:0, x:-80}, {opacity:1, x:0, duration:.45, ease:"power3.out"}, ${T});${outT("#g-cg .plate", T, D)}`);
gfx("g-ch", 10.08, 12.7, "g-plate-r", `<div class="plate plate-r"><b>CHANAKYA</b><span>Guru aur rananeetikar</span></div>`,
  (T, D) => `tl.fromTo("#g-ch .plate", {opacity:0, x:80}, {opacity:1, x:0, duration:.45, ease:"power3.out"}, ${T});${outT("#g-ch .plate", T, D)}`);

// 3 — Pataliputra
gfx("g-pat", 13.0, 17.6, "g-top2", `<div class="loc"><span class="pin"></span><div><b>PATALIPUTRA</b><span>Maurya rajdhani · Magadha</span></div></div>`,
  (T, D) => `tl.fromTo("#g-pat .loc", {opacity:0, y:-40}, {opacity:1, y:0, duration:.5, ease:"back.out(1.8)"}, ${T});
    tl.fromTo("#g-pat .pin", {scale:0}, {scale:1, duration:.4, ease:"back.out(3)"}, ${T + 0.2});${outT("#g-pat .loc", T, D)}`);

// 4 — Seleucus treaty
gfx("g-sel", 17.9, 22.5, "g-top2", `<div class="ribbon">SELEUCUS SE SANDHI</div><div class="ribbon ribbon2" id="g-sel-2">+ HATHI = NAYI TAAKAT</div>`,
  (T, D) => `tl.fromTo("#g-sel .ribbon", {opacity:0, scaleX:0}, {opacity:1, scaleX:1, duration:.45, ease:"power3.out"}, ${T});
    tl.fromTo("#g-sel-2", {opacity:0, scaleX:0}, {opacity:1, scaleX:1, duration:.4, ease:"back.out(2)", immediateRender:false}, ${fmt(20.68)});${outT("#g-sel .ribbon", T, D)}`);
sfx.push(["impact-bass-1", 20.68, 0.3]);

// 5 — Ashoka / Kalinga
gfx("g-ash", 23.3, 28.1, "g-top2", `<div class="name-big">ASHOKA</div><div class="chip-red" id="g-kal">KALINGA YUDDH</div>`,
  (T, D) => `tl.fromTo("#g-ash .name-big", {opacity:0, scale:1.8, filter:"blur(8px)"}, {opacity:1, scale:1, filter:"blur(0px)", duration:.5, ease:"power4.out"}, ${T});
    tl.fromTo("#g-kal", {opacity:0, y:20}, {opacity:1, y:0, duration:.35, ease:"power3.out"}, ${fmt(24.21)});${outT("#g-ash .name-big, #g-kal", T, D)}`);
// red "blood" pulse on "itna khoon"
tl.push(`tl.fromTo("#redwash", {opacity:0}, {opacity:.55, duration:.25, ease:"power2.out", immediateRender:false}, 26.64);`);
tl.push(`tl.to("#redwash", {opacity:0, duration:1.2, ease:"power2.inOut"}, 27.0);`);
sfx.push(["impact-bass-2", 26.3, 0.4]);

// 6 — Dhamma + Ashoka Chakra
const spokes = Array.from({ length: 24 }, (_, k) => `<line x1="100" y1="100" x2="${fmt(100 + 82 * Math.cos((k * Math.PI) / 12))}" y2="${fmt(100 + 82 * Math.sin((k * Math.PI) / 12))}"/>`).join("");
gfx("g-dh", 29.9, 34.5, "g-top2", `<div class="dhamma"><svg class="chakra" viewBox="0 0 200 200"><circle cx="100" cy="100" r="88"/><circle cx="100" cy="100" r="14"/>${spokes}</svg><div class="dh-word">DHAMMA</div><div class="dh-sub">Ashoka ke shilalekh · aaj bhi zinda</div></div>`,
  (T, D) => `tl.fromTo("#g-dh .chakra", {opacity:0, scale:.4, rotate:-90}, {opacity:1, scale:1, rotate:0, duration:.8, ease:"power3.out"}, ${T});
    tl.to("#g-dh .chakra", {rotate:120, duration:${fmt(D - 0.8)}, ease:"none"}, ${T + 0.8});
    tl.fromTo("#g-dh .dh-word", {opacity:0, y:20}, {opacity:1, y:0, duration:.6, ease:"power3.out"}, ${T + 0.2});
    tl.fromTo("#g-dh .dh-sub", {opacity:0}, {opacity:1, duration:.5}, ${fmt(31.04)});${outT("#g-dh .dhamma", T, D, 0.4)}`);
sfx.push(["chime", 29.92, 0.3]);

// 7 — decline begins
gfx("g-dec", 34.8, 39.1, "g-top2", `<div class="decline"><span class="arrow-dn">▼</span><div><b>PATAN KI SHURUAAT</b><span>Kamzor uttaradhikari</span></div></div>`,
  (T, D) => `tl.fromTo("#g-dec .decline", {opacity:0, y:-40}, {opacity:1, y:0, duration:.5, ease:"power3.out"}, ${T});
    tl.fromTo("#g-dec .arrow-dn", {y:-30}, {y:0, duration:.6, ease:"bounce.out"}, ${T + 0.2});${outT("#g-dec .decline", T, D)}`);
// cold desaturation through the decline section
tl.push(`tl.fromTo("#cold", {opacity:0}, {opacity:.35, duration:1.2, ease:"sine.inOut", immediateRender:false}, 34.6);`);
tl.push(`tl.to("#cold", {opacity:0, duration:1.0, ease:"sine.inOut"}, 50.6);`);

// 8 — treasury stats
gfx("g-tre", 39.3, 43.7, "g-top2", `<div class="stats">
    <div class="stat" id="g-st1"><b>KHARCHA</b><i class="up">▲</i></div>
    <div class="stat" id="g-st2"><b>KHAZANA</b><i class="dn">▼</i></div>
    <div class="stat" id="g-st3"><b>PRANT</b><i class="dn">⇠ ⇢</i></div></div>`,
  (T, D) => `${[["g-st1", 39.31], ["g-st2", 40.13], ["g-st3", 41.84]].map(([id, t]) => `
    tl.fromTo("#${id}", {opacity:0, x:-60}, {opacity:1, x:0, duration:.35, ease:"back.out(1.8)"}, ${t});`).join("")}${outT("#g-tre .stats", T, D)}`);
sfx.push(["whoosh", 39.2, 0.25], ["whoosh", 40.0, 0.25], ["whoosh", 41.7, 0.25]);

// 9 — 185 BCE + Pushyamitra
gfx("g-185", 44.48, 50.9, "g-top2", `<div class="year year-red">185 <small>BCE</small></div>`,
  (T, D) => `tl.fromTo("#g-185 .year", {opacity:0, scale:2.2}, {opacity:1, scale:1, duration:.4, ease:"power4.out"}, ${T});${outT("#g-185 .year", T, D)}`);
sfx.push(["impact-bass-1", 44.48, 0.4]);
gfx("g-pu", 47.0, 50.9, "g-plate-l", `<div class="plate plate-red"><b>PUSHYAMITRA SHUNGA</b><span>Maurya senapati</span></div>`,
  (T, D) => `tl.fromTo("#g-pu .plate", {opacity:0, x:-80}, {opacity:1, x:0, duration:.45, ease:"power3.out"}, ${T});${outT("#g-pu .plate", T, D)}`);
gfx("g-br", 49.48, 50.9, "g-plate-r", `<div class="plate plate-r"><b>BRIHADRATHA</b><span>Antim Maurya raja</span></div>`,
  (T, D) => `tl.fromTo("#g-br .plate", {opacity:0, x:80}, {opacity:1, x:0, duration:.4, ease:"power3.out"}, ${T});${outT("#g-br .plate", T, D, 0.25)}`);
sfx.push(["riser", 47.18, 0.3, 6.03, 4.0]);

// 10 — lion capital finale
gfx("g-fin", 53.04, 58.6, "g-top2", `<div class="finale"><div class="fin-k">ASHOKA KA SHER-STAMBH</div><div class="fin-t" id="g-fin-t">BHARAT KA<br>RASHTRIYA CHINH</div></div>`,
  (T, D) => `tl.fromTo("#g-fin .fin-k", {opacity:0, y:20}, {opacity:1, y:0, duration:.5, ease:"power3.out"}, ${T});
    tl.fromTo("#g-fin-t", {opacity:0, scale:1.5, filter:"blur(8px)"}, {opacity:1, scale:1, filter:"blur(0px)", duration:.6, ease:"power4.out", immediateRender:false}, 55.8);`);
sfx.push(["impact-bass-2", 55.45, 0.45], ["chime", 55.8, 0.35]);

// final fade
tl.push(`tl.fromTo("#fade", {opacity:0}, {opacity:1, duration:.7, ease:"power1.in", immediateRender:false}, ${fmt(END - 0.7)});`);

// ---------- captions ----------
const KEY = /^(samrajya|bharat|chandragupta|maurya|chanakya|nanda|pataliputra|rajdhani|seleucus|hathi|taakat|ashoka|kalinga|khoon|dard|dhamma|zinda|kamzor|bojh|khazana|khali|pushyamitra|shunga|brihadratha|sher-stambh|rashtriya|chinh|321|185|bce)$/i;
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
const sfxHtml = sfx
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
    <title>Maurya Samrajya Reel</title>
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
      .title { display: block; font-family: "Cinzel"; font-weight: 900; font-size: 178px; line-height: 1; color: var(--gold);
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
      .ribbon2 { font-size: 46px; background: rgba(12,8,4,.85); color: var(--gold); border: 2px solid var(--gold); }
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
      <audio id="voiceover" src="assets/audio/voiceover.mp3" data-start="0" data-duration="57.1" data-track-index="10" data-volume="1"></audio>
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
