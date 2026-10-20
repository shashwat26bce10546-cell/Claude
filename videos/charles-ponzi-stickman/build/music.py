# Original synthesized score: light, curious, playful bed for the stickman explainer.
# Plucked arpeggio over a walking bass with a soft kick and shaker, 112 bpm.
# Chords move A minor -> F -> C -> G, brightest while the money pours in and sparser
# through the collapse (audit, banks closed, prison).
import numpy as np, os, subprocess, wave

os.chdir(os.path.join(os.path.dirname(__file__), ".."))
SR = 48000
DUR = 82.6           # voiceover is 81.6s; tail lets the last note ring out
BPM = 112.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT

n = int(DUR * SR)
t = np.arange(n) / SR
out = np.zeros(n)


def place(buf, start, sig):
    i = int(start * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += sig[: j - i]


def pluck(freq, dur, amp):
    """Short plucked tone: sine + a little 2nd/3rd harmonic, fast exponential decay."""
    k = np.arange(int(dur * SR)) / SR
    env = np.exp(-5.5 * k) * np.minimum(1.0, k / 0.004)
    tone = np.sin(2 * np.pi * freq * k) + 0.35 * np.sin(4 * np.pi * freq * k) + 0.12 * np.sin(6 * np.pi * freq * k)
    return amp * env * tone


def bass(freq, dur, amp):
    k = np.arange(int(dur * SR)) / SR
    env = np.exp(-2.2 * k) * np.minimum(1.0, k / 0.006)
    return amp * env * (np.sin(2 * np.pi * freq * k) + 0.2 * np.sin(4 * np.pi * freq * k))


def kick(amp):
    k = np.arange(int(0.26 * SR)) / SR
    return amp * np.exp(-26 * k) * np.sin(2 * np.pi * (48 + 60 * np.exp(-34 * k)) * k)


def shaker(amp, seed):
    rng = np.random.default_rng(seed)
    k = np.arange(int(0.09 * SR)) / SR
    noise = rng.standard_normal(len(k))
    return amp * np.exp(-42 * k) * noise


# chord cycle: Am - F - C - G (one bar each), arpeggiated as eighth notes
CHORDS = [
    (110.00, [220.00, 261.63, 329.63, 261.63, 220.00, 329.63, 261.63, 329.63]),   # Am
    (87.31, [174.61, 220.00, 261.63, 220.00, 174.61, 261.63, 220.00, 261.63]),    # F
    (130.81, [261.63, 329.63, 392.00, 329.63, 261.63, 392.00, 329.63, 392.00]),   # C
    (98.00, [196.00, 246.94, 293.66, 246.94, 196.00, 293.66, 246.94, 293.66]),    # G
]

bars = int(DUR / BAR) + 1
for b in range(bars):
    bar_t = b * BAR
    root, arp = CHORDS[b % 4]
    # darker, sparser pass for the chase/caught/prison stretch (~38s-50s)
    dark = 53.0 <= bar_t < 70.0        # the collapse: newspaper, audit, banks closed, prison
    lift = 35.0 <= bar_t < 48.0          # the queue and the money pouring in
    amp = 0.17 * (0.6 if dark else (1.15 if lift else 1.0))
    for i, f in enumerate(arp):
        if dark and i % 2:               # halve the note density in the dark section
            continue
        place(out, bar_t + i * BEAT / 2, pluck(f * (0.5 if dark else 1.0), 0.75, amp))
    place(out, bar_t, bass(root, BEAT * 1.6, 0.26))
    place(out, bar_t + 2 * BEAT, bass(root * 1.5, BEAT * 1.2, 0.18))
    place(out, bar_t, kick(0.5))
    place(out, bar_t + 2 * BEAT, kick(0.42))
    for i in range(8):                   # shaker on the off-beats
        if i % 2:
            place(out, bar_t + i * BEAT / 2, shaker(0.05 if not dark else 0.03, b * 8 + i))

# overall envelope: fade in, duck under the voiceover, fade out
env = np.ones(n)
env *= np.minimum(1.0, t / 1.2)
env *= np.where(t > DUR - 2.2, np.maximum(0.0, (DUR - t) / 2.2), 1.0)
out *= env
out /= max(1e-9, np.abs(out).max())
out *= 0.72
stereo = np.stack([out, np.roll(out, 240)], axis=1)   # slight width

pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2")
with wave.open("build/score.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "build/score.wav",
                "-af", "highpass=f=45,alimiter=limit=0.9",
                "-c:a", "libmp3lame", "-b:a", "192k", "assets/audio/score.mp3"], check=True)
os.remove("build/score.wav")
print("score.mp3 written")
