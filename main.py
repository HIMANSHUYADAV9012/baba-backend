from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

import httpx
import os
import json
import asyncio


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# .env me specific model set kar sakte ho.
# Agar model set nahi hai to OpenRouter free router use hoga.
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free"
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Frontend URL
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000"
)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="AI Baba – Fast AI Scanner",
    version="2.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    # Production me apne actual domain ko yahan .env se set karna
    allow_origins=["*"],

    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class ProfileData(BaseModel):
    username: str
    name: str
    bio: str


# =========================================================
# PROMPT BUILDER
# =========================================================

def build_prompt(data: ProfileData) -> str:

    return f"""
Tum "AI Baba" ho — Instagram profiles ko dekhkar funny,
interesting aur friendly analysis dene wale bade bhai/chacha.

Tumhare website ke developer ka naam **Himanshu Yadav** hai.
Himanshu ek **developer** hai aur usne ye AI Baba website banayi hai.

PROFILE:
Naam: {data.name}
Username: {data.username}
Bio: {data.bio}

==================================================
IMPORTANT PERSONALITY RULE
==================================================

Profile ke sirf username, naam aur bio ko dekhkar
entertaining "vibe analysis" karo.


In words ka use karo:
"lagta hai", "vibe aa rahi hai", "bio se feel hota hai",
"shayad", "aisa lag raha hai".

Agar evidence nahi hai to kuch assume mat karo.

==================================================
BABA STYLE
==================================================

Language:
Simple Hindi/Hinglish.

Tone:
Jaise koi funny bada bhai ya chacha samjha raha ho.

Style:
Funny + relatable + thoda emotional + useful.

Instagram culture ke references naturally use karo:
Reels, memes, stories, DM, seen, followers, likes etc.

Maximum 150-180 words.

Short paragraphs rakho.
Har section readable hona chahiye.

==================================================
PART 1 — 🔥 FIRST IMPRESSION
==================================================

Username dekhkar 1 funny observation.

Naam aur bio dekhkar 2-3 lines ki first impression.

Example style:

"Arre bhai, username dekhkar lag raha hai
ki creativity ne attendance laga di hai 😂"

Lekin har profile ke hisaab se ORIGINAL observation do.

==================================================
PART 2 — 🧠 BABA ANALYSIS
==================================================

In 5 points ko short me analyze karo:

Nature:
Bio se kaisi vibe aa rahi hai?

Thinking:
Simple, creative, serious, chill ya overthinking type
ki vibe hai?

Feelings:
Feelings openly express karta hua lagta hai
ya thoda private?

Confidence:
Profile se confidence wali vibe aati hai ya shy/chill?

Social:
Outgoing, social, selective ya private type ki vibe?

IMPORTANT:
Ye observations sirf profile vibe hain,
confirmed personality facts nahi.

==================================================
PART 3 — 😂 HIMANSHU CONNECTION
==================================================

Kabhi-kabhi natural jagah par website ke developer
**Himanshu Yadav**, jo developer hai, ka funny reference do.

Example:

"Waise Himanshu Yadav developer hai,
toh bhai teri bio dekhkar lagta hai
Himanshu ko bhi is profile ka code debug karna padega 😂"

YA:

"Himanshu ne website bana di,
ab Baba tumhari bio ka bhi debugging kar rahe hain 😂"

IMPORTANT:
Har report me same joke repeat mat karo.
Sirf tab use karo jab naturally fit ho.

==================================================
PART 4 — ❤️ EMOTIONAL / SAD VIBE
==================================================

Agar bio me clearly heartbreak, sadness, betrayal,
loneliness, emotional ya relationship-related vibe ho,
toh 2-3 relatable lines likho.

Example:

"Bio me thodi heartbreak wali vibe aa rahi hai 😅
Lagta hai kisi ne 'seen' ko permanent bana diya.
Himanshu developer hai, par Baba bhi is case ka
emotional bug fix nahi kar paayenge 😂"

Lekin agar bio me aisi koi indication nahi hai,
toh heartbreak assume mat karo.

==================================================
PART 5 — 🔮 BABA KI BAAT
==================================================

Exactly ye 3 cheezein do:

• Ek achhi baat
• Ek improvement suggestion
• Ek simple daily mantra

Advice practical aur short honi chahiye.

==================================================
FINAL MANTRA
==================================================

End me ek short Baba-style line do.

Example:

"Baba mantra: Baccha, tu achha hai.
Bas thoda aur khul ke jee le! 😄"

==================================================
IMPORTANT OUTPUT RULES
==================================================

- Sirf final Baba report do.
- Koi explanation mat do.
- 150-180 words maximum.
- Simple Hindi/Hinglish.
- Funny but respectful.
- Har profile ke liye observations unique rakho.
- Himanshu Yadav ka reference natural jagah par hi use karo.
- Same joke baar-baar repeat mat karo.
- Sad/heartbreak/relationship situation tabhi mention karo
  jab bio se uski reasonable indication mile.
- Kisi bhi assumption ko confirmed fact ki tarah mat likho.
"""

