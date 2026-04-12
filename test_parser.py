import json
import re

def yaniti_ayristir(ham_metin: str):
    metin = ham_metin.strip()
    metin = re.sub(r"^```[a-zA-Z]*\n", "", metin)
    metin = re.sub(r"\n```$", "", metin)
    metin = metin.strip()
    
    try:
        data = json.loads(metin)
        if data.get("type") in ["error", "refusal"]:
            return data.get("content", ""), ""
        return data.get("explain", ""), data.get("content", "")
    except Exception:
        pass
        
    aciklama = ""
    komut = ""
    
    metin = re.sub(r"```[a-zA-Z]*\n", " ", ham_metin)
    metin = metin.replace("```", "")
    
    if not re.search(r"(AÇIKLAMA|DESCRIPTION|KOMUT|COMMAND)\s*:", metin, re.IGNORECASE):
        # THIS IS THE FALLBACK I AM CURIOUS ABOUT
        return "", ""

    # ...rest
    return "X", "Y"

print("1:", yaniti_ayristir("Hello! How can I help you?"))
print("2:", yaniti_ayristir('{"type": "command", "content": "hello"}'))
