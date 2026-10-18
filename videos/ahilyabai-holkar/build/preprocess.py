# Clips 1-15 in the user's order (verified against script + voiceover). Each fitted to its narration line
# (slow up to 1.3x, motion-interpolated, then hold), watermark sparkles cropped out (they orbit in the bottom-right, y>1085, so a
# 1.18x reframe of the top 1080 rows removes them cleanly instead of a smeary delogo), upscaled to 1080x1920.
import subprocess, os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
S = [0, 4.44, 8.1, 12.62, 17.1, 21.02, 24.16, 28.3, 32.34, 36.48, 39.58, 43.4, 47.5, 51.62, 55.96]
END = 61.4
subprocess.run(["ffmpeg","-v","error","-y","-i","assets/audio/voiceover.mp3","-af",
  "highpass=f=70,acompressor=threshold=-22dB:ratio=2.5:attack=5:release=100:makeup=2,loudnorm=I=-15:TP=-1.5:LRA=8",
  "-ar","48000","-c:a","libmp3lame","-b:a","192k","assets/audio/voiceover-master.mp3"], check=True)
os.makedirs("media/prepped", exist_ok=True)
for i, s in enumerate(S):
    e = S[i + 1] if i + 1 < len(S) else END
    target = round(e - s + 0.6, 3)
    f = round(min(max(target / 4.01, 1.0), 1.3), 4)
    speed = f"setpts={f}*PTS," + ("minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1" if f > 1.05 else "fps=30")
    vf = ("crop=608:1080:56:0," + speed +
          ",tpad=stop_mode=clone:stop_duration=10,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6:5:5:0,"
          "eq=contrast=1.04:saturation=1.05,trim=duration=%s,setpts=PTS-STARTPTS,format=yuv420p" % target)
    subprocess.run(["ffmpeg","-v","error","-y","-i",f"media/clips/{i+1}.mp4","-an","-vf",vf,"-c:v","libx264","-crf","18",
                    "-preset","medium","-movflags","+faststart",f"media/prepped/s{i+1}.mp4"], check=True)
    print(f"slot {i+1:2d} <- clip {i+1}: -> {target}s @x{f}")