# =========================================================
# COMMON HEADERS
# =========================================================

def get_headers():

    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",

        # OpenRouter analytics ke liye
        "HTTP-Referer": FRONTEND_URL,

        "X-Title": "AI Baba Scanner"
    }


# =========================================================
# NORMAL GENERATE REPORT
# =========================================================

@app.post("/generate-report")
async def generate_report(data: ProfileData):

    # -----------------------------------------------------
    # API KEY CHECK
    # -----------------------------------------------------

    if not OPENROUTER_API_KEY:
        return {
            "report": "Baba ki chabi (.env API key) nahi mili 😅"
        }


    # -----------------------------------------------------
    # INPUT CLEANING
    # -----------------------------------------------------

    username = data.username.strip()[:100]
    name = data.name.strip()[:100]
    bio = data.bio.strip()[:500]

    clean_data = ProfileData(
        username=username,
        name=name,
        bio=bio
    )


    # -----------------------------------------------------
    # PROMPT
    # -----------------------------------------------------

    prompt = build_prompt(clean_data)


    # -----------------------------------------------------
    # PAYLOAD
    # -----------------------------------------------------

    payload = {
        "model": OPENROUTER_MODEL,

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],

        # Creativity controlled
        "temperature": 0.7,

        # Output ko unnecessarily bada hone se rokta hai
        "max_tokens": 450,

        # Model ko extra unnecessary output se rokne ke liye
        "stream": False
    }


    # -----------------------------------------------------
    # REQUEST
    # -----------------------------------------------------

    try:

        timeout = httpx.Timeout(
            connect=5.0,
            read=25.0,
            write=10.0,
            pool=5.0
        )

        async with httpx.AsyncClient(
            timeout=timeout,
            http2=True
        ) as client:

            response = await client.post(
                OPENROUTER_URL,
                headers=get_headers(),
                json=payload
            )


        # -------------------------------------------------
        # HTTP ERROR
        # -------------------------------------------------

        if response.status_code != 200:

            try:
                error_data = response.json()
            except Exception:
                error_data = response.text

            print(
                "OPENROUTER ERROR:",
                response.status_code,
                error_data
            )

            return {
                "report": (
                    "Baba ka AI connection thoda slow ho gaya 😅 "
                    "Thodi der baad dobara try karo."
                ),
                "error": error_data
            }


        # -------------------------------------------------
        # RESPONSE JSON
        # -------------------------------------------------

        result = response.json()

        print(
            "OPENROUTER MODEL:",
            result.get("model", OPENROUTER_MODEL)
        )


        # -------------------------------------------------
        # SAFETY CHECK
        # -------------------------------------------------

        if "choices" not in result:

            print("INVALID OPENROUTER RESPONSE:", result)

            return {
                "report": (
                    "Baba keh rahe hain... "
                    "gyaan ka flow ruk gaya 😅"
                )
            }


        # -------------------------------------------------
        # EXTRACT REPORT
        # -------------------------------------------------

        report = (
            result["choices"][0]
            .get("message", {})
            .get("content", "")
        )


        if not report:

            return {
                "report": (
                    "Baba ki tapasya complete nahi hui 😅 "
                    "Dobara try karo."
                )
            }


        return {
            "report": report,
            "model": result.get(
                "model",
                OPENROUTER_MODEL
            )
        }


    # -----------------------------------------------------
    # TIMEOUT
    # -----------------------------------------------------

    except httpx.TimeoutException:

        print("OPENROUTER TIMEOUT")

        return {
            "report": (
                "Baba ka connection dhyaan me chala gaya 😅 "
                "Dobara try karo."
            )
        }


    # -----------------------------------------------------
    # CONNECTION ERROR
    # -----------------------------------------------------

    except httpx.RequestError as e:

        print(
            "OPENROUTER REQUEST ERROR:",
            str(e)
        )

        return {
            "report": (
                "Baba server se connection nahi bana paaye 😅"
            )
        }


    # -----------------------------------------------------
    # UNKNOWN ERROR
    # -----------------------------------------------------

    except Exception as e:

        print(
            "UNKNOWN ERROR:",
            str(e)
        )

        return {
            "report": (
                "Baba tapasya me disturb ho gaye 😅"
            )
        }


