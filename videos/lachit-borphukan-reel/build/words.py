# Hinglish (Roman) caption words for the Lachit Borphukan reel.
# The full Whisper large-v3 pass skipped lines 9-12 (about 15s), so that stretch was re-transcribed on
# its own and spliced in: build/transcript-merged.json. This script maps each Hindi word to its Roman
# caption spelling, fixing what the ASR mis-heard (it hears "Mughal" as "Mukhal" and 1667 as 1687).
import json, os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
ROMAN = {
 "1671":"1671", "1687":"1667", "24":"24", "अधूरा":"ADHOORA", "असाम,":"ASSAM", "अहोम":"AHOM", "आज":"AAJ",
 "उठे":"UTHE", "उनकी":"UNKI", "उनके":"UNKE", "उन्होंने":"UNHONE", "एक":"EK", "औरंगजेब":"AURANGZEB",
 "कडी":"KADI", "कमजोर":"KAMZOR", "करने":"KARNE", "करो":"KARO", "कहा":"KAHA", "की":"KI", "के":"KE",
 "को":"KO", "खुद":"KHUD", "खुली":"KHULI", "गंभीर":"GAMBHIR", "गई,":"GAYI", "गए,":"GAYE",
 "गुहाटी":"GUWAHATI", "घुडसावार":"GHUDSAWAAR", "चले":"CHALE", "चुनी":"CHUNI", "छोटी":"CHHOTI",
 "छोड":"CHHOD", "जंग":"JANG", "जगा":"JAGAH", "जनरल":"GENERAL", "जमीन":"ZAMEEN", "जाता":"JAATA",
 "तरफ":"TARAF", "ताकतवर":"TAAKATWAR", "तूटी":"TOOTI", "तेज":"TEZ", "थी":"THI", "थे":"THE",
 "दिया":"DIYA", "दिवस":"DIVAS", "दी":"DI", "देश":"DESH", "नदी":"NADI", "नवंबर":"NOVEMBER",
 "नहीं":"NAHI", "नावें":"NAAVEIN", "नावों":"NAAVON", "ने":"NE", "नौ":"NAU", "पड़ा":"PADA",
 "पड़ी":"PADI", "पर":"PAR", "पार":"PAAR", "प्लान,":"PLAN", "बड़ा":"BADA", "बड़ी":"BADI",
 "बनवाए":"BANWAYE", "बहुत":"BAHUT", "बांध":"BANDH", "बाद":"BAAD", "बिस्तर":"BISTAR",
 "बीमार":"BIMAAR", "बोरफुकन":"BORPHUKAN", "बोल":"BOL", "ब्रह्मपुत्र":"BRAHMAPUTRA", "भी":"BHI",
 "भेजा":"BHEJA", "मजबूर":"MAJBOOR", "मामा":"MAMA", "मार्च":"MARCH", "मिट्टी":"MITTI",
 "मुखल":"MUGHAL", "मुखलों":"MUGHALON", "मुगल":"MUGHAL", "मेरा":"MERA", "मेरे":"MERE", "रहा":"RAHA",
 "राम":"RAM", "रूप":"ROOP", "लगे":"LAGE", "लचित":"LACHIT", "लड़ने":"LADNE", "लिया":"LIYA",
 "लोटना":"LAUTNA", "वापस":"WAAPAS", "वे":"VE", "शब्द":"SHABD", "सजा":"SAZAA", "सबसे":"SABSE",
 "साथ":"SAATH", "साल":"SAAL", "सिंग":"SINGH", "सिर्फ":"SIRF", "सीधा":"SEEDHA", "से":"SE",
 "सेना":"SENA", "हमला":"HAMLA", "हर":"HAR", "हराया":"HARAYA", "हार":"HAAR", "है":"HAI",
}
# "साथ" is SAAT ("seven boats") in line 12, SAATH ("with") elsewhere
src = json.load(open("build/transcript-merged.json"))
saat = {i for i, w in enumerate(src) if w["text"] == "साथ" and i + 1 < len(src) and src[i + 1]["text"] == "नावों"}
# sentence ends: the last word before each narration line starts
LINE_STARTS = [2.62, 7.92, 11.18, 14.38, 18.30, 21.72, 25.68, 29.75, 33.57, 38.13, 41.73, 44.88, 47.90, 51.42]
out, missing = [], set()
for i, w in enumerate(src):
    r = "SAAT" if i in saat else ROMAN.get(w["text"])
    if r is None:
        missing.add(w["text"]); r = w["text"]
    nxt = src[i + 1]["start"] if i + 1 < len(src) else 1e9
    end_of_line = i + 1 == len(src) or any(w["start"] < t <= nxt + 0.01 for t in LINE_STARTS)
    out.append({"text": r + ("." if end_of_line else ""), "start": w["start"], "end": w["end"]})
if missing:
    raise SystemExit("no Roman spelling for: " + ", ".join(sorted(missing)))
json.dump(out, open("build/words.json", "w"), ensure_ascii=False, indent=0)
print(len(out), "words")
