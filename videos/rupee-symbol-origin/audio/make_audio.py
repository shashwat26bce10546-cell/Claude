"""Synthesise the music bed and SFX track for the ₹ Short (deterministic, no samples).

  python3 make_audio.py   ->  bed.wav, sfx.wav  (then encoded to .m4a by the caller)

Music: curious pizzicato in D minor (Dm–Bb–F–C), 100 bpm, Karplus–Strong plucks + soft shaker.
SFX timings match the scene cuts in ../index.html.
"""
import math
import os
import wave

import numpy as np

SR = 44100
DUR = 56.0
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)


def pluck(freq, dur, decay=0.996, bright=0.5):
    n = int(SR * dur)
    p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p)
    buf = bright * buf + (1 - bright) * np.convolve(buf, np.ones(3) / 3, "same")
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = decay * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    env = np.minimum(1, np.arange(n) / (0.003 * SR))
    return out * env


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def place(track, sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    j = min(len(track), i + len(sig))
    if j <= i:
        return
    l, r = gain * math.cos((pan + 1) * math.pi / 4), gain * math.sin((pan + 1) * math.pi / 4)
    track[i:j, 0] += sig[: j - i] * l
    track[i:j, 1] += sig[: j - i] * r


def music():
    tr = np.zeros((int(SR * DUR), 2))
    beat = 60 / 100
    # chord roots (midi) and arpeggio tones per bar
    chords = [(50, [62, 65, 69, 74]), (46, [62, 65, 70, 74]), (53, [60, 65, 69, 72]), (48, [60, 64, 67, 72])]
    cache = {}

    def note(m, dur, decay, bright):
        k = (m, dur, decay, bright)
        if k not in cache:
            cache[k] = pluck(midi(m), dur, decay, bright)
        return cache[k]

    bar = 0
    t = 0.0
    while t < DUR - 0.5:
        root, arp = chords[bar % 4]
        # bass on 1 and 3
        place(tr, note(root - 12, 1.4, 0.995, 0.3), t, 0.55, -0.1)
        place(tr, note(root - 12, 1.4, 0.995, 0.3), t + 2 * beat, 0.4, -0.1)
        # staccato pizzicato arpeggio (8ths), pattern varies every other bar
        pat = [0, 2, 1, 3, 2, 1, 3, 2] if bar % 2 == 0 else [0, 1, 2, 3, 3, 2, 1, 0]
        for k, idx in enumerate(pat):
            if bar < 1 and k % 2:  # sparse intro
                continue
            place(tr, note(arp[idx], 0.45, 0.985, 0.6), t + k * beat / 2, 0.33, 0.35 if k % 2 else -0.25)
        # shaker on off-beats from bar 2
        if bar >= 2:
            for k in range(4):
                n = int(0.05 * SR)
                s = rng.uniform(-1, 1, n) * np.exp(-np.linspace(0, 8, n))
                s = np.diff(s, prepend=0)
                place(tr, s, t + k * beat + beat / 2, 0.08, 0.5)
        t += 4 * beat
        bar += 1
    # fade in/out
    n = len(tr)
    fade = np.ones(n)
    fi, fo = int(0.3 * SR), int(1.8 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo)
    return tr * fade[:, None]


def env_noise(dur, a, d, lp=0.0):
    n = int(SR * dur)
    s = rng.uniform(-1, 1, n)
    if lp:
        k = int(lp)
        s = np.convolve(s, np.ones(k) / k, "same")
    t = np.arange(n) / SR
    return s * np.minimum(1, t / a) * np.exp(-np.maximum(0, t - a) / d)


def whoosh(dur=0.6):
    n = int(SR * dur)
    s = rng.uniform(-1, 1, n)
    out = np.zeros(n)
    acc = 0.0
    for i in range(n):  # sweeping one-pole low-pass
        a = 0.02 + 0.3 * math.sin(math.pi * i / n) ** 2
        acc += a * (s[i] - acc)
        out[i] = acc
    return out * np.sin(np.linspace(0, math.pi, n)) * 1.6


def thud():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * math.pi * (90 * t - 60 * t * t)) * np.exp(-t * 14) + 0.2 * env_noise(0.35, 0.001, 0.03, 30)


def boom():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    f = 55 + 70 * np.exp(-t * 6)
    ph = 2 * math.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 2.2) * 1.2 + 0.4 * env_noise(1.6, 0.002, 0.12, 40)


def scratch(dur):
    n = int(SR * dur)
    s = np.diff(rng.uniform(-1, 1, n), prepend=0)
    t = np.arange(n) / SR
    mod = 0.5 + 0.5 * np.abs(np.sin(2 * math.pi * 5.5 * t))
    return s * mod * 0.35 * np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.05)


def buzz(dur=0.7):
    t = np.arange(int(SR * dur)) / SR
    gate = (np.sin(2 * math.pi * 6 * t) > 0).astype(float)
    return np.sign(np.sin(2 * math.pi * 150 * t)) * 0.25 * gate * np.exp(-t * 0.5)


def ding(f=1318.5, dur=1.8):
    t = np.arange(int(SR * dur)) / SR
    return (np.sin(2 * math.pi * f * t) + 0.4 * np.sin(2 * math.pi * f * 2.76 * t)) * np.exp(-t * 3) * 0.6


def shimmer():
    out = np.zeros(int(SR * 1.5))
    for k, m in enumerate((86, 90, 93, 98)):
        d = ding(midi(m), 1.2) * 0.4
        i = int(k * 0.07 * SR)
        out[i:i + len(d)] += d[: len(out) - i]
    return out


def pop():
    t = np.arange(int(0.12 * SR)) / SR
    return np.sin(2 * math.pi * (500 + 2500 * t) * t) * np.exp(-t * 40)


def tick():
    return env_noise(0.06, 0.001, 0.01, 4) * 0.8


def sfx():
    tr = np.zeros((int(SR * DUR), 2))
    place(tr, ding(1318.5, 1.0), 0.15, 0.35)  # hook sparkle on the ₹
    place(tr, whoosh(0.5), 2.85, 0.6)  # cut to newspaper
    place(tr, whoosh(0.7), 7.9, 0.55)  # envelopes start
    for k in range(6):
        place(tr, whoosh(0.35), 8.4 + k * 0.65, 0.22, -0.6 + 0.24 * k)
    place(tr, pop(), 14.4, 0.6)  # red arrow
    place(tr, scratch(1.6), 19.15, 0.9, -0.2)  # drawing र
    place(tr, scratch(1.6), 21.2, 0.9, 0.2)  # drawing R
    place(tr, shimmer(), 24.3, 0.7)  # ₹ appears
    for f in (40, 56, 72, 88):  # easels dim in S06 (starts at 27s, 24 fps)
        place(tr, thud(), 27 + f / 24, 0.7)
    place(tr, boom(), 33.0, 0.8)  # 15 July 2010 card
    place(tr, buzz(), 44.15, 0.7, -0.2)  # phone buzz
    for t in (47.0, 48.5, 50.0, 51.5):  # quick cuts
        place(tr, tick(), t, 0.7)
    place(tr, ding(), 55.2, 0.5)  # loop ding
    return tr


def write(path, x):
    x = x / max(1e-9, np.max(np.abs(x))) * 0.89
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    write(os.path.join(HERE, "bed.wav"), music())
    write(os.path.join(HERE, "sfx.wav"), sfx())
    print("ok")
