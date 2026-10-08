// Generates ../index.html for the DLF Cyber City recut.
// All times below are SOURCE seconds (media/enhanced.mp4); they are mapped to
// output time after the dead-air trims in REMOVE.
//   node build/build.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const SRC_END = 60.7;

// Dead air removed from the source (pauses found with silencedetect).
const REMOVE = [
  [0.0, 0.35],
  [5.22, 5.5],
  [9.68, 10.25],
  [15.72, 16.05],
  [18.98, 19.45],
  [19.72, 20.1],
  [21.78, 22.12],
  [23.8, 24.85],
  [25.95, 26.22],
  [28.62, 29.4],
  [37.95, 38.28],
  [39.7, 39.98],
  [50.4, 51.02],
  [52.08, 52.34],
];
// Hard cuts already in the source footage (scene detection).
const SCENE_CUTS = [5.517, 9.633, 12.983, 15.867, 24.083, 28.6, 32.533, 49.317, 54.467];

for (const r of REMOVE) for (const c of SCENE_CUTS) if (c >= r[0] - 0.1 && c < r[0]) r[0] = c;
const cutAt = (a, b) => SCENE_CUTS.some((c) => c >= a - 0.01 && c <= b + 0.01);

// Map a source time to output time (times inside a removed gap land on its end).
function map(t) {
  let out = t;
  for (const [a, b] of REMOVE) {
    if (t >= b) out -= b - a;
    else if (t > a) out -= t - a;
  }
  return +out.toFixed(3);
}
const OUT_END = map(SRC_END);

// ---------- footage segments ----------
const keep = [];
let cursor = 0;
for (const [a, b] of REMOVE) {
  if (a > cursor) keep.push([cursor, a]);
  cursor = Math.max(cursor, b);
}
if (cursor < SRC_END) keep.push([cursor, SRC_END]);
// split kept ranges at the source's own scene cuts
const segs = [];
for (const [a, b] of keep) {
  let s = a;
  for (const c of SCENE_CUTS) {
    if (c > s + 0.05 && c < b - 0.05) {
      segs.push({ a: s, b: c, endsAt: "scene" });
      s = c;
    }
  }
  const rem = REMOVE.find((r) => Math.abs(r[0] - b) < 1e-6);
  segs.push({ a: s, b, endsAt: rem && cutAt(rem[0], rem[1]) ? "scene" : "jump" });
}
segs[segs.length - 1].endsAt = "end";
// shot index per segment (changes after a scene cut) and punch-in alternation on jump cuts
let shot = 0;
let punched = false;
segs.forEach((s, i) => {
  s.id = `seg-${i}`;
  s.shot = shot;
  s.scale = punched ? 1.13 : 1.0;
  const f = (t) => Math.round(map(t) * 30);
  s.start = Math.ceil((f(s.a) / 30) * 1e4) / 1e4;
  s.dur = Math.floor(((f(s.b) - f(s.a)) / 30) * 1e4) / 1e4 - 1e-4;
  if (s.endsAt === "scene") {
    shot++;
    punched = false;
  } else if (s.endsAt === "jump") {
    punched = !punched;
  }
});

// transition style per source scene cut (output time computed later)
const TRANSITION = {
  5.517: "whip",
  9.633: "zoom",
  12.983: "zoom",
  15.867: "flash",
  24.083: "whip",
  28.6: "zoom",
  32.533: "flash",
  49.317: "whip",
  54.467: "zoom",
};

