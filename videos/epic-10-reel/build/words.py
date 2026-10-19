# Hinglish (Roman) caption words: Whisper large-v3 word timings from the Hindi voiceover,
# with the Roman spelling for each word corrected by hand (the ASR mis-hears a few).
import json, os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
ROMAN = {
 "आग्रा,":"AGRA", "1666":"1666", "शिवाजी":"SHIVAJI", "महराज":"MAHARAJ", "को":"KO", "बुलाया":"BULAYA",
 "गया":"GAYA", "पर":"PAR", "ये":"YE", "निमंत्रन":"NIMANTRAN", "नहीं,":"NAHI", "एक":"EK", "चाल":"CHAAL",
  "दर्बार":"DARBAR", "में":"MEIN", "उन्हें":"UNHE", "पीछे":"PEECHE", "खड़ा":"KHADA",
 "किया":"KIYA", "इतना":"ITNA", "अपमान":"APMAAN", "और":"AUR", "ने":"NE", "मूँ":"MUNH", "मोर":"MOD",
 "लिया":"LIYA", "फिर":"PHIR", "शुरू":"SHURU", "हुई":"HUI", "नजरपंदी":"NAZARBANDI", "हर":"HAR",
 "तरफ":"TARAF", "पहरा,":"PEHRA", "कैद":"QAID", "तब":"TAB", "चली":"CHALI", "वो":"VO", "बिमार":"BIMAAR",
 "पड़":"PAD", "गए":"GAYE", "रोज":"ROZ", "मिठाई":"MITHAI", "के":"KE", "टोकरे":"TOKRE", "संत":"SANT",
 "दरबडियों":"DARBARIYON", "बाटे":"BAANTE", "जाने":"JAANE", "लगे":"LAGE", "पहरेदार":"PEHREDAAR",
 "आदी":"AADI", "हो":"HO", "बिस्तर":"BISTAR", "हमशकल":"HUM-SHAKAL", "उनकी":"UNKI", "चगा":"JAGAH",
 "लेटा":"LETA", "हुआ":"HUA", "रात":"RAAT", "दो":"DO", "टोकरों":"TOKRON", "सामभाजी":"SAMBHAJI",
 "रोका":"ROKA", "पल":"PAL", "लिए":"LIYE", "सांस":"SAANS", "धम":"THAM", "गई":"GAYI", "सुभा":"SUBAH",
 "तक":"TAK", "खाली":"KHALI", "जो":"JO", "स्वराज":"SWARAJ", "का":"KA", "सपना":"SAPNA", "लेकर":"LEKAR",
 "लोट":"LAUT", "आया":"AAYA",
}
# "था" is THI after "chaal" (feminine) and THA in the two later lines
THA_BY_INDEX = {13: "THI", 96: "THA", 100: "THA"}
# sentence ends (a caption group always breaks here)
BREAK_AFTER = {6, 13, 20, 28, 32, 38, 44, 48, 59, 63, 72, 80, 84, 91, 96, 107}
src = json.load(open("assets/audio/transcript.json"))
out = []
missing = set()
for i, w in enumerate(src):
    t = w["text"]
    r = THA_BY_INDEX.get(i) if t == "था" else ROMAN.get(t)
    if r is None:
        missing.add(t)
        r = t
    out.append({"text": r + ("." if i in BREAK_AFTER else ""), "start": w["start"], "end": w["end"]})
if missing:
    raise SystemExit("no Roman spelling for: " + ", ".join(sorted(missing)))
json.dump(out, open("build/words.json", "w"), ensure_ascii=False, indent=0)
print(len(out), "words")
