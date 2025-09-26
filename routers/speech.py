"""
Speech-to-Text and Text-to-Speech functionality for farmers
"""

from fastapi import APIRouter, Form, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import speech_recognition as sr
import io
import wave
import os
from googletrans import Translator

router = APIRouter()

# Initialize speech recognition and text-to-speech
recognizer = sr.Recognizer()

# Initialize TTS only if not in production environment
tts_engine = None
try:
    # Only initialize pyttsx3 if we're not in a server environment
    if os.getenv("RENDER") != "true" and os.getenv("RAILWAY_ENVIRONMENT") != "production":
        import pyttsx3
        tts_engine = pyttsx3.init()
except (ImportError, RuntimeError) as e:
    print(f"TTS not available in this environment: {e}")
    tts_engine = None

translator = Translator()

# Language codes for agriculture portal
SUPPORTED_LANGUAGES = {
    'english': 'en',
    'hindi': 'hi',
    'nagpuri': 'hi',  # Using Hindi as base for Nagpuri
    'santali': 'hi'   # Using Hindi as base for Santali
}

@router.post("/speech-to-text")
async def speech_to_text(
    audio_file: UploadFile = File(...),
    language: str = Form(default="english")
):
    """
    Convert speech to text for farmers
    Supports multiple languages for agricultural communities
    """
    try:
        # Get language code
        lang_code = SUPPORTED_LANGUAGES.get(language.lower(), 'en')
        
        # Read audio file
        audio_data = await audio_file.read()
        
        # Convert audio to text using speech recognition
        with sr.AudioFile(io.BytesIO(audio_data)) as source:
            audio = recognizer.record(source)
            
        # Recognize speech
        try:
            text = recognizer.recognize_google(audio, language=lang_code)
            
            # If not English, translate to English for processing
            if lang_code != 'en':
                translated = translator.translate(text, src=lang_code, dest='en')
                english_text = translated.text
            else:
                english_text = text
            
            return {
                "success": True,
                "original_text": text,
                "english_text": english_text,
                "language": language,
                "message": "Speech converted to text successfully"
            }
            
        except sr.UnknownValueError:
            return {
                "success": False,
                "error": "Could not understand the audio. Please speak clearly.",
                "message": "Speech recognition failed"
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "error": f"Speech recognition service error: {str(e)}",
                "message": "Service temporarily unavailable"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@router.post("/text-to-speech")
async def text_to_speech(
    text: str = Form(...),
    language: str = Form(default="english"),
    speed: int = Form(default=150)
):
    """
    Convert text to speech for farmers
    Useful for illiterate farmers or field announcements
    """
    try:
        # Get language code
        lang_code = SUPPORTED_LANGUAGES.get(language.lower(), 'en')
        
        # Translate text if needed
        if lang_code != 'en' and language.lower() != 'english':
            translated = translator.translate(text, src='en', dest=lang_code)
            speech_text = translated.text
        else:
            speech_text = text
        
        # Configure TTS engine if available
        if tts_engine:
            tts_engine.setProperty('rate', speed)
            # For zero-cost implementation, we'll return the text that would be spoken
            # In a full implementation, you would generate actual audio file
            note = "Audio generation requires additional setup. Text is ready for local TTS."
        else:
            note = "TTS engine not available in production environment. Text prepared for client-side synthesis."
        
        return {
            "success": True,
            "text": speech_text,
            "language": language,
            "speed": speed,
            "message": "Text prepared for speech synthesis",
            "note": note
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported languages for speech features"""
    return {
        "languages": [
            {"code": "english", "name": "English", "native": "English"},
            {"code": "hindi", "name": "Hindi", "native": "हिंदी"},
            {"code": "nagpuri", "name": "Nagpuri", "native": "नागपुरी"},
            {"code": "santali", "name": "Santali", "native": "संताली"}
        ],
        "message": "Languages supported for agricultural communities"
    }

@router.post("/translate-agricultural-terms")
async def translate_agricultural_terms(
    text: str = Form(...),
    from_language: str = Form(...),
    to_language: str = Form(...)
):
    """
    Translate agricultural terms between supported languages
    Specialized for farming terminology
    """
    try:
        from_code = SUPPORTED_LANGUAGES.get(from_language.lower(), 'en')
        to_code = SUPPORTED_LANGUAGES.get(to_language.lower(), 'en')
        
        # Common agricultural terms dictionary for better accuracy
        agricultural_terms = {
            'crop': {'hi': 'फसल', 'en': 'crop'},
            'fertilizer': {'hi': 'उर्वरक', 'en': 'fertilizer'},
            'irrigation': {'hi': 'सिंचाई', 'en': 'irrigation'},
            'harvest': {'hi': 'फसल काटना', 'en': 'harvest'},
            'soil': {'hi': 'मिट्टी', 'en': 'soil'},
            'seed': {'hi': 'बीज', 'en': 'seed'},
            'weather': {'hi': 'मौसम', 'en': 'weather'},
            'rainfall': {'hi': 'बारिश', 'en': 'rainfall'}
        }
        
        # Check if it's a common agricultural term
        text_lower = text.lower().strip()
        if text_lower in agricultural_terms and to_code in agricultural_terms[text_lower]:
            translated_text = agricultural_terms[text_lower][to_code]
        else:
            # Use Google Translate for other terms
            translated = translator.translate(text, src=from_code, dest=to_code)
            translated_text = translated.text
        
        return {
            "success": True,
            "original_text": text,
            "translated_text": translated_text,
            "from_language": from_language,
            "to_language": to_language,
            "message": "Agricultural term translated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")