// ---------- transcript (from the original burned-in captions) ----------
// [word, sourceStart]; phrase end is the last field.
const PHRASES = [
  [[["DLF", 0.5], ["CYBER", 1.0], ["CITY,", 1.3]], 2.0],
  [[["THE", 2.0], ["IT", 2.3], ["HUB", 2.7]], 3.2],
  [[["FULL", 3.2], ["OF", 3.7], ["IT-ENABLED", 4.0], ["EMPLOYEES", 4.7]], 5.4],
  [[["BUT", 5.6], ["THE", 6.0], ["PROBLEM", 6.7]], 7.0],
  [[["IS", 7.0], ["KOI", 7.2], ["BHI", 7.5]], 8.2],
  [[["THEEK", 8.3], ["SE", 8.5], ["CHARGING", 9.1]], 9.3],
  [[["SOLUTIONS", 9.3], ["NAHI", 9.5]], 9.68],
  [[["PEOPLE", 10.25], ["USE", 10.8], ["ALL", 11.1], ["SORT", 11.2]], 11.5],
  [[["OF", 11.5], ["CHEAP", 11.6]], 11.9],
  [[["AND", 11.9], ["HAZARDOUS", 12.0]], 12.5],
  [[["POWER", 12.5], ["BANKS", 12.8]], 13.1],
  [[["AND", 13.1], ["HERE", 13.3], ["IS", 13.5], ["WHERE", 13.7]], 14.2],
  [[["AMBRANE", 15.1], ["COMES", 15.5], ["IN", 15.8]], 16.05],
  [[["SINCE", 16.1], ["2012,", 16.4]], 17.5],
  [[["AMBRANE", 17.5], ["OWNS", 17.8]], 18.1],
  [[["THE", 18.1], ["CONSUMERS'", 18.2], ["POCKETS", 18.6]], 19.45],
  [[["BUT", 19.5]], 19.72],
  [[["BUT", 20.1], ["CORPORATE", 20.12], ["DESKS", 20.6]], 21.1],
  [[["ARE", 21.1], ["STILL", 21.2], ["EMPTY", 21.5]], 22.12],
  [[["AND", 22.2], ["WE", 22.4], ["ARE", 22.5], ["HERE", 22.6]], 23.0],
  [[["TO", 23.0], ["SOLVE", 23.1], ["THAT", 23.4], ["PROBLEM", 23.5]], 24.0],
  [[["TAREEKA", 25.0], ["SIMPLE", 25.2], ["HAI", 25.3]], 25.95],
  [[["DLF", 26.22], ["JAISE", 26.3], ["DENSELY", 26.4]], 27.2],
  [[["POPULATED", 27.2]], 27.75],
  [[["OFFICES", 27.8], ["MAI", 28.2], ["JAANA", 28.3]], 28.62],
  [[["PROCURE", 29.5], ["THE", 29.9], ["ORDER", 30.1], ["AND", 30.5]], 31.0, "high"],
  [[["HELP", 31.6], ["YOU", 31.9], ["CLOSE", 32.0]], 32.3],
  [[["THE", 32.3], ["DEAL", 32.45]], 32.75],
  [[["WHY", 32.8], ["US?", 33.3]], 33.75],
  [[["WELL,", 33.8], ["WE", 34.5], ["WALK", 34.9], ["IN,", 35.2]], 35.75],
  [[["WE", 35.8], ["QUALIFY,", 36.0]], 36.85],
  [[["WE", 37.0], ["REGISTER", 37.1], ["THE", 37.4], ["LEAD.", 37.5]], 38.3],
  [[["ZERO", 38.4], ["CHANNEL", 38.7], ["CONFLICTS.", 39.0]], 39.98],
  [[["YOUR", 40.0], ["ACQUISITION", 40.4], ["COST?", 41.0]], 41.55],
  [[["ZERO.", 41.6]], 42.15],
  [[["AD", 42.2], ["SPEND?", 42.5]], 43.05],
  [[["ZERO.", 43.1]], 43.7],
  [[["PAYROLL?", 43.8]], 44.55],
  [[["ZERO.", 44.6]], 45.15],
  [[["YOU", 45.2], ["ONLY", 45.5], ["PAY", 46.0], ["US", 46.2]], 46.4],
  [[["A", 46.4], ["PERCENT", 46.5], ["OF", 47.0]], 47.2],
  [[["THE", 47.2], ["REVENUE", 47.3], ["THAT", 47.9]], 48.2],
  [[["WE", 48.2], ["BRING", 48.4], ["TO", 48.7]], 48.8],
  [[["THE", 48.8], ["TABLE.", 48.9]], 49.4],
  [[["FOR", 49.5], ["THE", 49.7], ["NEXT", 49.8]], 50.0],
  [[["TWO", 50.0], ["MONTHS,", 50.2]], 51.05],
  [[["WE", 51.05], ["TAKE", 51.3], ["IT", 51.4], ["AS", 51.6]], 51.7],
  [[["CHALLENGE", 51.7]], 52.36],
  [[["IF", 52.4], ["YOU", 52.6], ["DON'T", 52.7], ["DELIVER,", 52.9]], 53.5],
  [[["YOU", 53.5], ["LOSE", 53.6], ["NOTHING.", 53.8]], 54.45],
  [[["60", 54.8], ["DAYS,", 55.2]], 55.6],
  [[["ZERO", 55.6], ["RISK,", 55.9]], 56.4],
  [[["PURE", 56.4], ["UPSIDE.", 56.7]], 57.35],
  [[["LET'S", 57.4], ["MAKE", 57.7], ["AMBRANE'S", 58.0]], 58.6],
  [[["INDIA", 58.6], ["CORPORATE", 58.9]], 59.3],
  [[["FOOTPRINT", 59.3], ["TOGETHER.", 60.0]], 60.7],
];
// words that always carry the accent colour
const KEY = new Set([
  "PROBLEM", "CHEAP", "HAZARDOUS", "AMBRANE", "AMBRANE'S", "2012,", "EMPTY", "SOLVE", "DEAL",
  "ZERO", "ZERO.", "PERCENT", "REVENUE", "CHALLENGE", "NOTHING.", "60", "UPSIDE.", "TOGETHER.",
  "QUALIFY,", "LEAD.", "SIMPLE",
]);

// ---------- motion graphics (source times) ----------
// Each: { id, a, b, html, anim } — anim is JS added to the timeline at output time T.
// Sound cues: [sound, sourceTime of the on-screen hit, gain]. Every cue has its own sound
// (see build/make-sfx.sh); each file's loudest point lands on the cue time.
const sfx = [
  ["popLight", 0.5, 0.5],
  ["negTap", 6.7, 0.5],
  ["buzzer", 11.6, 0.32],
  ["logo", 15.1, 0.75],
  ["popHard", 17.2, 0.45],
  ["hitFuture", 21.5, 0.55],
  ["popDry", 27.8, 0.5],
  ["popMsg", 29.5, 0.5],
  ["popLong", 32.0, 0.5],
  ["whooshImpact", 32.8, 0.6],
  ["clickBox", 34.9, 0.55],
  ["clickTech", 36.0, 0.55],
  ["clickClassic", 37.1, 0.55],
  ["tickCorrect", 38.4, 0.45],
  ["clickCool", 40.0, 0.5],
  ["hitShort", 41.6, 0.6],
  ["popLight", 42.2, 0.45],
  ["zoomHit", 43.1, 0.55],
  ["popMsg", 43.8, 0.45],
  ["trailerHit", 44.6, 0.6],
  ["sparkle", 46.5, 0.45],
  ["deepImpact", 51.7, 0.6],
  ["positive", 53.8, 0.45],
  ["hitFuture", 54.8, 0.55],
  ["hitShort", 55.6, 0.6],
  ["epicHit", 56.4, 0.6],
  ["whooshC", 57.3, 0.45],
  ["bells", 60.0, 0.45],
];
const tcues = []; // transitions get their sound below
const G = [];
const add = (g) => G.push(g);

