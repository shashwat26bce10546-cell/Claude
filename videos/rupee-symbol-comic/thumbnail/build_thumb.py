#!/usr/bin/env python3
"""Shorts cover (1080x1920) built from the video's own comic toolkit (src/shared.css + src/lib.js)."""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
css = open(os.path.join(ROOT, "src", "shared.css")).read().replace('url("assets/', f'url("file://{ROOT}/assets/')
lib = open(os.path.join(ROOT, "src", "lib.js")).read()
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
{css}
html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #D8000F; }}
#root {{ width: 1080px; height: 1920px; }}
#burst {{ position: absolute; left: -460px; top: -40px; width: 2000px; height: 2000px; }}
#rays {{ position: absolute; left: 80px; top: 380px; width: 1100px; height: 1100px; }}
#giant {{ position: absolute; left: 400px; top: 500px; width: 660px; text-align: center; font-size: 720px; color: #FFFFFF; transform: rotate(8deg); filter: drop-shadow(9px 0 0 #1C1410) drop-shadow(-9px 0 0 #1C1410) drop-shadow(0 9px 0 #1C1410) drop-shadow(0 -9px 0 #1C1410) drop-shadow(18px 18px 0 rgba(28, 20, 16, 0.45)); }}
#h2 span {{ filter: drop-shadow(5px 0 0 #1C1410) drop-shadow(-5px 0 0 #1C1410) drop-shadow(0 5px 0 #1C1410) drop-shadow(0 -5px 0 #1C1410); display: inline-block; }}
#guy {{ position: absolute; left: -60px; top: 690px; width: 620px; height: 1395px; }}
#h1 {{ position: absolute; left: 50px; top: 100px; font-size: 160px; color: #FFFFFF; transform: rotate(-4deg); }}
#h2 {{ position: absolute; left: 70px; top: 275px; font-size: 172px; color: #FFFFFF; transform: rotate(-4deg); white-space: nowrap; }}
#h2 span {{ color: #FFD23F; }}
#tag {{ position: absolute; left: 470px; top: 1380px; transform: rotate(3deg); font-size: 46px; }}
#tag b {{ display: block; font-size: 34px; color: #D8000F; letter-spacing: 4px; }}
#sticker {{ position: absolute; left: 600px; top: 1060px; width: 330px; height: 330px; }}
#stickerword {{ position: absolute; left: 600px; top: 1172px; width: 330px; text-align: center; font-size: 62px; line-height: 0.95; color: #D8000F; transform: rotate(-10deg); }}
</style></head><body><div id="root">
  <div class="cmc-halftone-light"></div>
  <div id="burstwrap"></div><div id="rayswrap"></div>
  <div id="giant" class="cmc-shrik cmc-ink-outline cmc-stack-shadow">₹</div>
  <div id="guywrap"></div>
  <div id="h1" class="cmc-shrik cmc-ink-outline cmc-stack-shadow">Student ne</div>
  <div id="h2" class="cmc-shrik cmc-ink-outline cmc-stack-shadow">banaya <span>₹!</span></div>
  <div id="stickerwrap"></div><div id="stickerword" class="cmc-shrik">TRUE<br>STORY</div>
  <div id="tag" class="cmc-cap"><b>IIT Bombay</b>PhD student</div>
</div>
<script src="file://{ROOT}/vendor/gsap.min.js"></script>
<script>
{lib}
document.getElementById("burstwrap").outerHTML = burst("burst", "#A8000B", 44, 0.12);
document.getElementById("rayswrap").outerHTML = burst("rays", "#FFD23F", 30, 0.3, 0.9);
document.getElementById("stickerwrap").outerHTML = star("sticker", "#FFFFFF", 14, 320, 470);
// graduation cap with tassel, in character space above the head
const cap = `<g><path d="M200 40 L330 92 L200 144 L70 92 Z" fill="#1C1410" stroke="#1C1410" stroke-width="8" stroke-linejoin="round"/>
  <path d="M120 112 L120 150 Q200 186 280 150 L280 112 L200 144 Z" fill="#2A211C" stroke="#1C1410" stroke-width="8" stroke-linejoin="round"/>
  <path d="M200 92 L312 120 L318 178" fill="none" stroke="#FFD23F" stroke-width="8" stroke-linecap="round"/><circle cx="318" cy="186" r="12" fill="#FFD23F" stroke="#1C1410" stroke-width="5"/></g>`;
document.getElementById("guywrap").innerHTML = `<div id="guy">${{person("u", "udaya", {{ overlay: "" }})}}</div>`;
document.querySelector("#u-head").insertAdjacentHTML("beforeend", cap);
const tl = gsap.timeline({{ paused: true }});
setPose(tl, "u", {{ armR: -112, foreR: -22, armL: 14, foreL: 64, head: 6 }});
mouth(tl, "u", 0, "mOpen");
tl.set("#u-brows", {{ y: -12 }}, 0);
tl.set("#u-eyes", {{ scale: 1.15, svgOrigin: PIV.eyes }}, 0);
tl.seek(0.01);
</script></body></html>"""
open(os.path.join(HERE, "thumb.html"), "w").write(html)
out = os.path.join(HERE, "rupee-thumbnail-1080x1920.png")
subprocess.run(["timeout", "60", "/opt/pw-browsers/chromium", "--headless", "--no-sandbox", "--disable-gpu",
                "--allow-file-access-from-files", "--hide-scrollbars", f"--screenshot={out}", "--window-size=1080,2100",
                "--virtual-time-budget=3000", "file://" + os.path.join(HERE, "thumb.html")], capture_output=True)
from PIL import Image
Image.open(out).crop((0, 0, 1080, 1920)).save(out)
print(out, os.path.getsize(out))
