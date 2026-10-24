# Hinglish (Roman) caption words: Whisper large-v3 timings from the Hindi voiceover, with the Roman
# spelling fixed by hand. Whisper stuttered three phrases (emitting a zero-length duplicate copy of
# each); those copies are dropped.
import json, os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
DROP = set(range(28, 38)) | {116, 117, 118, 119} | {156, 157, 158}
ROMAN = {
 "लगभग":"LAGBHAG", "120":"120", "जवान,":"JAWAAN", "सामने":"SAAMNE", "कई":"KAI", "गुना":"GUNA",
 "दुश्मन":"DUSHMAN", "और":"AUR", "जमीनी":"JAMAATI", "ठंड":"THAND", "1962":"1962", "युद्ध,":"YUDDH",
 "लद्दाख":"LADAKH", "का":"KA", "चुशुल":"CHUSHUL", "हवाई":"HAWAI", "अड्डा":"ADDA", "बचाना":"BACHANA",
 "था":"THA", "से":"SE", "पहले":"PEHLE", "थी":"THI", "रेजांगला,":"REZANG LA", "16,000":"16,000",
 "फीट":"FEET", "उंची":"OONCHI", "पहाडी":"PAHAADI", "यहां":"YAHAN", "13":"13", "कुमाओं":"KUMAON",
 "की":"KI", "चारली":"CHARLIE", "कंपनी":"COMPANY", "थी,":"THI", "ज्यादातर":"ZYADATAR", "आहिर":"AHIR",
 "जवा":"JAWAAN", "जवान":"JAWAAN", "मेजर":"MAJOR", "शैतान":"SHAITAN", "सिंग":"SINGH", "के":"KE",
 "नितरित्व":"NETRITVA", "में,":"MEIN", "में":"MEIN", "ठंड,":"THAND", "कम":"KAM", "गरम":"GARAM", "कपड़े":"KAPDE",
 "तोप":"TOP", "खाने":"KHANE", "मदद":"MADAD", "नहीं":"NAHI", "18":"18", "नवंबर,":"NOVEMBER",
 "सुभा":"SUBAH", "पहले,":"PEHLE", "भारी":"BHAARI", "गोला":"GOLA", "बारी":"BAARI", "साथ":"SAATH",
 "हमला,":"HAMLA", "हमले":"HAMLE", "हुए":"HUE", "बार":"BAAR", "जवानों":"JAWAANON", "ने":"NE",
 "को":"KO", "रोका":"ROKA", "गोलियां":"GOLIYAAN", "खत्म":"KHATAM", "फिर":"PHIR", "भी":"BHI",
 "मोर्चे":"MORCHE", "पर":"PAR", "जमे":"JAME", "रहे":"RAHE", "गायल":"GHAYAL", "जाकर":"JAAKAR",
 "होसला":"HAUSLA", "बढ़ाते":"BADHATE", "कहा":"KAHA", "जाता":"JAATA", "है":"HAI",
 "उन्होंने":"UNHONE", "साथियों":"SAATHIYON", "उन्हें":"UNHE", "छोड़":"CHHOD", "देने":"DENE",
 "114":"114", "शहीद":"SHAHEED", "आखरी":"AAKHRI", "गोली":"GOLI", "तक":"TAK", "लड़ते":"LADTE",
 "बच":"BACH", "गया":"GAYA", "तीन":"TEEN", "दिन":"DIN", "बाद":"BAAD", "चाइना":"CHINA",
 "युद्ध":"YUDDH", "विराम":"VIRAAM", "किया":"KIYA", "कुछ":"KUCH", "महीने":"MAHINE",
 "चरवाहे":"CHARWAHE", "अपने":"APNE", "मोर्चों":"MORCHON", "मिले":"MILE", "परमवीर":"PARAM VIR",
 "चक्र":"CHAKRA", "बनी":"BANI", "रेजांगला":"REZANG LA",
}
# "साथ" is SAAT ("seven attacks") in the battle line, SAATH ("with") in "ke saath"
SAAT_BY_INDEX = {76, 79}
BREAK_AFTER = {9, 18, 27, 47, 53, 64, 75, 85, 94, 104, 115, 128, 139, 149, 162}
src = json.load(open("assets/audio/transcript.json"))
out, missing = [], set()
for i, w in enumerate(src):
    if i in DROP:
        continue
    r = "SAAT" if i in SAAT_BY_INDEX else ROMAN.get(w["text"])
    if r is None:
        missing.add(w["text"]); r = w["text"]
    out.append({"text": r + ("." if i in BREAK_AFTER else ""), "start": w["start"], "end": w["end"]})
if missing:
    raise SystemExit("no Roman spelling for: " + ", ".join(sorted(missing)))
json.dump(out, open("build/words.json", "w"), ensure_ascii=False, indent=0)
print(len(out), "words")