add({
  id: "g-loc", a: 0.5, b: 5.22, cls: "top",
  html: `<div class="chip"><span class="pin"></span><span>DLF CYBER CITY</span><span class="chip-sub">GURUGRAM</span></div>`,
  anim: (T, D) => `
    tl.fromTo("#g-loc .chip", {y:-60, opacity:0, scale:.9}, {y:0, opacity:1, scale:1, duration:.5, ease:"back.out(2)"}, ${T});
    tl.fromTo("#g-loc .pin", {scale:0}, {scale:1, duration:.4, ease:"back.out(3)"}, ${T + 0.15});
    tl.to("#g-loc .chip", {y:-40, opacity:0, duration:.3, ease:"power2.in"}, ${T + D - 0.3});`,
});

add({
  id: "g-problem", a: 6.7, b: 9.6, cls: "top",
  html: `<div class="tag tag-red"><span class="warn">!</span><span>THE PROBLEM</span></div>`,
  anim: (T, D) => `
    tl.fromTo("#g-problem .tag", {x:-700}, {x:0, duration:.45, ease:"power4.out"}, ${T});
    tl.fromTo("#g-problem .warn", {rotate:-30, scale:.4}, {rotate:0, scale:1, duration:.5, ease:"back.out(3)"}, ${T + 0.2});
    tl.to("#g-problem .tag", {x:700, duration:.35, ease:"power3.in"}, ${T + D - 0.35});`,
});

add({
  id: "g-hazard", a: 11.6, b: 13.05, cls: "mid",
  html: `<div class="tape"><div class="tape-inner">⚠ CHEAP · HAZARDOUS · POWER BANKS ⚠ CHEAP · HAZARDOUS · POWER BANKS</div></div>`,
  anim: (T, D) => `
    tl.fromTo("#g-hazard .tape", {scaleX:0, rotate:-8}, {scaleX:1, rotate:-6, duration:.35, ease:"power3.out"}, ${T});
    tl.fromTo("#g-hazard .tape-inner", {xPercent:0}, {xPercent:-30, duration:${D}, ease:"none"}, ${T});
    tl.to("#g-hazard .tape", {opacity:0, duration:.2}, ${T + D - 0.2});`,
});

add({
  id: "g-ambrane", a: 15.1, b: 15.72, cls: "center",
  html: `<div class="slam">AMBRANE</div>`,
  anim: (T, D) => `
    tl.fromTo("#g-ambrane .slam", {scale:2.4, opacity:0}, {scale:1, opacity:1, duration:.32, ease:"power4.out"}, ${T});
    tl.to("#g-ambrane .slam", {scale:1.08, duration:${Math.max(0.1, D - 0.32)}, ease:"none"}, ${T + 0.32});`,
});

add({
  id: "g-since", a: 16.1, b: 18.98, cls: "top",
  html: `<div class="since"><div class="since-label">SINCE</div><div class="since-year" id="g-since-year">2000</div><div class="since-sub">IN CONSUMERS' POCKETS</div></div>`,
  anim: (T, D) => `
    tl.fromTo("#g-since .since", {y:-40, opacity:0}, {y:0, opacity:1, duration:.4, ease:"power3.out"}, ${T});
    { const o = {v:2000}; tl.to(o, {v:2012, duration:.9, ease:"power2.out", onUpdate:()=>{ document.getElementById("g-since-year").textContent = Math.round(o.v); }}, ${T + 0.15}); }
    tl.fromTo("#g-since .since-sub", {opacity:0, y:20}, {opacity:1, y:0, duration:.35}, ${map(18.2)});
    tl.to("#g-since .since", {opacity:0, y:-30, duration:.3, ease:"power2.in"}, ${T + D - 0.3});`,
});

add({
  id: "g-empty", a: 21.5, b: 21.78, cls: "mid",
  html: `<div class="stamp">STILL EMPTY</div>`,
  anim: (T, D) => `
    tl.fromTo("#g-empty .stamp", {scale:2.2, opacity:0, rotate:-14}, {scale:1, opacity:1, rotate:-8, duration:.22, ease:"power4.out"}, ${T});
    tl.to("#g-empty .stamp", {opacity:0, duration:.15}, ${T + D + 0.2});`,
  extra: 0.35,
});

