import sys, json, torch, torchaudio
from chatterbox.tts import ChatterboxTTS
torch.manual_seed(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
m = ChatterboxTTS.from_pretrained(device="cpu")
for job in json.load(open(sys.argv[1])):
    torch.manual_seed(job.get("seed", 7))
    wav = m.generate(job["text"], audio_prompt_path=job["ref"], exaggeration=job["ex"], cfg_weight=job["cfg"], temperature=job.get("temp", 0.8))
    torchaudio.save(job["out"], wav, m.sr)
    print("wrote", job["out"], round(wav.shape[-1] / m.sr, 2), flush=True)
