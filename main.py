from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import os
from dotenv import load_dotenv

app = FastAPI(title="AI Baba – DeepSeek R1 (OpenRouter)")

# CORS (frontend ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()  # .env load karega

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# OpenRouter endpoint
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class ProfileData(BaseModel):
    username: str
    name: str
    bio: str


@app.post("/generate-report")
def generate_report(data: ProfileData):

    prompt = f"""
Tum ek aise baba ho jo Instagram ko samajhte ho. Har profile tumhare liye ek kitaab hai jismein insaan ki kahani likhi hai.

📖 **Is kitaab ke kuch panna:**
Naam: {data.name}
Username: {data.username}
Bio: {data.bio}

**Ab baba ki anubhooti se suno:**

**Part 1: First Impression (Funny)**
- Username dekhkar kya laga? (1-2 line joke)
- Bio padhkar kaisa feel hua? (3-4 lines)

**Part 2: Real Analysis (Simple & Deep)**
- Nature: Seedha hai ya complicated?
- Thinking: Positive hai ya negative?
- Feelings: Express karta hai ya chhupa leta hai?
- Confidence: Khud pe bharosa hai?
- Social: Kitna outgoing hai?

**Part 3: Baba Ki Baat (Wisdom + Advice)**
- Ek achhi baat batayo ismein
- Ek improvement ki suggestion do
- Ek chhota sa mantra/ritual batao daily ke liye
- bhai ek advice do jismei mujhe example ke sath dikhai jaisi bio se lage koi sad hai ya dhokha mila h toh ese bol himanshu website ke owner inske sath bhi esa hi huaa  2-3 lines mei

**RULES FOR BABA-STYLE:**
1. **Language:** Aisi Hindi jo 15 saal ka bacha bhi samjhe
2. **Tone:** Jaise bade bhai ya chacha samjha rahe ho
3. **Length:** 250-300 words total, zyada nahi
4. **Mix:** 30% humor + 40% analysis + 30% advice
5. **Connect:** Aajkal ke trends se jodo (reels, memes, etc.)

**EXAMPLE:**
"Arre {data.username}, tera username toh bada catchy hai! 😄
Par baba ko lagta hai tu andar se thoda confused hai...
Teri soch acchi hai, par himmat thodi kam hai.
Ek kaam kar: Roz subah 5 minute khud se baat kar.
Aur haan, zyada serious mat ho, life enjoy kar!"

**MANTRA FOR YOU:** "Baccha, tu achha hai. Bas thoda aur khul ke jee le!"
"""

    try:
        payload = {
            "model": "deepseek/deepseek-r1-0528:free",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            # Optional but recommended (OpenRouter ranking / tracking)
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "AI Baba Scanner"
        }

        res = requests.post(
            OPENROUTER_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=40
        )

        out = res.json()

        # 🔍 DEBUG (terminal me dikhega)
        print("OPENROUTER RAW RESPONSE 👉", out)

        # ❌ Safety check
        if "choices" not in out:
            return {
                "report": "⚠️ Baba keh rahe hain… gyaan ka flow ruk gaya 😅",
                "debug": out
            }

        report = out["choices"][0]["message"]["content"]

        return {"report": report}

    except Exception as e:
        return {
            "report": "❌ Baba tapasya me disturb ho gaye…",
            "error": str(e)
        }
