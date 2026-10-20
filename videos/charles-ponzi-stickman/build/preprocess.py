# Clips 1-15 in the user's order (verified against the script and the voiceover: each clip's
# artwork matches its scene, so the numbering is correct). Each clip is fitted to its narration
# line (retimed, motion-interpolated when slowed, then held on the last frame), and the result is upscaled to 1080x1920.
# The Gemini sparkle watermark orbits the bottom-right below y=1095. Blurring it out smears the flat
# artwork, so each clip is reframed to its top 1080 rows (a 1.17x push-in) and the watermark is gone.
import subprocess, os

os.chdir(os.path.join(os.path.dirname(__file__), ".."))

# scene starts, from the Scribe word timings (one per voiceover line)
S = [0, 6.20, 10.90, 16.65, 23.00, 29.55, 35.30, 41.05, 48.40, 53.25, 58.60, 62.65, 69.25, 74.20, 77.85]
END = 82.3
SRC = 4.01                      # every source clip is 4.01s

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "assets/audio/voiceover.mp3", "-af",
                "highpass=f=70,acompressor=threshold=-22dB:ratio=2.5:attack=5:release=100:makeup=2,"
                "loudnorm=I=-15:TP=-1.5:LRA=8",
                "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "192k",
                "assets/audio/voiceover-master.mp3"], check=True)

os.makedirs("media/prepped", exist_ok=True)
for i, s in enumerate(S):
    e = S[i + 1] if i + 1 < len(S) else END
    target = round(e - s + 0.5, 3)
    f = round(min(max(target / SRC, 0.72), 2.0), 4)   # retime factor, clamped
    speed = f"setpts={f}*PTS," + ("minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1"
                                  if f > 1.05 else "fps=30")
    vf = ("crop=608:1080:56:0," + speed +
          ",tpad=stop_mode=clone:stop_duration=10,scale=1080:1920:flags=lanczos,"
          "eq=contrast=1.02:saturation=1.04,trim=duration=%s,setpts=PTS-STARTPTS,format=yuv420p" % target)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"media/clips/{i+1}.mp4", "-an", "-vf", vf,
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-movflags", "+faststart",
                    f"media/prepped/s{i+1}.mp4"], check=True)
    print(f"slot {i+1:2d} <- clip {i+1}: -> {target}s @x{f}", flush=True)
