"""
Multi-language support for agriculture portal
"""

from fastapi import APIRouter, Form, HTTPException
from googletrans import Translator

router = APIRouter()
translator = Translator()

# Language codes mapping
LANGUAGE_CODES = {
    'english': 'en',
    'hindi': 'hi',
    'nagpuri': 'hi',  # Using Hindi as base for Nagpuri
    'santali': 'hi'   # Using Hindi as base for Santali
}

@router.post("/translate")
async def translate_text(
    text: str = Form(...),
    target_language: str = Form(...),
    source_language: str = Form(default="english")
):
    """
    Translate text between supported languages
    """
    try:
        # Get language codes
        source_code = LANGUAGE_CODES.get(source_language.lower(), 'en')
        target_code = LANGUAGE_CODES.get(target_language.lower(), 'hi')
        
        # Translate text
        translated = translator.translate(text, src=source_code, dest=target_code)
        
        return {
            "success": True,
            "original_text": text,
            "translated_text": translated.text,
            "source_language": source_language,
            "target_language": target_language,
            "message": "Text translated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

# Common agricultural terms dictionary for better accuracy
AGRICULTURAL_TERMS = {
    'en': {
        'crop': 'Crop',
        'fertilizer': 'Fertilizer',
        'irrigation': 'Irrigation',
        'harvest': 'Harvest',
        'soil': 'Soil',
        'seed': 'Seed',
        'weather': 'Weather',
        'rainfall': 'Rainfall',
        'yield': 'Yield',
        'pest': 'Pest',
        'disease': 'Disease',
        'market': 'Market',
        'price': 'Price',
        'government': 'Government',
        'scheme': 'Scheme',
        'support': 'Support',
        'helpline': 'Helpline'
    },
    'hi': {
        'crop': 'फसल',
        'fertilizer': 'उर्वरक',
        'irrigation': 'सिंचाई',
        'harvest': 'कटाई',
        'soil': 'मिट्टी',
        'seed': 'बीज',
        'weather': 'मौसम',
        'rainfall': 'वर्षा',
        'yield': 'उपज',
        'pest': 'कीट',
        'disease': 'रोग',
        'market': 'बाजार',
        'price': 'मूल्य',
        'government': 'सरकार',
        'scheme': 'योजना',
        'support': 'सहायता',
        'helpline': 'हेल्पलाइन'
    }
}

@router.post("/translate-agricultural-term")
async def translate_agricultural_term(
    term: str = Form(...),
    target_language: str = Form(...),
    source_language: str = Form(default="english")
):
    """
    Translate common agricultural terms with higher accuracy
    """
    try:
        # Convert to lowercase for matching
        term_lower = term.lower().strip()
        
        # Check if it's a common agricultural term
        if (source_language.lower() in ['english', 'hindi'] and 
            target_language.lower() in ['english', 'hindi']):
            
            source_code = 'en' if source_language.lower() == 'english' else 'hi'
            target_code = 'hi' if target_language.lower() == 'hindi' else 'en'
            
            # Check in agricultural terms dictionary
            if (source_code in AGRICULTURAL_TERMS and 
                term_lower in AGRICULTURAL_TERMS[source_code]):
                
                # Find the target translation
                for lang_code, terms in AGRICULTURAL_TERMS.items():
                    if lang_code == target_code:
                        for key, value in terms.items():
                            if (source_code == 'en' and key == term_lower) or \
                               (source_code == 'hi' and value.lower() == term_lower):
                                return {
                                    "success": True,
                                    "original_term": term,
                                    "translated_term": value if target_code == 'hi' else key,
                                    "source_language": source_language,
                                    "target_language": target_language,
                                    "message": "Agricultural term translated with high accuracy"
                                }
        
        # Fallback to Google Translate for other terms
        source_code = LANGUAGE_CODES.get(source_language.lower(), 'en')
        target_code = LANGUAGE_CODES.get(target_language.lower(), 'hi')
        
        translated = translator.translate(term, src=source_code, dest=target_code)
        
        return {
            "success": True,
            "original_term": term,
            "translated_term": translated.text,
            "source_language": source_language,
            "target_language": target_language,
            "message": "Term translated using Google Translate"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")
