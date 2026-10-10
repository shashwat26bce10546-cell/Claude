#!/usr/bin/env python3
"""Assemble comic frames: src/frames/NN-name.html + src/shared.css + src/lib.js
-> compositions/frames/NN-name.html (one bare <template> per frame, everything inside it).

A source frame file has three blocks, in order:
  <style> ...frame css... </style>
  <markup> ...frame DOM (placed inside #root)... </markup>
  <script> ...frame timeline code; `tl`, `ID`, `DUR` and the lib helpers are in scope... </script>
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "compositions", "frames")


def durations():
    meta = json.load(open(os.path.join(ROOT, "audio_meta.json")))
    return {v["frame"]: v["duration_s"] for v in meta["voices"]}


def block(text, tag):
    m = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.S)
    return m.group(1).strip() if m else ""


def build(name, dur, css, lib):
    raw = open(os.path.join(SRC, "frames", name + ".html")).read()
    fid = name
    pre = f"f{name[:2]}-"  # element-id prefix: CSS ids may not start with a digit
    style = block(raw, "style").replace("ID-", pre)
    markup = block(raw, "markup").replace("ID-", pre).replace("{DUR}", f"{dur}")
    script = block(raw, "script").replace("ID-", pre)
    html = f"""<template>
  <style>
{css}
{style}
  </style>
  <div id="root" data-composition-id="{fid}" data-width="1080" data-height="1920" data-duration="{dur}">
{markup}
  </div>
  <script>
    (function () {{
      const ID = "{fid}";
      const DUR = {dur};
{lib}
      const tl = gsap.timeline({{ paused: true }});
{script}
      window.__timelines["{fid}"] = tl;
    }})();
  </script>
</template>
"""
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, name + ".html"), "w").write(html)
    return fid


def main():
    css = open(os.path.join(SRC, "shared.css")).read()
    lib = open(os.path.join(SRC, "lib.js")).read()
    durs = durations()
    names = sorted(f[:-5] for f in os.listdir(os.path.join(SRC, "frames")) if f.endswith(".html"))
    only = sys.argv[1:]
    for n in names:
        if only and not any(n.startswith(o) for o in only):
            continue
        num = int(n[:2])
        print("built", build(n, durs[num], css, lib), durs[num])


if __name__ == "__main__":
    main()