add({
  id: "g-plan", a: 25.0, b: 32.75, cls: "top",
  html: `<div class="plan">
    <div class="plan-title">TAREEKA SIMPLE HAI</div>
    <div class="step" id="g-step1"><span class="num">01</span><span>VISIT THE OFFICES</span></div>
    <div class="step" id="g-step2"><span class="num">02</span><span>PROCURE THE ORDER</span></div>
    <div class="step" id="g-step3"><span class="num">03</span><span>CLOSE THE DEAL</span></div>
  </div>`,
  anim: (T, D) => `
    tl.fromTo("#g-plan .plan-title", {opacity:0, y:-30}, {opacity:1, y:0, duration:.4, ease:"power3.out"}, ${T});
    tl.fromTo("#g-step1", {opacity:0, x:-120}, {opacity:1, x:0, duration:.4, ease:"back.out(1.6)"}, ${map(27.8)});
    tl.fromTo("#g-step2", {opacity:0, x:-120}, {opacity:1, x:0, duration:.4, ease:"back.out(1.6)"}, ${map(29.5)});
    tl.fromTo("#g-step3", {opacity:0, x:-120}, {opacity:1, x:0, duration:.4, ease:"back.out(1.6)"}, ${map(32.0)});
    tl.to("#g-step3", {backgroundColor:"#FFD43B", color:"#111", duration:.2}, ${map(32.45)});
    tl.to("#g-plan .plan", {opacity:0, y:-30, duration:.25, ease:"power2.in"}, ${T + D - 0.25});`,
});

add({
  id: "g-why", a: 32.8, b: 33.75, cls: "center",
  html: `<div class="why">WHY <span>US?</span></div>`,
  anim: (T, D) => `
    tl.fromTo("#g-why .why", {scale:.3, opacity:0, rotate:-6}, {scale:1, opacity:1, rotate:-3, duration:.35, ease:"back.out(2.2)"}, ${T});
    tl.to("#g-why .why", {scale:1.1, opacity:0, duration:.25, ease:"power2.in"}, ${T + D - 0.25});`,
});

add({
  id: "g-check", a: 34.5, b: 39.7, cls: "top",
  html: `<div class="checks">
    <div class="check" id="g-c1"><span class="tick">✓</span><span>WE WALK IN</span></div>
    <div class="check" id="g-c2"><span class="tick">✓</span><span>WE QUALIFY</span></div>
    <div class="check" id="g-c3"><span class="tick">✓</span><span>WE REGISTER THE LEAD</span></div>
    <div class="check check-hot" id="g-c4"><span class="tick">0</span><span>CHANNEL CONFLICTS</span></div>
  </div>`,
  anim: (T, D) => `
    ${[[1, 34.9], [2, 36.0], [3, 37.1], [4, 38.4]].map(([n, t]) => `
    tl.fromTo("#g-c${n}", {opacity:0, x:-80}, {opacity:1, x:0, duration:.35, ease:"power3.out", immediateRender:false}, ${map(t)});
    tl.fromTo("#g-c${n} .tick", {scale:0}, {scale:1, duration:.35, ease:"back.out(3)"}, ${map(t) + 0.12});`).join("")}
    tl.to("#g-check .checks", {opacity:0, y:-30, duration:.25, ease:"power2.in"}, ${T + D - 0.25});`,
});

add({
  id: "g-zero", a: 40.0, b: 45.2, cls: "top",
  html: `<div class="zero-board">
    <div class="zrow" id="g-z1"><span>ACQUISITION COST</span><b class="zval">₹0</b></div>
    <div class="zrow" id="g-z2"><span>AD SPEND</span><b class="zval">₹0</b></div>
    <div class="zrow" id="g-z3"><span>PAYROLL</span><b class="zval">₹0</b></div>
  </div>`,
  anim: (T, D) => `
    ${[[1, 40.0, 41.6], [2, 42.2, 43.1], [3, 43.8, 44.6]].map(([n, q, z]) => `
    tl.fromTo("#g-z${n}", {opacity:0, y:30}, {opacity:1, y:0, duration:.3, ease:"power3.out"}, ${map(q)});
    tl.fromTo("#g-z${n} .zval", {scale:3, opacity:0, rotate:-15}, {scale:1, opacity:1, rotate:0, duration:.25, ease:"power4.out"}, ${map(z)});`).join("")}
    tl.to("#g-zero .zero-board", {opacity:0, y:-30, duration:.25, ease:"power2.in"}, ${T + D - 0.25});`,
});

add({
  id: "g-pct", a: 46.5, b: 49.3, cls: "top",
  html: `<div class="pct"><div class="pct-ring"><span>%</span></div><div class="pct-text"><small>YOU ONLY PAY</small>A % OF THE REVENUE WE BRING</div></div>`,
  anim: (T, D) => `
    tl.fromTo("#g-pct .pct-ring", {scale:0, rotate:-180}, {scale:1, rotate:0, duration:.5, ease:"back.out(2)"}, ${T});
    tl.fromTo("#g-pct .pct-text", {opacity:0, x:60}, {opacity:1, x:0, duration:.4, ease:"power3.out"}, ${T + 0.2});
    tl.to("#g-pct .pct", {opacity:0, y:-30, duration:.25, ease:"power2.in"}, ${T + D - 0.25});`,
});

