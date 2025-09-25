import os
from typing import List, Optional
import requests
from fastapi import APIRouter, HTTPException
from fastapi import Body

router = APIRouter(prefix="/api/translate", tags=["Translation (Google API)"])

GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY") or os.getenv("TRANSLATE_API_KEY")

# Map UI language codes to Google Translate codes for all 22 official Indian languages
LANG_MAP = {
    # English
    "en": "en",
    "english": "en",
    
    # All 22 Official Indian Languages with Google Translate API codes
    "as": "as",      # Assamese
    "assamese": "as",
    
    "bn": "bn",      # Bengali
    "bengali": "bn",
    
    "brx": "hi",     # Bodo (not directly supported, fallback to Hindi)
    "bodo": "hi",
    
    "doi": "doi",    # Dogri
    "dogri": "doi",
    
    "gu": "gu",      # Gujarati
    "gujarati": "gu",
    
    "hi": "hi",      # Hindi
    "hindi": "hi",
    
    "kn": "kn",      # Kannada
    "kannada": "kn",
    
    "ks": "hi",      # Kashmiri (limited support, fallback to Hindi)
    "kashmiri": "hi",
    
    "gom": "gom",    # Konkani
    "konkani": "gom",
    
    "mai": "mai",    # Maithili
    "maithili": "mai",
    
    "ml": "ml",      # Malayalam
    "malayalam": "ml",
    
    "mni-Mtei": "mni-Mtei",  # Manipuri (Meitei script)
    "manipuri": "mni-Mtei",
    "meitei": "mni-Mtei",
    
    "mr": "mr",      # Marathi
    "marathi": "mr",
    
    "ne": "ne",      # Nepali
    "nepali": "ne",
    
    "or": "or",      # Odia (Oriya)
    "odia": "or",
    "oriya": "or",
    
    "pa": "pa",      # Punjabi
    "punjabi": "pa",
    
    "sa": "sa",      # Sanskrit
    "sanskrit": "sa",
    
    "sat": "hi",     # Santali (limited support, fallback to Hindi)
    "santali": "hi",
    
    "sd": "sd",      # Sindhi
    "sindhi": "sd",
    
    "ta": "ta",      # Tamil
    "tamil": "ta",
    
    "te": "te",      # Telugu
    "telugu": "te",
    
    "ur": "ur",      # Urdu
    "urdu": "ur",
    
    # Legacy mappings for backward compatibility
    "nagpuri": "hi",  # Regional dialect, fallback to Hindi
}

TRANSLATE_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"

# Language display names for UI
LANGUAGE_NAMES = {
    "en": "English",
    "as": "অসমীয়া (Assamese)",
    "bn": "বাংলা (Bengali)", 
    "brx": "बर' (Bodo)",
    "doi": "डोगरी (Dogri)",
    "gu": "ગુજરાતી (Gujarati)",
    "hi": "हिंदी (Hindi)",
    "kn": "ಕನ್ನಡ (Kannada)",
    "ks": "कॉशुर (Kashmiri)",
    "gom": "कोंकणी (Konkani)",
    "mai": "मैथिली (Maithili)",
    "ml": "മലയാളം (Malayalam)",
    "mni-Mtei": "মেইতেই (Manipuri)",
    "mr": "मराठी (Marathi)",
    "ne": "नेपाली (Nepali)",
    "or": "ଓଡ଼ିଆ (Odia)",
    "pa": "ਪੰਜਾਬੀ (Punjabi)",
    "sa": "संस्कृतम् (Sanskrit)",
    "sat": "ᱥᱟᱱᱛᱟᱲᱤ (Santali)",
    "sd": "سنڌي (Sindhi)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)",
    "ur": "اردو (Urdu)"
}

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

@router.get("/languages")
async def get_supported_languages():
    """
    Get list of all supported languages with their display names.
    Returns: { languages: [{ code: 'hi', name: 'हिंदी (Hindi)', native_name: 'हिंदी' }, ...] }
    """
    languages = []
    
    # Get unique language codes from LANG_MAP (excluding aliases)
    primary_codes = set()
    for key, value in LANG_MAP.items():
        if len(key) <= 3 and key == value:  # Primary language codes
            primary_codes.add(key)
    
    # Add languages with display names
    for code in sorted(primary_codes):
        if code in LANGUAGE_NAMES:
            languages.append({
                "code": code,
                "name": LANGUAGE_NAMES[code],
                "google_code": LANG_MAP.get(code, code)
            })
    
    return {"languages": languages}

@router.get("/detect")
async def detect_language(text: str):
    """
    Detect the language of given text using Google Translate API.
    """
    if not GOOGLE_TRANSLATE_API_KEY:
        raise HTTPException(status_code=500, detail="GOOGLE_TRANSLATE_API_KEY is not configured")
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    detect_endpoint = "https://translation.googleapis.com/language/translate/v2/detect"
    params = {"key": GOOGLE_TRANSLATE_API_KEY}
    data = {"q": text}
    
    try:
        resp = requests.post(detect_endpoint, params=params, data=data, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        
        detections = result.get("data", {}).get("detections", [[]])[0]
        if detections:
            detected = detections[0]
            language_code = detected.get("language", "unknown")
            confidence = detected.get("confidence", 0.0)
            
            # Map back to our language codes if possible
            display_name = LANGUAGE_NAMES.get(language_code, f"Unknown ({language_code})")
            
            return {
                "detected_language": language_code,
                "confidence": confidence,
                "display_name": display_name
            }
        else:
            return {
                "detected_language": "unknown",
                "confidence": 0.0,
                "display_name": "Unknown"
            }
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Language detection failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected detection error: {e}")
