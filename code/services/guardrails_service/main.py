from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Guardrails Service")


class TextInput(BaseModel):
    text: str


REAL_ESTATE_KEYWORDS = [
    "apartment", "house", "villa", "office", "retail", "industrial",
    "property", "listing", "bedroom", "bathroom", "parking",
    "balcony", "kitchen", "garden", "location", "price",
    "renovated", "room", "rooms"
]

SPAM_WORDS = [
    "click here", "earn money", "crypto", "casino",
    "bonus", "free money", "limited offer", "buy now"
]

OFFENSIVE_WORDS = [
    "hate", "scam", "stupid"
]

UNSAFE_OUTPUT_CLAIMS = [
    "guaranteed profit",
    "guaranteed increase",
    "officially certified",
    "legal guarantee",
    "risk-free investment",
    "guaranteed return",
    "100% profit"
]


@app.get("/")
def root():
    return {
        "message": "Guardrails Service is running",
        "checks": [
            "spam detection",
            "off-topic detection",
            "minimum length validation",
            "real estate keyword validation",
            "unsafe output claim detection"
        ]
    }


@app.post("/check/input")
def check_input(data: TextInput):
    text = data.text.lower().strip()

    if len(text) < 20:
        return {
            "pass": False,
            "reason": "Input is too short to be a valid property listing.",
            "safe_text": ""
        }

    if any(word in text for word in spam_words_lower()):
        return {
            "pass": False,
            "reason": "Input looks like spam or promotional content.",
            "safe_text": ""
        }

    if any(word in text for word in offensive_words_lower()):
        return {
            "pass": False,
            "reason": "Input contains offensive or inappropriate content.",
            "safe_text": ""
        }

    has_real_estate_context = any(
        keyword in text for keyword in real_estate_keywords_lower()
    )

    if not has_real_estate_context:
        return {
            "pass": False,
            "reason": "Input does not appear to describe a real estate listing.",
            "safe_text": ""
        }

    return {
        "pass": True,
        "reason": "Valid real estate listing input.",
        "safe_text": data.text
    }


@app.post("/check/output")
def check_output(data: TextInput):
    text = data.text.lower().strip()

    if any(claim in text for claim in unsafe_output_claims_lower()):
        return {
            "pass": False,
            "reason": "Output contains risky legal, certification, or profit guarantee claims.",
            "safe_text": ""
        }

    if len(text) < 10:
        return {
            "pass": False,
            "reason": "Output is too short to be useful.",
            "safe_text": ""
        }

    return {
        "pass": True,
        "reason": "Safe output.",
        "safe_text": data.text
    }


def spam_words_lower():
    return [word.lower() for word in SPAM_WORDS]


def offensive_words_lower():
    return [word.lower() for word in OFFENSIVE_WORDS]


def real_estate_keywords_lower():
    return [word.lower() for word in REAL_ESTATE_KEYWORDS]


def unsafe_output_claims_lower():
    return [claim.lower() for claim in UNSAFE_OUTPUT_CLAIMS]