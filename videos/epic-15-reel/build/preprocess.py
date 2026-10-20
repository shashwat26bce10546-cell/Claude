# Saragarhi (1897). The user's clips follow the voiceover almost 1:1, with two corrections:
#   * clip 3 (the signal beam between the two hill forts) covers two narration lines, so it runs long;
#   * clip 9 (the two Afridi/Orakzai chiefs) belongs with the line that names them, i.e. BEFORE the
#     charge in clip 5 — in the user's numbering it sat after the defenders' line.
# Clip 7 is unusable: it is a three-panel collage (a face crop, the wide shot and a hands crop
# stacked) for its whole length, never a single full-frame shot. The "help was far away" line uses
# clip 2's distant dawn ridge instead, from 1.5s in so it is framed differently from its own scene.
# Segments shorter than the 4.01s source are trimmed rather than sped up; longer ones are slowed with
# motion interpolation and then held. The sparkle watermark sits below y=1080 of the 720x1280 source,
# so every clip is reframed to its top 1080 rows (a 1.17x push-in).
import subprocess, os

os.chdir(os.path.join(os.path.dirname(__file__), ".."))
SRC = 4.01
END = 49.0

# clip, src_in, out_in   (out_out is the next segment's out_in, or END)
SEG = [
    (1,  0.0,  0.00),   # lone sentry above thousands
    (2,  0.0,  4.10),   # 1897, the North-West Frontier
    (3,  0.0,  7.40),   # Saragarhi post + the only signal route between the two forts (two lines)
    (4,  0.0, 14.05),   # Havildar Ishar Singh sees the dust
    (9,  0.0, 17.15),   # the Afridi and Orakzai chiefs
    (5,  0.0, 19.00),   # the charge, all on one target
    (6,  0.0, 20.95),   # Gurmukh Singh signals "we are under attack"
    (2,  1.5, 23.90),   # help is far away (clip 7 dropped: three-panel collage)
    (8,  0.0, 26.60),   # they chose to stand
    (10, 0.0, 30.60),   # wave after wave on the wall
    (11, 0.0, 33.40),   # the signaller stays at his post
    (12, 0.0, 35.95),   # the wall is breached
    (13, 0.0, 38.70),   # the last message, then silence
    (14, 0.0, 41.50),   # the post falls, all 21 killed
    (15, 0.0, 45.40),   # the forts around them held
]

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "assets/audio/voiceover.mp3", "-af",
                "highpass=f=70,acompressor=threshold=-22dB:ratio=2.5:attack=5:release=100:makeup=2,"
                "loudnorm=I=-15:TP=-1.5:LRA=8",
                "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "192k",
                "assets/audio/voiceover-master.mp3"], check=True)

os.makedirs("media/prepped", exist_ok=True)
for i, (clip, src_in, out_in) in enumerate(SEG):
    out_out = SEG[i + 1][2] if i + 1 < len(SEG) else END
    target = round(out_out - out_in + 0.4, 3)
    avail = SRC - src_in
    f = round(min(max(target / avail, 1.0), 2.0), 4)
    speed = f"setpts={f}*PTS," + ("minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1"
                                  if f > 1.05 else "fps=30")
    vf = ("crop=608:1080:56:0," + speed +
          ",tpad=stop_mode=clone:stop_duration=10,scale=1080:1920:flags=lanczos,"
          "unsharp=5:5:0.4:5:5:0,eq=contrast=1.04:saturation=1.05,"
          "trim=duration=%s,setpts=PTS-STARTPTS,format=yuv420p" % target)
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if src_in:
        cmd += ["-ss", str(src_in)]
    cmd += ["-i", f"media/clips/{clip}.mp4", "-an", "-vf", vf, "-c:v", "libx264", "-crf", "18",
            "-preset", "medium", "-movflags", "+faststart", f"media/prepped/s{i+1}.mp4"]
    subprocess.run(cmd, check=True)
    print(f"slot {i+1:2d} <- clip {clip:2d} @{src_in}: -> {target}s @x{f}", flush=True)
