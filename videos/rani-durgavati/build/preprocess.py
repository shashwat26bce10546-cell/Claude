# Corrected clip sequence for the Rani Durgavati voiceover (user numbering did not follow the story;
# clips 5 and 7 each contain two shots joined by a dissolve, clip 8 is a padded square video used twice).
# Each segment: clip, source in/out, output in/out; max slow-down factor (motion-interpolated above 1.0).
import subprocess, os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
END = 56.6
SEG = [
    # clip, src_in, src_out, out_in, max_speed, extra
    (8, 0.0, 5.0, 0.0, 1.3, "crop8"),
    (2, 0.0, 4.01, 4.94, 1.3, ""),
    (3, 0.0, 4.01, 10.7, 1.4, ""),
    (4, 0.0, 4.01, 16.3, 1.3, ""),
    (5, 0.0, 1.10, 21.26, 1.7, ""),          # prosperous Gondwana (before the statue dissolve)
    (7, 1.60, 4.01, 23.0, 1.4, ""),          # Singaurgarh-style hill fort (after the dissolve)
    (6, 0.0, 4.01, 27.14, 1.5, ""),
    (1, 0.0, 4.01, 32.98, 1.0, ""),
    (7, 0.0, 1.15, 36.2, 2.0, ""),           # battle charge on the elephant
    (9, 0.0, 4.01, 39.1, 1.3, ""),
    (8, 5.0, 10.0, 43.76, 1.4, "crop8,dark"),# sacrifice — same portrait, darker grade
    (5, 1.65, 4.01, 50.72, 1.3, ""),         # golden statue
    (10, 0.0, 4.01, 53.0, 1.3, ""),
]
os.makedirs("media/prepped", exist_ok=True)
starts = [s[3] for s in SEG]
subprocess.run(["ffmpeg","-v","error","-y","-i","assets/audio/voiceover.mp3","-af",
  "highpass=f=70,acompressor=threshold=-22dB:ratio=2.5:attack=5:release=100:makeup=2,loudnorm=I=-15:TP=-1.5:LRA=8",
  "-ar","48000","-c:a","libmp3lame","-b:a","192k","assets/audio/voiceover-master.mp3"], check=True)
for k, (clip, a, b, o, maxf, extra) in enumerate(SEG):
    o_end = starts[k + 1] if k + 1 < len(SEG) else END
    target = round(o_end - o + 0.6, 3)
    src = b - a
    f = round(min(max(target / src, 1.0), maxf), 4)
    vf = []
    if "crop8" in extra: vf.append("crop=380:676:170:336")
    vf.append(f"setpts={f}*PTS")
    vf.append("minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1" if f > 1.05 else "fps=30")
    vf += ["tpad=stop_mode=clone:stop_duration=10", "scale=1080:1920:flags=lanczos", "unsharp=5:5:0.7:5:5:0"]
    vf.append("eq=contrast=1.08:saturation=0.75:brightness=-0.05" if "dark" in extra else "eq=contrast=1.05:saturation=1.06")
    vf += [f"trim=duration={target}", "setpts=PTS-STARTPTS", "format=yuv420p"]
    if "crop8" in extra:
        # square shot padded inside the clip: show it full-width (face fully visible) over a blurred, darker copy
        speed = f"setpts={f}*PTS"
        mi = "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1" if f > 1.05 else "fps=30"
        grade = "eq=contrast=1.08:saturation=0.75:brightness=-0.05" if "dark" in extra else "eq=contrast=1.05:saturation=1.06"
        fc = (f"[0:v]crop=720:676:0:336,split[a][b];"
              f"[a]{speed},{mi},tpad=stop_mode=clone:stop_duration=10,scale=1080:1014:flags=lanczos,unsharp=5:5:0.7:5:5:0[fg];"
              f"[b]{speed},fps=30,tpad=stop_mode=clone:stop_duration=10,crop=380:676:170:0,scale=1080:1920,boxblur=28:2,eq=brightness=-0.18:saturation=0.8[bg];"
              f"[bg][fg]overlay=0:430,{grade},trim=duration={target},setpts=PTS-STARTPTS,format=yuv420p[v]")
        cmd = ["ffmpeg","-v","error","-y","-ss",str(a),"-t",str(src),"-i",f"media/clips/{clip}.mp4","-an",
               "-filter_complex",fc,"-map","[v]","-c:v","libx264","-crf","18","-preset","medium","-movflags","+faststart",
               f"media/prepped/s{k+1}.mp4"]
    else:
        cmd = ["ffmpeg","-v","error","-y","-ss",str(a),"-t",str(src),"-i",f"media/clips/{clip}.mp4","-an",
               "-vf",",".join(vf),"-c:v","libx264","-crf","18","-preset","medium","-movflags","+faststart",
               f"media/prepped/s{k+1}.mp4"]
    if os.environ.get("ONLY") and str(k + 1) not in os.environ["ONLY"].split(","):
        continue
    subprocess.run(cmd, check=True)
    print(f"slot {k+1:2d} <- clip {clip} [{a}-{b}] -> {target}s @x{f}")