add({
  id: "g-challenge", a: 50.0, b: 52.36, cls: "top",
  html: `<div class="cal"><div class="cal-top">CHALLENGE</div><div class="cal-num">2</div><div class="cal-sub">MONTHS</div></div>`,
  anim: (T, D) => `
    tl.fromTo("#g-challenge .cal", {y:-200, rotate:10, opacity:0}, {y:0, rotate:-4, opacity:1, duration:.5, ease:"back.out(1.8)"}, ${T});
    tl.fromTo("#g-challenge .cal-top", {backgroundColor:"#222"}, {backgroundColor:"#E8344E", duration:.2}, ${map(51.7)});
    tl.to("#g-challenge .cal", {opacity:0, y:-40, duration:.25, ease:"power2.in"}, ${T + D - 0.25});`,
});

add({
  id: "g-lose", a: 53.6, b: 54.45, cls: "mid",
  html: `<div class="stamp stamp-green">YOU LOSE NOTHING</div>`,
  anim: (T, D) => `
    tl.fromTo("#g-lose .stamp", {scale:2, opacity:0, rotate:8}, {scale:1, opacity:1, rotate:4, duration:.22, ease:"power4.out"}, ${T});
    tl.to("#g-lose .stamp", {opacity:0, duration:.15}, ${T + D - 0.15});`,
});

add({
  id: "g-trio", a: 54.8, b: 57.35, cls: "top",
  html: `<div class="trio">
    <div class="trio-row" id="g-t1"><b>60</b> DAYS</div>
    <div class="trio-row" id="g-t2"><b>ZERO</b> RISK</div>
    <div class="trio-row" id="g-t3"><b>PURE</b> UPSIDE <span class="arrow">↗</span></div>
  </div>`,
  anim: (T, D) => `
    ${[[1, 54.8], [2, 55.6], [3, 56.4]].map(([n, t]) => `
    tl.fromTo("#g-t${n}", {opacity:0, scale:1.8, y:-20}, {opacity:1, scale:1, y:0, duration:.28, ease:"power4.out"}, ${map(t)});`).join("")}
    tl.fromTo("#g-trio .arrow", {x:-20, y:20, opacity:0}, {x:0, y:0, opacity:1, duration:.4, ease:"back.out(3)"}, ${map(56.7)});
    tl.to("#g-trio .trio", {opacity:0, y:-30, duration:.25, ease:"power2.in"}, ${T + D - 0.25});`,
});

add({
  id: "g-end", a: 57.4, b: SRC_END, cls: "top",
  html: `<div class="endcard"><div class="end-kicker">AMBRANE × CORPORATE INDIA</div><div class="end-title">LET'S BUILD IT <span>TOGETHER</span></div></div>`,
  anim: (T, D) => `
    tl.fromTo("#g-end .end-kicker", {opacity:0, y:-20}, {opacity:1, y:0, duration:.4, ease:"power3.out"}, ${T});
    tl.fromTo("#g-end .end-title", {opacity:0, scale:.8}, {opacity:1, scale:1, duration:.5, ease:"back.out(2)"}, ${T + 0.25});
    tl.fromTo("#g-end .end-title span", {color:"#FFFFFF"}, {color:"#FFD43B", duration:.3}, ${map(60.0)});`,
});

// ---------- assemble ----------
const fmt = (n) => +n.toFixed(3);

// footage
const footage = segs
  .map(
    (s, i) => `      <div class="seg" id="${s.id}-wrap" style="z-index:${i + 1}">
        <div class="kb" id="${s.id}-kb"><div class="tx" id="${s.id}-tx">
          <video id="${s.id}" class="clip" src="media/enhanced.mp4" playsinline data-has-audio="true"
            data-start="${s.start}" data-duration="${s.dur}" data-media-start="${fmt(s.a)}" data-track-index="0" data-volume="1"></video>
        </div></div>
      </div>`,
  )
  .join("\n");

const tlLines = [];
// Ken Burns / punch-in per segment (on .kb), transitions on .tx
segs.forEach((s) => {
  const drift = s.scale + 0.035;
  tlLines.push(
    `tl.fromTo("#${s.id}-kb", {scale:${s.scale}}, {scale:${fmt(drift)}, duration:${s.dur}, ease:"none"}, ${s.start});`,
  );
});
segs.forEach((s) => tlLines.push(`tl.set("#${s.id}-tx", {scale:1, xPercent:0, filter:"blur(0px)"}, 0);`));
// emphasis punches on single-word "ZERO" answers (snap in)
for (const t of [41.6, 43.1, 44.6]) {
  const seg = segs.find((s) => t >= s.a && t < s.b);
  tlLines.push(
    `tl.fromTo("#${seg.id}-tx", {scale:1.18}, {scale:1, duration:.45, ease:"power3.out", immediateRender:false}, ${map(t)});`,
  );
}
// transitions at the source's own scene cuts
const cutsOut = [];
segs.forEach((s, i) => {
  if (s.endsAt !== "scene") return;
  const next = segs[i + 1];
  const c = fmt(s.start + s.dur);
  const rem = REMOVE.find((r) => Math.abs(r[0] - s.b) < 1e-6) || [s.b, s.b];
  const kind = TRANSITION[Object.keys(TRANSITION).find((k) => +k >= rem[0] - 0.01 && +k <= rem[1] + 0.01)] || "zoom";
  cutsOut.push(c);
  if (kind === "whip") {
    tlLines.push(
      `tl.fromTo("#${s.id}-tx", {xPercent:0, filter:"blur(0px)"}, {xPercent:-35, filter:"blur(14px)", duration:.16, ease:"power3.in", immediateRender:false}, ${fmt(c - 0.16)});`,
      `tl.fromTo("#${next.id}-tx", {xPercent:35, filter:"blur(14px)"}, {xPercent:0, filter:"blur(0px)", duration:.22, ease:"power3.out", immediateRender:false}, ${c});`,
    );
    tcues.push(["whip", s.b]);
  } else if (kind === "zoom") {
    tlLines.push(
      `tl.fromTo("#${s.id}-tx", {scale:1, filter:"blur(0px)"}, {scale:1.25, filter:"blur(10px)", duration:.16, ease:"power3.in", immediateRender:false}, ${fmt(c - 0.16)});`,
      `tl.fromTo("#${next.id}-tx", {scale:1.25, filter:"blur(10px)"}, {scale:1, filter:"blur(0px)", duration:.24, ease:"power3.out", immediateRender:false}, ${c});`,
    );
    tcues.push(["zoom", s.b]);
  } else {
    tlLines.push(`tl.fromTo("#flash", {opacity:0}, {opacity:.85, duration:.07, ease:"none", immediateRender:false}, ${fmt(c - 0.07)});`);
    tlLines.push(`tl.to("#flash", {opacity:0, duration:.28, ease:"power2.out"}, ${c});`);
    tlLines.push(
      `tl.fromTo("#${next.id}-tx", {scale:1.1}, {scale:1, duration:.35, ease:"power3.out", immediateRender:false}, ${c});`,
    );
    tcues.push(["flash", s.b]);
  }
});

