#!/usr/bin/env python3
"""Swap in the ElevenLabs Hinglish narration (assets/voice-hi/take1.mp3).

1. Cut the single take into one clip per frame at the mid-points of its line pauses.
2. Give each clip word timings: whisper cannot transcribe Hinglish, so each line's words are laid
   across that clip's detected speech intervals in proportion to their length.
3. Write audio_meta.json voices + src/retime.json (per-frame old→new cue anchors that tools/build.py
   uses to re-time the English-cut animation onto the Hinglish delivery).
"""
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAKE = os.path.join(ROOT, "assets", "voice-hi", "take1.mp3")

# cut points = middle of the pause between lines (from silencedetect + whisper anchor words)
CUTS = [0.0, 6.03, 16.37, 22.38, 29.88, 39.43, 45.56, 53.65, 62.929]

LINES = [
    "Yeh symbol aap roz use karte ho... lekin kya aap jaante ho, isse banaya KISNE?",
    "Do hazaar das tak, rupee ka apna koi symbol hi nahi tha! Dollar ka tha, pound ka tha... aur India? Bas \"R-S\" likh deta tha.",
    "Toh sarkaar ne poore desh mein ek contest rakha... aur teen hazaar se zyada designs aa gaye!",
    "Unmein se ek design aaya IIT Bombay ke ek young PhD student se... naam tha — D. Udaya Kumar.",
    "Unhone Devanagari ka \"र\" aur English ka \"R\" mila diya... aur upar do lines jodi — ek tirange ki nishaani, aur barabari ka \"equal to\" sign!",
    "Pandrah July, do hazaar das ko, Union Cabinet ne final paanch mein se... unka design chuna!",
    "Aur ab suniye twist... lagbhag usi waqt... woh IIT Guwahati mein professor ki nayi naukri shuru kar rahe the!",
    "Aaj unka symbol har price tag, har keyboard, har payment app par hai. Toh agli baar jab ₹ dekho... Udaya Kumar ko yaad karna!",
]

# reliable whisper word hits (global seconds in take1) used as hard caption anchors: line -> {word: time}
ANCHORS = {
    1: {"Dollar": 10.1, "pound": 11.0, "India?": 12.0},
    2: {"contest": 18.1, "designs": 21.0},
    3: {"IIT": 23.8, "Bombay": 24.1, "young": 25.2, "PhD": 25.6, "student": 25.9},
    6: {"twist...": 47.3, "professor": 51.1},
    7: {"price": 54.7, "tag,": 55.3, "keyboard,": 56.0, "payment": 57.3, "app": 57.7},
}

# old (English-cut) local cue time -> new (Hinglish) local cue time, per frame
RETIME = {
    "01": [[0, 0], [0.85, 0.7], [2.4, 2.6], [3.0, 4.3], [3.62, 5.1], [4.373, 6.03]],
    "02": [[0, 0], [1.3, 1.3], [2.66, 2.6], [4.07, 4.07], [5.41, 4.97], [5.98, 5.3], [6.12, 5.5], [6.51, 5.97], [6.9, 7.8], [7.76, 8.6], [8.149, 10.34]],
    "03": [[0, 0], [1.03, 1.35], [1.63, 1.9], [2.85, 2.8], [3.0, 3.2], [3.75, 4.2], [5.163, 6.01]],
    "04": [[0, 0], [1.33, 1.42], [2.56, 3.0], [3.6, 5.0], [3.85, 5.6], [4.54, 6.4], [5.44, 7.5]],
    "05": [[0, 0], [1.87, 1.95], [3.44, 3.55], [4.08, 5.0], [4.32, 5.3], [6.14, 6.9], [7.19, 8.1], [8.02, 8.8], [8.704, 9.55]],
    "06": [[0, 0], [0.45, 0.4], [1.08, 1.0], [1.6, 1.6], [2.6, 2.3], [3.55, 3.4], [4.06, 4.6], [4.3, 5.0], [4.9, 5.5], [5.717, 6.13]],
    "07": [[0, 0], [0.75, 1.3], [1.6, 2.1], [4.4, 5.0], [4.55, 5.4], [5.05, 5.7], [5.45, 6.2], [6.1, 6.9], [6.4, 7.2], [7.232, 8.09]],
    "08": [[0, 0], [1.85, 0.95], [2.7, 2.25], [3.35, 3.55], [4.1, 4.3], [4.95, 5.2], [6.4, 7.0], [6.9, 7.9], [7.851, 9.28]],
}


def speech_intervals(path, dur):
    out = subprocess.run(["ffmpeg", "-i", path, "-af", "silencedetect=noise=-38dB:d=0.18", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
    sil = list(zip(starts, ends + [dur] * (len(starts) - len(ends))))
    speech, t = [], 0.0
    for s, e in sil:
        if s - t > 0.05:
            speech.append((t, s))
        t = e
    if dur - t > 0.05:
        speech.append((t, dur))
    return speech


def main():
    os.makedirs(os.path.join(ROOT, "assets", "voice"), exist_ok=True)
    meta = json.load(open(os.path.join(ROOT, "audio_meta.json")))
    voices = []
    for k in range(8):
        a, b = CUTS[k], CUTS[k + 1]
        rel = f"assets/voice/{k + 1:02d}.wav"
        path = os.path.join(ROOT, rel)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", TAKE, "-ss", f"{a}", "-to", f"{b}",
                        "-ar", "44100", "-ac", "1", path], check=True)
        dur = round(b - a, 3)
        sp = speech_intervals(path, dur)
        words = LINES[k].split()
        weights = [len(re.sub(r"[^\w]", "", w)) + 1.5 for w in words]
        # anchor points (word index -> clip time); fill between anchors proportionally in speech time
        anc = {}
        for wi, w in enumerate(words):
            t = ANCHORS.get(k, {}).get(w)
            if t is not None and wi not in anc.values():
                anc[wi] = round(t - a, 3)

        def to_speech(x):  # clip time -> speech-time
            acc = 0.0
            for s0, e0 in sp:
                if x <= s0:
                    return acc
                if x <= e0:
                    return acc + x - s0
                acc += e0 - s0
            return acc

        def at(x):  # speech-time -> clip time
            for s0, e0 in sp:
                if x <= e0 - s0:
                    return s0 + x
                x -= e0 - s0
            return sp[-1][1]

        total_t = sum(e0 - s0 for s0, e0 in sp)
        keys = [(-1, 0.0)] + sorted((i, to_speech(t)) for i, t in anc.items()) + [(len(words), total_t)]
        starts = [0.0] * (len(words) + 1)
        for (i0, t0), (i1, t1) in zip(keys, keys[1:]):
            lo = max(i0, 0)
            seg = weights[lo:i1]
            tot = sum(seg) or 1
            acc = t0
            for j, w in enumerate(seg):
                starts[lo + j] = acc
                acc += w / tot * (t1 - t0)
        starts[len(words)] = total_t
        out = [{"id": f"f{k + 1}w{i}", "text": w, "start": round(at(starts[i]), 3), "end": round(at(starts[i + 1]), 3)}
               for i, w in enumerate(words)]
        voices.append({"frame": k + 1, "path": rel, "duration_s": dur, "words": out})
        print(k + 1, dur, f"{len(sp)} speech runs", out[0]["start"], "→", out[-1]["end"])
    meta["voices"] = voices
    json.dump(meta, open(os.path.join(ROOT, "audio_meta.json"), "w"), indent=2)
    json.dump(RETIME, open(os.path.join(ROOT, "src", "retime.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
