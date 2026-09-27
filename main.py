import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

app = FastAPI(title="AI Baba – Groq Stable Edition")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ProfileData(BaseModel):
    username: str
    name: str
    bio: str


# =========================================================
# PROMPT BUILDER
# =========================================================
def build_prompt(data: ProfileData) -> str:
    bio_text = data.bio.strip() if data.bio and data.bio.strip() else "BABA — is bande ne bio nahi likhi"
    username_text = data.username.strip() if data.username else "unknown"
    name_text = data.name.strip() if data.name else "Baccha"

    return f"""Tu "AI Baba" hai — Instagram profile dekhkar funny + warm + thodi deep baat karne wala bada bhai.

Developer ka naam: **Himanshu Yadav** (raat ko code likhta hai, chai peeta hai, bugs se ladta hai).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NAAM: {name_text}
USERNAME: @{username_text}
BIO: "{bio_text}"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 SABSE ZAROORI 3 RULES:

**RULE 1 — NAAM SE BAAT KARO:** Har section mein "{name_text}" naam use karo. Total 4-6 baar.

**RULE 2 — BIO KE EXACT WORDS QUOTE KARO:** Bio ke words direct output mein quote karo.

**RULE 3 — USERNAME "@{username_text}" PAR COMMENT:** 1 line observation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 OUTPUT FORMAT — POORA LIKHNA ZAROORI HAI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🔥 Pehli Nazar
Naam + username + bio observation (3 lines minimum)

## 🧠 Baba Ki Reading — {name_text}
- **Nature:** {name_text} lagta hai... (poori line likho)
- **Thinking:** ...
- **Feelings:** ...
- **Confidence:** ...
- **Social:** ...

## 😂 Himanshu Connection
Himanshu aur {name_text} ka funny connection (2 lines)

## ❤️ Dil Ki Baat — {name_text} Sun
SIRF agar bio mein sad emoji ho (💔 🥀 😔). Warna skip karo.

## 🔮 Baba Ki Salah — {name_text} Ke Liye
- **Achhi baat:** {name_text}, tere mein...
- **Improvement:** {name_text}, ek change la...
- **Mantra:** Roz {name_text} ye bol — "..."

## 🕉️ Final Mantra
1-2 lines, {name_text} ke saath.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ LENGTH RULE — 250-300 WORDS MINIMUM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Report 250-300 words ki honi chahiye. Har section poora likho.
Agar short likha toh report reject ho jayegi aur dobara banani padegi.

Language: Simple Hindi/Hinglish. Tone: Bada bhai. Emojis natural.

Ab POORI report do — kam se kam 250 words:"""
    

# =========================================================
# HELPER — WORD COUNT CHECK
# =========================================================
def is_valid_report(report: str) -> tuple[bool, str]:
    """Check karo report valid hai ya nahi."""
    if not report:
        return False, "empty"
    
    report = report.strip()
    words = len(report.split())
    
    if words < 150:
        return False, f"too_short ({words} words)"
    
    # Prompt markers check — agar prompt repeat hua ho
    markers = ["RULE 1", "OUTPUT FORMAT", "━━━━━", "SABSE ZAROORI"]
    for m in markers:
        if m in report:
            return False, f"prompt_echo ({m})"
    
    return True, f"valid ({words} words)"


# =========================================================
# GENERATE REPORT
# =========================================================
@app.post("/generate-report")
def generate_report(data: ProfileData):
    
    if not GROQ_API_KEY:
        return {"report": "Baba ki chabi (.env GROQ_API_KEY) nahi mili 😅"}
    
    clean = ProfileData(
        username=data.username.strip()[:100],
        name=data.name.strip()[:100],
        bio=data.bio.strip()[:500]
    )
    
    prompt = build_prompt(clean)
    
    # ✅ Retry logic — 3 attempts
    last_report = ""
    last_reason = ""
    
    for attempt in range(3):
        try:
            print(f"\n🚀 Attempt {attempt + 1}/3 — Model: {GROQ_MODEL}")
            
            res = requests.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Tu AI Baba hai. Sirf final report output karta hai. "
                                "Minimum 250 words likhna. Koi explanation nahi, koi prompt repetition nahi. "
                                "Seedha 'Arre {name}, ...' se shuru kar."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.8,
                    "max_tokens": 2000,          # ✅ 1000 → 2000
                    "top_p": 0.9,
                    "reasoning_effort": "low"    # ✅ Reasoning कम — report के लिए ज़्यादा tokens
                },
                timeout=90
            )
            
            if res.status_code != 200:
                print(f"❌ HTTP {res.status_code}: {res.text[:200]}")
                last_reason = f"http_{res.status_code}"
                continue
            
            data_json = res.json()
            
            if "choices" not in data_json or not data_json["choices"]:
                last_reason = "no_choices"
                continue
            
            report = data_json["choices"][0].get("message", {}).get("content", "")
            
            # ✅ Validate
            is_valid, reason = is_valid_report(report)
            print(f"📊 {reason}")
            
            if is_valid:
                print(f"✅ Report accepted on attempt {attempt + 1}")
                return {
                    "report": report.strip(),
                    "model": data_json.get("model", GROQ_MODEL),
                    "attempt": attempt + 1
                }
            else:
                last_report = report.strip()
                last_reason = reason
                print(f"⚠️ Rejected ({reason}), retrying...")
                continue
        
        except requests.exceptions.Timeout:
            print("⏱️ Timeout")
            last_reason = "timeout"
            continue
        except Exception as e:
            print(f"💥 Error: {e}")
            last_reason = str(e)[:100]
            continue
    
    # ❌ All attempts failed
    print(f"\n❌ All 3 attempts failed. Last reason: {last_reason}")
    
    # Agar koi report मिली थी (short), toh wo return कर दो
    if last_report and len(last_report) > 50:
        return {
            "report": last_report,
            "model": GROQ_MODEL,
            "warning": f"Short report ({last_reason})"
        }
    
    return {
        "report": "Baba thoda busy hain 😅 Thodi der baad try karo baccha.",
        "error": last_reason
    }


# =========================================================
# HEALTH
# =========================================================
@app.get("/")
def root():
    return {
        "status": "online",
        "provider": "Groq",
        "model": GROQ_MODEL,
        "api_key_configured": bool(GROQ_API_KEY)
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": GROQ_MODEL,
        "api_key_configured": bool(GROQ_API_KEY)
    }
