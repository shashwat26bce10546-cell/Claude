# Hinglish (Roman) caption words: Whisper large-v3 timings from the Hindi voiceover, with the Roman
# spelling for each word fixed by hand. Whisper stuttered one phrase (it emitted "lehar par lehar par
# dushman aage nahi" twice, the first copy squeezed into 0.1s); the bad copy is dropped.
import json, os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
DROP = set(range(70, 78))          # the duplicated, zero-length copy
ROMAN = {
 "21":"21", "सिपाही":"SIPAHI", "और":"AUR", "सामने":"SAAMNE", "हजारों":"HAZAARON", "दुश्मन":"DUSHMAN",
 "1897":"1897", "नौथ":"NORTH", "वेस्ट":"WEST", "फ्रंटियर":"FRONTIER", "सालागढी":"SARAGARHI",
 "नाम":"NAAM", "की":"KI", "एक":"EK", "छोटी":"CHHOTI", "सी":"SI", "चौकी":"CHOWKI", "दो":"DO",
 "बड़े":"BADE", "किलों":"KILON", "के":"KE", "बीच":"BEECH", "संदेश":"SANDESH", "का":"KA",
 "मात्र":"MAATRA", "रास्ता":"RAASTA", "हविलदार":"HAVILDAR", "इशार":"ISHAR", "सिंग":"SINGH",
 "ने":"NE", "दूर":"DOOR", "से":"SE", "उठती":"UTHTI", "धूल":"DHOOL", "देखी":"DEKHI",
 "आफरीदी":"AFRIDI", "ओरकजाई":"ORAKZAI", "हमलावर":"HAMLAWAR", "ही":"HI", "निशाने":"NISHAANE",
 "पर":"PAR", "गुर्मुक":"GURMUKH", "भेजा":"BHEJA", "हम":"HUM", "हमला":"HAMLA", "हो":"HO",
 "गया":"GAYA", "है":"HAI", "मदद":"MADAD", "थी":"THI", "बहुत":"BAHUT", "भाग":"BHAAG",
 "जाना":"JAANA", "या":"YA", "खड़े":"KHADE", "रहना":"REHNA", "उन्होंने":"UNHONE", "चुना":"CHUNA",
 "लहर":"LEHAR", "आगे":"AAGE", "नहीं":"NAHI", "बढ़":"BADH", "पाया":"PAAYA", "आखरी":"AAKHRI",
 "तक":"TAK", "सिग्निलर":"SIGNALLER", "अपनी":"APNI", "जगह":"JAGAH", "रहा":"RAHA",
 "दिवार":"DEEWAR", "तूट":"TOOT", "गई":"GAYI", "हिम्मत":"HIMMAT", "फिर":"PHIR",
 "खामोशी":"KHAMOSHI", "सारी":"SAARI", "गिर":"GIR", "सारे":"SAARE", "शहीद":"SHAHEED",
 "हुए":"HUE", "उनकी":"UNKI", "वजह":"VAJAH", "आसपास":"AASPAAS", "किले":"KILE", "बच":"BACH",
 "गए":"GAYE",
}
BREAK_AFTER = {5, 9, 16, 26, 35, 44, 55, 60, 69, 86, 93, 99, 104, 112, 120}   # sentence ends
src = json.load(open("assets/audio/transcript.json"))
out, missing = [], set()
for i, w in enumerate(src):
    if i in DROP:
        continue
    r = ROMAN.get(w["text"])
    if r is None:
        missing.add(w["text"])
        r = w["text"]
    out.append({"text": r + ("." if i in BREAK_AFTER else ""), "start": w["start"], "end": w["end"]})
if missing:
    raise SystemExit("no Roman spelling for: " + ", ".join(sorted(missing)))
json.dump(out, open("build/words.json", "w"), ensure_ascii=False, indent=0)
print(len(out), "words")