// captions
const capHtml = [];
PHRASES.forEach(([words, end, pos], i) => {
  const id = `cap-${i}`;
  const start = map(words[0][1]);
  const stop = map(end);
  const dur = fmt(Math.max(0.2, stop - start));
  capHtml.push(
    `      <div class="cap-line${pos === "high" ? " cap-high" : ""} clip" id="${id}" data-start="${start}" data-duration="${dur}" data-track-index="5"><div class="cap-card">${words
      .map(([w], j) => `<span class="w${KEY.has(w) ? " key" : ""}" id="${id}-w${j}">${w}</span>`)
      .join(" ")}</div></div>`,
  );
  tlLines.push(
    `tl.fromTo("#${id} .cap-card", {scale:.86, y:18, opacity:0}, {scale:1, y:0, opacity:1, duration:.16, ease:"back.out(2.4)"}, ${start});`,
  );
  words.forEach(([, t], j) => {
    const wt = Math.max(start, map(t));
    const nextT = j + 1 < words.length ? Math.max(start, map(words[j + 1][1])) : stop;
    tlLines.push(
      `tl.fromTo("#${id}-w${j}", {opacity:.55, scale:1}, {opacity:1, scale:1.12, duration:.1, ease:"power2.out"}, ${fmt(wt)});`,
      `tl.set("#${id}-w${j}", {backgroundColor:"#FFD43B", color:"#0E0E12"}, ${fmt(wt)});`,
      `tl.to("#${id}-w${j}", {scale:1, duration:.12, ease:"power2.out"}, ${fmt(Math.max(wt + 0.1, nextT - 0.02))});`,
      `tl.set("#${id}-w${j}", {backgroundColor:"rgba(255,212,59,0)", color:"${KEY.has(words[j][0]) ? "#FFD43B" : "#FFFFFF"}"}, ${fmt(Math.max(wt + 0.1, nextT))});`,
    );
  });
});

// graphics
const gHtml = G.map((g) => {
  const T = map(g.a);
  const D = fmt(map(g.b) - T + (g.extra || 0));
  tlLines.push(g.anim(T, D));
  return `      <div class="gfx gfx-${g.cls} clip" id="${g.id}" data-start="${T}" data-duration="${D}" data-track-index="6">${g.html}</div>`;
}).join("\n");

// final fade to black
tlLines.push(`tl.fromTo("#fade", {opacity:0}, {opacity:1, duration:.5, ease:"power1.in"}, ${fmt(OUT_END - 0.5)});`);

// sfx audio
// transition sounds, rotating per kind so neighbours differ
const TPOOL = { whip: ["whooshA", "whooshD"], zoom: ["sweepA", "swooshFast", "sweepB", "sweepC"], flash: ["whooshB", null] }; // 2nd flash sits under the "WHY US?" hit
const tUsed = {};
for (const [kind, t] of tcues) {
  const n = (tUsed[kind] = (tUsed[kind] ?? -1) + 1);
  const name = TPOOL[kind][n % TPOOL[kind].length];
  if (name) sfx.push([name, t, 0.5]);
}
const META = JSON.parse(readFileSync(join(here, "sfx-meta.json"), "utf8"));
// output-time windows where someone is speaking (caption phrases)
const SPEECH = PHRASES.map(([w, end]) => [map(w[0][1]), map(end)]);
const speaking = (t) => SPEECH.some(([a, b]) => t >= a - 0.05 && t <= b);
const sfxHtml = sfx
  .sort((x, y) => x[1] - y[1])
  .map(([name, t, gain], i) => {
    const m = META[name];
    const hit = map(t);
    const start = fmt(Math.max(0, hit - m.peak));
    const skip = fmt(Math.max(0, m.peak - hit)); // cue too close to 0: skip into the file
    const dur = fmt(Math.min(m.dur - skip, OUT_END - start));
    // dip a little while the speaker is talking so the voice stays on top
    const vol = fmt(gain * (speaking(hit) ? 0.8 : 1));
    const lane = { version: 1, lanes: [{ target: "volume", points: [{ t: 0, v: vol }, { t: fmt(Math.max(0.02, dur - 0.08)), v: vol }, { t: dur, v: 0 }] }] };
    return `      <audio id="sfx-${i}" src="assets/sfx-mk/${name}.mp3" data-start="${start}" data-duration="${dur}"${skip ? ` data-media-start="${skip}"` : ""} data-track-index="${10 + (i % 8)}" data-volume="1" data-automation='${JSON.stringify(lane)}'></audio>`;
  })
  .join("\n");

