# Clips 1-15 in the user's order (verified against the script and the voiceover: each clip's
# artwork matches its scene, so the numbering is correct). Each clip is fitted to its narration
# line: played at natural speed (at most 1.08x) and, when the line runs longer than one pass of
# the clip, the clip plays again with a crossfade. Upscaled to 1080x1920.
# The Gemini sparkle watermark orbits the bottom-right below y=1095. Blurring it out smears the flat
# artwork, so each clip is reframed to its top 1080 rows (a 1.17x push-in) and the watermark is gone.
import subprocess, os

os.chdir(os.path.join(os.path.dirname(__file__), ".."))

# scene starts, from the Scribe word timings (one per voiceover line)
S = [0, 5.49, 9.15, 13.12, 19.06, 23.39, 27.37, 32.28, 36.43, 42.90, 46.83, 50.49, 56.03, 60.94, 65.13]
END = 70.2
SRC = 4.01                      # every source clip is 4.01s

# The delivered read is slower than the artwork's own animation, which made the cut drag. Speeding
# the voiceover up 1.12x (atempo keeps the pitch) lets every clip play at its own natural speed.
VO_SPEED = 1.12
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "assets/audio/voiceover.mp3", "-af",
                f"atempo={VO_SPEED},"
                "highpass=f=70,acompressor=threshold=-22dB:ratio=2.5:attack=5:release=100:makeup=2,"
                "loudnorm=I=-15:TP=-1.5:LRA=8",
                "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "192k",
                "assets/audio/voiceover-master.mp3"], check=True)

os.makedirs("media/prepped", exist_ok=True)
MAX_SLOW = 1.08         # essentially natural speed; the voiceover carries the pacing instead
XF = 0.5                # crossfade used when a scene outlasts one pass of the clip

for i, s in enumerate(S):
    e = S[i + 1] if i + 1 < len(S) else END
    target = round(e - s + 0.5, 3)
    f = round(min(max(target / SRC, 0.72), MAX_SLOW), 4)
    # Frame BLENDING, not motion-compensated interpolation: on flat cartoon art mci guesses motion
    # badly, which warped moving props and left the pacing uneven (visible as stutter).
    speed = f"setpts={f}*PTS," + ("minterpolate=fps=30:mi_mode=blend" if f > 1.02 else "fps=30")
    vf = ("crop=608:1080:56:0," + speed +
          ",scale=1080:1920:flags=lanczos,eq=contrast=1.02:saturation=1.04,format=yuv420p")
    pass_len = round(SRC * f, 3)
    out = f"media/prepped/s{i+1}.mp4"
    src = f"media/clips/{i+1}.mp4"
    enc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-movflags", "+faststart"]
    if target <= pass_len + 0.02:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an", "-vf",
                        vf + f",trim=duration={target},setpts=PTS-STARTPTS"] + enc + [out], check=True)
        note = ""
    else:
        # The scene outlasts one pass, so the clip plays again and the two passes are crossfaded.
        # Holding the last frame instead would read as a freeze, and stretching further looks slow.
        tail = round(target - pass_len + XF, 3)
        fc = (f"[0:v]{vf}[a];[1:v]{vf},trim=duration={tail},setpts=PTS-STARTPTS[b];"
              f"[a][b]xfade=transition=fade:duration={XF}:offset={round(pass_len - XF, 3)},"
              f"trim=duration={target},setpts=PTS-STARTPTS,format=yuv420p[v]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", src, "-an",
                        "-filter_complex", fc, "-map", "[v]"] + enc + [out], check=True)
        note = f" + {round(target - pass_len, 2)}s second pass"
    print(f"slot {i+1:2d} <- clip {i+1}: -> {target}s @x{f}{note}", flush=True)
