"""Synthesise the music bed and SFX track for the comic ₹ Short (deterministic, no samples).

  python3 make_audio.py   ->  bed.wav, sfx.wav  (then encoded to .m4a by the caller)

Music: curious pizzicato in D minor (Dm–Bb–F–C), 100 bpm, Karplus–Strong plucks + soft shaker.
Adds a kick/clap groove for energy. SFX timings match the cuts and motion graphics in ../index.html.
"""
import math
import os
import wave

import numpy as np

SR = 44100
DUR = 62.929
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
        # kick on 1 and 3, clap on 2 and 4 from bar 1
        if bar >= 1:
            for k in range(4):
                if k % 2 == 0:
                    n = int(0.25 * SR)
                    tt = np.arange(n) / SR
                    kick = np.sin(2 * math.pi * np.cumsum(50 + 110 * np.exp(-tt * 30)) / SR) * np.exp(-tt * 9)
                    place(tr, kick, t + k * beat, 0.55, 0.0)
                else:
                    place(tr, env_noise(0.15, 0.001, 0.05, 3) * 0.6, t + k * beat, 0.18, 0.1)
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
    gen = {
        'whoosh': lambda: whoosh(0.5), 'swish': lambda: whoosh(0.3), 'pop': pop, 'thud': thud, 'boom': boom,
        'tick': tick, 'step': lambda: env_noise(0.08, 0.002, 0.02, 12) * 0.6, 'shimmer': shimmer, 'ding': ding,
        'ding2': lambda: ding(1760.0, 0.8), 'buzz': buzz, 'scratch12': lambda: scratch(1.2), 'scratch09': lambda: scratch(0.9),
        'sad': lambda: np.concatenate([ding(f, 0.32) * 0.5 for f in (392.0, 370.0, 349.2, 311.1)]),
        'counter': lambda: np.concatenate([tick() for _ in range(12)]),
    }
    events = [
        ('whoosh', 0.000, 0.5),  # frame 1
        ('pop', 0.609, 0.6),  # frame 1
        ('whoosh', 0.700, 0.6),  # frame 1
        ('thud', 1.374, 0.7),  # frame 1
        ('pop', 4.300, 0.6),  # frame 1
        ('pop', 4.623, 0.5),  # frame 1
        ('tick', 5.100, 0.6),  # frame 1
        ('whoosh', 6.030, 0.5),  # frame 2
        ('whoosh', 7.330, 0.5),  # frame 2
        ('pop', 7.569, 0.6),  # frame 2
        ('pop', 10.100, 0.6),  # frame 2
        ('pop', 11.000, 0.6),  # frame 2
        ('pop', 11.330, 0.5),  # frame 2
        ('pop', 11.530, 0.5),  # frame 2
        ('sad', 13.923, 0.6),  # frame 2
        ('thud', 15.614, 0.9),  # frame 2
        ('whoosh', 16.370, 0.5),  # frame 3
        ('pop', 17.720, 0.7),  # frame 3
        ('counter', 19.570, 0.5),  # frame 3
        ('boom', 20.570, 0.6),  # frame 3
        ('swish', 19.170, 0.15),  # frame 3
        ('swish', 19.490, 0.15),  # frame 3
        ('swish', 19.690, 0.15),  # frame 3
        ('swish', 19.850, 0.15),  # frame 3
        ('swish', 20.010, 0.15),  # frame 3
        ('swish', 20.170, 0.15),  # frame 3
        ('swish', 20.330, 0.15),  # frame 3
        ('swish', 20.490, 0.15),  # frame 3
        ('swish', 20.647, 0.15),  # frame 3
        ('swish', 20.801, 0.15),  # frame 3
        ('swish', 20.954, 0.15),  # frame 3
        ('swish', 21.108, 0.15),  # frame 3
        ('swish', 21.262, 0.15),  # frame 3
        ('swish', 21.415, 0.15),  # frame 3
        ('swish', 21.569, 0.15),  # frame 3
        ('swish', 21.723, 0.15),  # frame 3
        ('whoosh', 22.967, 0.35),  # frame 4
        ('whoosh', 24.275, 0.35),  # frame 4
        ('whoosh', 25.745, 0.35),  # frame 4
        ('whoosh', 23.800, 0.4),  # frame 4
        ('whoosh', 25.380, 0.4),  # frame 4
        ('whoosh', 27.980, 0.5),  # frame 4
        ('thud', 28.780, 0.8),  # frame 4
        ('scratch12', 30.662, 0.9),  # frame 5
        ('scratch09', 32.472, 0.9),  # frame 5
        ('pop', 32.166, 0.5),  # frame 5
        ('whoosh', 33.702, 0.5),  # frame 5
        ('pop', 34.880, 0.5),  # frame 5
        ('pop', 35.180, 0.5),  # frame 5
        ('shimmer', 36.569, 0.6),  # frame 5
        ('pop', 36.780, 0.6),  # frame 5
        ('whoosh', 37.934, 0.5),  # frame 5
        ('thud', 38.326, 0.7),  # frame 5
        ('pop', 38.621, 0.6),  # frame 5
        ('whoosh', 39.519, 0.5),  # frame 6
        ('pop', 39.830, 0.6),  # frame 6
        ('pop', 40.430, 0.5),  # frame 6
        ('thud', 41.205, 0.8),  # frame 6
        ('whoosh', 41.730, 0.4),  # frame 6
        ('tick', 42.135, 0.4),  # frame 6
        ('tick', 42.205, 0.4),  # frame 6
        ('tick', 42.274, 0.4),  # frame 6
        ('tick', 42.344, 0.4),  # frame 6
        ('tick', 42.413, 0.4),  # frame 6
        ('tick', 42.830, 0.7),  # frame 6
        ('tick', 43.065, 0.7),  # frame 6
        ('tick', 43.301, 0.7),  # frame 6
        ('tick', 43.536, 0.7),  # frame 6
        ('shimmer', 43.889, 0.6),  # frame 6
        ('boom', 44.597, 0.7),  # frame 6
        ('thud', 44.597, 0.9),  # frame 6
        ('boom', 46.860, 0.6),  # frame 7
        ('whoosh', 47.660, 0.5),  # frame 7
        ('step', 47.566, 0.35),  # frame 7
        ('step', 47.929, 0.35),  # frame 7
        ('step', 48.302, 0.35),  # frame 7
        ('step', 48.675, 0.35),  # frame 7
        ('step', 49.048, 0.35),  # frame 7
        ('step', 49.421, 0.35),  # frame 7
        ('step', 49.794, 0.35),  # frame 7
        ('step', 50.166, 0.35),  # frame 7
        ('whoosh', 50.960, 0.5),  # frame 7
        ('buzz', 52.029, 0.7),  # frame 7
        ('pop', 52.560, 0.7),  # frame 7
        ('boom', 52.760, 0.5),  # frame 7
        ('pop', 54.600, 0.6),  # frame 8
        ('pop', 55.900, 0.6),  # frame 8
        ('tick', 56.500, 0.6),  # frame 8
        ('pop', 57.200, 0.6),  # frame 8
        ('ding2', 57.400, 0.4),  # frame 8
        ('pop', 57.950, 0.6),  # frame 8
        ('whoosh', 58.850, 0.6),  # frame 8
        ('whoosh', 58.974, 0.4),  # frame 8
        ('boom', 61.985, 0.6),  # frame 8
        ('ding', 62.276, 0.45),  # frame 8
    ]
    for name, t, g in events:
        place(tr, gen[name](), t, g)
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
