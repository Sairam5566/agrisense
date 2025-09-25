import os
from typing import List, Optional
import requests
from fastapi import APIRouter, HTTPException
from fastapi import Body

router = APIRouter(prefix="/api/translate", tags=["Translation (Google API)"])

GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY") or os.getenv("TRANSLATE_API_KEY")

# Map UI language codes to Google Translate codes
LANG_MAP = {
    "en": "en",
    "hi": "hi",
    # Fallback mappings for languages not directly supported by our UI
    "nagpuri": "hi",
    "santali": "hi",  # 'sat' is not universally available; fallback to Hindi
}

TRANSLATE_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"

@router.post("/batch")
async def translate_batch(
    payload: dict = Body(..., example={"texts": ["Hello world"], "target": "hi", "source": "en"})
):
    """
    Translate an array of texts using Google Cloud Translation (v2 REST).
    Expects JSON: { texts: [..], target: 'hi', source?: 'en' }
    Returns: { translations: [..] }
    """
    if not GOOGLE_TRANSLATE_API_KEY:
        raise HTTPException(status_code=500, detail="GOOGLE_TRANSLATE_API_KEY is not configured in .env")

    texts: List[str] = payload.get("texts", [])
    target: str = payload.get("target", "hi")
    source: Optional[str] = payload.get("source")

    if not texts:
        return {"translations": []}

    # Normalize lang codes
    target = LANG_MAP.get(target, target)
    if source:
        source = LANG_MAP.get(source, source)

    # Build form-encoded data with multiple q parameters
    form_data = [("q", t) for t in texts]
    form_data.append(("target", target))
    if source:
        form_data.append(("source", source))

    params = {"key": GOOGLE_TRANSLATE_API_KEY}

    try:
        resp = requests.post(TRANSLATE_ENDPOINT, params=params, data=form_data, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        translations = [item["translatedText"] for item in data.get("data", {}).get("translations", [])]
        # Ensure the output length matches input length; if not, pad with originals
        if len(translations) != len(texts):
            # Fallback: return originals for any missing entries
            out = []
            for i in range(len(texts)):
                out.append(translations[i] if i < len(translations) else texts[i])
            translations = out
        return {"translations": translations}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Translation API request failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected translation error: {e}")