const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>DLF Cyber City Recut</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Montserrat"; font-weight: 700; src: url("assets/fonts/montserrat-latin-700-normal.woff2") format("woff2"); }
      @font-face { font-family: "Montserrat"; font-weight: 800; src: url("assets/fonts/montserrat-latin-800-normal.woff2") format("woff2"); }
      @font-face { font-family: "Montserrat"; font-weight: 900; src: url("assets/fonts/montserrat-latin-900-normal.woff2") format("woff2"); }
      @font-face { font-family: "Anton"; font-weight: 400; src: url("assets/fonts/anton-latin-400-normal.woff2") format("woff2"); }
      :root { --accent: #FFD43B; --red: #E8344E; --green: #2BD67B; --ink: #0E0E12; }
      body { margin: 0; background: #000; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #000; font-family: "Montserrat", sans-serif; color: #fff; }
      .seg { position: absolute; inset: 0; overflow: hidden; }
      .kb, .tx { position: absolute; inset: 0; transform-origin: 50% 40%; }
      .seg video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      #scrim { position: absolute; left: 0; right: 0; top: 1180px; height: 560px; z-index: 200;
        background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,.42) 35%, rgba(0,0,0,.42) 65%, rgba(0,0,0,0) 100%); }
      #vignette { position: absolute; inset: 0; z-index: 201; pointer-events: none;
        background: radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,.38) 100%); }
      #flash { position: absolute; inset: 0; background: #fff; opacity: 0; z-index: 400; }
      #fade { position: absolute; inset: 0; background: #000; opacity: 0; z-index: 500; }

      /* captions */
      .cap-line { position: absolute; left: 60px; right: 60px; top: 1300px; height: 300px; z-index: 300;
        display: flex; align-items: center; justify-content: center; }
      .cap-line.cap-high { top: 920px; }
      .cap-card { display: block; max-width: 920px; padding: 22px 34px; border-radius: 26px; text-align: center;
        background: rgba(12,12,18,.72); box-shadow: 0 18px 50px rgba(0,0,0,.45);
        font-weight: 900; font-size: 76px; line-height: 1.08; letter-spacing: -1px; }
      .w { display: inline-block; opacity: .55; color: #fff; background-color: rgba(255,212,59,0); padding: 0 6px; border-radius: 12px; }

      /* graphics */
      .gfx { position: absolute; left: 0; right: 0; z-index: 320; display: flex; justify-content: center; }
      .gfx-top { top: 150px; height: 600px; align-items: flex-start; }
      .gfx-mid { top: 1000px; height: 360px; align-items: center; }
      .gfx-center { top: 640px; height: 520px; align-items: center; }
      .chip { display: flex; align-items: center; gap: 18px; padding: 20px 34px; border-radius: 999px;
        background: rgba(255,255,255,.94); color: var(--ink); font-weight: 900; font-size: 48px; box-shadow: 0 16px 40px rgba(0,0,0,.35); }
      .chip-sub { font-weight: 700; font-size: 30px; color: #666; letter-spacing: 3px; }
      .pin { display: block; width: 34px; height: 34px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); background: var(--red); }
      .tag { display: flex; align-items: center; gap: 20px; padding: 22px 40px; border-radius: 18px; font-weight: 900; font-size: 64px; box-shadow: 0 16px 40px rgba(0,0,0,.35); }
      .tag-red { background: var(--red); color: #fff; }
      .warn { display: flex; align-items: center; justify-content: center; width: 70px; height: 70px; border-radius: 50%; background: #fff; color: var(--red); font-size: 52px; }
      .tape { width: 1500px; height: 130px; overflow: hidden; display: flex; align-items: center; transform-origin: 50% 50%;
        background: repeating-linear-gradient(-45deg, #FFD43B 0 40px, #111 40px 80px); box-shadow: 0 20px 40px rgba(0,0,0,.4); }
      .tape-inner { display: block; white-space: nowrap; font-family: "Anton", sans-serif; font-size: 78px; color: #fff; letter-spacing: 3px;
        background: #111; padding: 4px 30px; margin-left: 120px; }
      .slam { display: block; font-family: "Anton", sans-serif; font-size: 210px; color: #fff; letter-spacing: 6px;
        text-shadow: 0 10px 40px rgba(0,0,0,.6), 0 0 2px #000; }
      .since { display: flex; flex-direction: column; align-items: center; padding: 26px 60px 30px; border-radius: 28px;
        background: rgba(12,12,18,.78); box-shadow: 0 18px 50px rgba(0,0,0,.45); }
      .since-label { font-weight: 800; font-size: 40px; letter-spacing: 12px; color: #bbb; }
      .since-year { font-family: "Anton", sans-serif; font-size: 190px; line-height: 1; color: var(--accent); }
      .since-sub { font-weight: 800; font-size: 34px; letter-spacing: 3px; }
      .stamp { display: block; padding: 14px 40px; border: 10px solid var(--red); border-radius: 20px; color: var(--red);
        font-family: "Anton", sans-serif; font-size: 130px; letter-spacing: 4px; background: rgba(255,255,255,.9); }
      .stamp-green { border-color: var(--green); color: #0b7a3f; font-size: 96px; }
      .plan { display: flex; flex-direction: column; gap: 18px; width: 860px; }
      .plan-title { font-family: "Anton", sans-serif; font-size: 84px; color: #fff; text-align: center; text-shadow: 0 6px 30px rgba(0,0,0,.6); }
      .step { display: flex; align-items: center; gap: 26px; padding: 22px 30px; border-radius: 22px; background: rgba(255,255,255,.95);
        color: var(--ink); font-weight: 900; font-size: 50px; box-shadow: 0 14px 34px rgba(0,0,0,.35); }
      .num { font-family: "Anton", sans-serif; font-size: 60px; color: var(--red); }
      .why { display: block; font-family: "Anton", sans-serif; font-size: 230px; color: #fff; text-shadow: 0 12px 50px rgba(0,0,0,.6); }
      .why span { color: var(--accent); }
      .checks { display: flex; flex-direction: column; gap: 16px; width: 860px; }
      .check { display: flex; align-items: center; gap: 24px; padding: 20px 28px; border-radius: 22px; background: rgba(12,12,18,.8);
        font-weight: 900; font-size: 50px; box-shadow: 0 14px 34px rgba(0,0,0,.35); }
      .tick { display: flex; align-items: center; justify-content: center; width: 70px; height: 70px; border-radius: 50%;
        background: var(--green); color: #fff; font-size: 44px; flex: none; }
      .check-hot .tick { background: var(--accent); color: var(--ink); font-family: "Anton", sans-serif; }
      .zero-board { display: flex; flex-direction: column; gap: 16px; width: 880px; }
      .zrow { display: flex; align-items: center; justify-content: space-between; padding: 22px 34px; border-radius: 22px;
        background: rgba(255,255,255,.95); color: var(--ink); font-weight: 900; font-size: 50px; box-shadow: 0 14px 34px rgba(0,0,0,.35); }
      .zval { display: block; font-family: "Anton", sans-serif; font-weight: 400; font-size: 80px; color: var(--green); }
      .pct { display: flex; align-items: center; gap: 34px; padding: 26px 40px; border-radius: 30px; background: rgba(12,12,18,.82); box-shadow: 0 18px 50px rgba(0,0,0,.45); width: 860px; box-sizing: border-box; }
      .pct-ring { display: flex; align-items: center; justify-content: center; flex: none; width: 190px; height: 190px; border-radius: 50%;
        border: 14px solid var(--accent); font-family: "Anton", sans-serif; font-size: 120px; color: var(--accent); box-sizing: border-box; }
      .pct-text { display: block; font-weight: 900; font-size: 48px; line-height: 1.1; }
      .pct-text small { display: block; font-size: 30px; color: #aaa; letter-spacing: 4px; margin-bottom: 8px; }
      .cal { display: flex; flex-direction: column; align-items: center; width: 400px; border-radius: 30px; overflow: hidden; background: #fff; box-shadow: 0 20px 50px rgba(0,0,0,.45); }
      .cal-top { display: block; width: 100%; text-align: center; padding: 18px 0; background: #222; color: #fff; font-weight: 900; font-size: 46px; letter-spacing: 4px; }
      .cal-num { display: block; font-family: "Anton", sans-serif; font-size: 230px; line-height: 1.05; color: var(--ink); }
      .cal-sub { display: block; font-weight: 900; font-size: 44px; color: var(--ink); letter-spacing: 8px; padding-bottom: 22px; }
      .trio { display: flex; flex-direction: column; align-items: center; gap: 4px; }
      .trio-row { display: block; font-family: "Anton", sans-serif; font-size: 130px; line-height: 1.05; color: #fff; text-shadow: 0 10px 40px rgba(0,0,0,.65); }
      .trio-row b { font-weight: 400; color: var(--accent); }
      .arrow { display: inline-block; color: var(--green); }
      .endcard { display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 34px 50px; border-radius: 32px;
        background: rgba(12,12,18,.82); box-shadow: 0 20px 60px rgba(0,0,0,.5); width: 900px; box-sizing: border-box; }
      .end-kicker { display: block; font-weight: 800; font-size: 34px; letter-spacing: 6px; color: #bbb; }
      .end-title { display: block; font-family: "Anton", sans-serif; font-size: 104px; line-height: 1.05; text-align: center; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="${OUT_END}">
${footage}
      <div id="scrim"></div>
      <div id="vignette"></div>
${capHtml.join("\n")}
${gHtml}
      <div id="flash"></div>
      <div id="fade"></div>
${sfxHtml}
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      ${tlLines.join("\n      ")}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
`;

writeFileSync(join(here, "..", "index.html"), html);
console.log(`segments=${segs.length} captions=${PHRASES.length} graphics=${G.length} sfx=${sfx.length} duration=${OUT_END}s cuts=${cutsOut.join(",")}`);