# =========================================================
# 🚀 STREAMING VERSION
# =========================================================
#
# Is endpoint ka biggest benefit:
#
# Normal:
# Request → wait → complete report
#
# Streaming:
# Request → response ke tokens immediately frontend ko
#
# Isliye user ko waiting kam feel hogi.
#
# =========================================================

@app.post("/generate-report-stream")
async def generate_report_stream(data: ProfileData):

    if not OPENROUTER_API_KEY:

        async def key_error():

            yield "Baba ki API key missing hai 😅"

        return StreamingResponse(
            key_error(),
            media_type="text/plain"
        )


    # -----------------------------------------------------
    # CLEAN INPUT
    # -----------------------------------------------------

    clean_data = ProfileData(
        username=data.username.strip()[:100],
        name=data.name.strip()[:100],
        bio=data.bio.strip()[:500]
    )


    prompt = build_prompt(clean_data)


    # -----------------------------------------------------
    # STREAM PAYLOAD
    # -----------------------------------------------------

    payload = {
        "model": OPENROUTER_MODEL,

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],

        "temperature": 0.7,

        "max_tokens": 450,

        # ⭐ IMPORTANT
        "stream": True
    }


    # -----------------------------------------------------
    # STREAM GENERATOR
    # -----------------------------------------------------

    async def generate():

        timeout = httpx.Timeout(
            connect=5.0,
            read=40.0,
            write=10.0,
            pool=5.0
        )

        try:

            async with httpx.AsyncClient(
                timeout=timeout,
                http2=True
            ) as client:

                async with client.stream(
                    "POST",
                    OPENROUTER_URL,
                    headers=get_headers(),
                    json=payload
                ) as response:


                    # -------------------------------------
                    # ERROR
                    # -------------------------------------

                    if response.status_code != 200:

                        error_text = await response.aread()

                        print(
                            "STREAM ERROR:",
                            response.status_code,
                            error_text
                        )

                        yield (
                            "Baba server ne thoda dhyaan "
                            "laga liya 😅"
                        )

                        return


                    # -------------------------------------
                    # READ STREAM
                    # -------------------------------------

                    async for line in response.aiter_lines():

                        if not line:
                            continue


                        # OpenRouter SSE format:
                        #
                        # data: {...}
                        #

                        if not line.startswith("data:"):
                            continue


                        raw_data = line[
                            len("data:"):
                        ].strip()


                        # Stream finished
                        if raw_data == "[DONE]":
                            break


                        try:

                            chunk = json.loads(
                                raw_data
                            )

                        except json.JSONDecodeError:

                            continue


                        # ---------------------------------
                        # GET TOKEN
                        # ---------------------------------

                        choices = chunk.get(
                            "choices",
                            []
                        )

                        if not choices:
                            continue


                        delta = choices[0].get(
                            "delta",
                            {}
                        )

                        content = delta.get(
                            "content"
                        )


                        if content:

                            yield content


        except httpx.TimeoutException:

            print(
                "STREAM TIMEOUT"
            )

            yield (
                "\n\nBaba ka connection slow ho gaya 😅"
            )


        except httpx.RequestError as e:

            print(
                "STREAM REQUEST ERROR:",
                str(e)
            )

            yield (
                "\n\nBaba server se connection toot gaya 😅"
            )


        except Exception as e:

            print(
                "STREAM UNKNOWN ERROR:",
                str(e)
            )

            yield (
                "\n\nBaba ki tapasya interrupt ho gayi 😅"
            )


    # -----------------------------------------------------
    # RETURN STREAM
    # -----------------------------------------------------

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",

        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
async def root():

    return {
        "status": "online",
        "service": "AI Baba",
        "model": OPENROUTER_MODEL
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "model": OPENROUTER_MODEL,
        "api_key_configured": bool(
            OPENROUTER_API_KEY
        )
    }
