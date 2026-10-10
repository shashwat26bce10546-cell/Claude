#!/bin/bash
# Original synthesized cinematic bed (58.6s): D-minor drone, 80bpm heartbeat drum,
# quiet drop for the Dhamma section, swell to D major for the finale.
set -euo pipefail
cd "$(dirname "$0")/.."
D=58.6
# drone: D2 A2 D3 F3 (minor) -> F#3 (major) after 51.2s, slow tremolo + shimmer
ffmpeg -v error -y -f lavfi -i "aevalsrc='\
0.30*sin(2*PI*73.42*t)+0.22*sin(2*PI*110*t+0.3*sin(2*PI*0.11*t))+0.16*sin(2*PI*146.83*t)\
+0.12*lt(t,51.2)*sin(2*PI*174.61*t)+0.12*gte(t,51.2)*min(1,(t-51.2)/1.5)*sin(2*PI*185.0*t)\
+0.06*sin(2*PI*220*t+2*sin(2*PI*0.07*t))+0.04*sin(2*PI*293.66*t)*(0.5+0.5*sin(2*PI*0.2*t))\
|0.30*sin(2*PI*73.6*t)+0.22*sin(2*PI*110.3*t)+0.16*sin(2*PI*147.1*t)\
+0.12*lt(t,51.2)*sin(2*PI*174.9*t)+0.12*gte(t,51.2)*min(1,(t-51.2)/1.5)*sin(2*PI*185.4*t)\
+0.06*sin(2*PI*220.4*t+2*sin(2*PI*0.05*t))+0.04*sin(2*PI*294*t)*(0.5+0.5*cos(2*PI*0.2*t))':s=48000:d=$D" \
  -af "lowpass=f=1800,aecho=0.8:0.7:120|260:0.35|0.25,volume=0.55" build/drone.wav
# heartbeat drum (taiko-like): one 0.75s double-hit beat looped at 80bpm,
# gated to 6.16-28.3 and 34.6-51.2, plus one deep boom at 51.2
ffmpeg -v error -y -f lavfi -i "aevalsrc='sin(2*PI*(52+40*exp(-30*t))*t)*exp(-7*t)+0.6*gt(t,0.22)*sin(2*PI*(50+30*exp(-30*(t-0.22)))*(t-0.22))*exp(-9*(t-0.22))':s=48000:d=0.75" build/beat.wav
ffmpeg -v error -y -stream_loop 80 -i build/beat.wav -f lavfi -i "aevalsrc='gt(t,51.2)*sin(2*PI*(45+40*exp(-20*max(0,t-51.2)))*max(0,t-51.2))*exp(-2.5*max(0,t-51.2))':s=48000:d=$D" -filter_complex \
  "[0]atrim=duration=$D,volume='(gt(t,6.16)*lt(t,28.3)+gt(t,34.6)*lt(t,51.2))*0.9':eval=frame[b];[b][1]amix=inputs=2:normalize=0,lowpass=f=400,aecho=0.6:0.5:60:0.3" -ac 2 build/drum.wav
# mix + overall envelope (fade in, dip in Dhamma section, fade out)
ffmpeg -v error -y -i build/drone.wav -i build/drum.wav -filter_complex \
  "[0][1]amix=inputs=2:normalize=0,volume='if(lt(t,1.5),t/1.5,1)*if(between(t,28.3,34.6),0.55,1)':eval=frame,afade=t=out:st=56.6:d=2,alimiter=limit=0.9" \
  -ar 48000 -c:a libmp3lame -b:a 192k assets/audio/score.mp3
rm -f build/drone.wav build/drum.wav build/beat.wav
