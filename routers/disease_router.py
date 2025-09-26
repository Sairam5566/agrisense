import os
import shutil
import json
import uuid
import re
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import traceback
from PIL import Image, UnidentifiedImageError
# Optional: enable HEIC/HEIF support if library is present
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except Exception:
    pass
import google.generativeai as genai

# Convert to APIRouter so it plugs into main.py
router = APIRouter()

# Gemini API configuration (use environment variable)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Ensure there is a folder to save uploaded images
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@router.get("/status")
async def disease_status():
    """Quick status check for Gemini configuration."""
    return {
        "gemini_configured": bool(GEMINI_API_KEY),
        "model_type": "Gemini-2.5-Flash (Image Analysis)"
    }

@router.get("/diseases")
async def get_all_diseases():
    """Get disease information"""
    return JSONResponse(content={
        "total_diseases": 1,
        "diseases": {"detected_plant_disease": {"name": "Detected Plant Disease", "description": "", "causes": "", "protection": ""}}
    })

@router.get("/diseases/{disease_key}")
async def get_disease(disease_key: str):
    """Get disease information"""
    disease_info = {"name": disease_key.replace('_', ' ').title(), "description": "", "causes": "", "protection": ""}
    return JSONResponse(content=disease_info)

@router.get("/diseases/list")
async def get_disease_list():
    """Get a simple list of disease names and keys"""
    disease_list = [{
        "key": "detected_plant_disease",
        "name": "Detected Plant Disease",
        "type": "disease"
    }]
    return JSONResponse(content={
        "total_diseases": len(disease_list),
        "diseases": disease_list
    })

@router.post("/predict")
async def predict(image: UploadFile = File(...)):
    if not image.filename:
        return JSONResponse(content={"error": "No image selected"}, status_code=400)

    try:
        unique_filename = f"{uuid.uuid4().hex}_{image.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Validate the saved image and normalize to JPEG to avoid malformed base64 issues
        try:
            with Image.open(file_path) as im:
                im = im.convert('RGB')
                im.save(file_path, format='JPEG', quality=95)
        except UnidentifiedImageError:
            return JSONResponse(content={"error": "Uploaded file is not a valid image. Please upload an image (PNG/JPG/WEBP/HEIC)."}, status_code=400)
        except Exception as img_err:
            return JSONResponse(content={"error": f"Failed to process image: {img_err}"}, status_code=400)

        # Extra guard: ensure file size > 0 after processing
        try:
            if os.path.getsize(file_path) <= 0:
                return JSONResponse(content={"error": "Uploaded image appears to be empty."}, status_code=400)
        except Exception:
            pass

        try:
            # Use Gemini for complete disease prediction and analysis
            pil_image = Image.open(file_path)
        except Exception as img_load_err:
            return JSONResponse(content={"error": f"Failed to load image for analysis: {img_load_err}"}, status_code=500)
        
        # Get prediction from Gemini with image
        result = {"predictions": [], "disease_details": {}}
        
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = '''Look at this plant photo. Tell me what plant it is (like rice, tomato, potato). Check if the plant has any disease or pest problems. If the plant looks healthy with no disease signs, say "Healthy Plant". If you see disease signs, name the disease. Give confidence as just a number 0-100 (like "85" not "85%").

                FOR HEALTHY PLANTS (use this format exactly):
                <plant>Rice</plant>
                <disease>Healthy Plant</disease>
                <confidence>85</confidence>
                <desc>* Plant looks strong and green. Leaves look fresh.
                * No yellow or brown spots. Plant stands straight.</desc>
                <causes>* Getting enough water. Soil has good food.
                * Plant gets sunlight and fresh air. No pests now.</causes>
                <protect>* Step 1: Water at the base only. Do not wet leaves.
                * Step 2: Remove weeds and check leaves daily.
                * Step 3: Keep good spacing for air. Clean fallen leaves.
                * Step 4: Spray neem 5 ml in 1 L water every 14 days.</protect>
                <fert>* Step 1: Add cow dung compost 2 kg per square meter. Mix into soil monthly.
                * Step 2: Add vermicompost 500 g per plant. Apply around roots monthly.
                * Step 3: If crop needs, use NPK 10-10-10 one spoon. Mix with 1 L water every 15 days.
                * Step 4: Do not use chemicals when plant is healthy. Small compost tea can be used weekly.</fert>

                FOR DISEASED PLANTS (use this format exactly):
                <plant>Rice</plant>
                <disease>Leaf Spot</disease>
                <confidence>85</confidence>
                <desc>* Black spots on leaves. Yellow color starts.
                * Spots spread to other leaves. Growth becomes slow.</desc>
                <causes>* Fungus likes wet leaves. Water stays on leaf.
                * Hot and wet weather helps it spread fast.</causes>
                <protect>* Step 1: Water at the base only. Do not wet leaves.
                * Step 2: Pick fallen and sick leaves. Burn or bury them.
                * Step 3: Give space for air. Keep 20–30 cm gap between plants.
                * Step 4: Spray neem oil 5 ml in 1 L water every 7 days.</protect>
                <fert>* Step 1: Use Urea 50 g per plant. Mix in 2 L water and apply at 30 days.
                * Step 2: Use NPK 10-10-10 1 spoon per plant. Mix with 1 L water every 15 days.
                * Step 3: Add cow dung compost 2 kg per square meter. Mix in soil monthly.
                * Step 4: Add vermicompost 500 g per plant. Apply around roots every month.</fert>

                IMPORTANT: Give EXACTLY 2 bullet points for <desc> and <causes>. Give EXACTLY 4 bullet points for <protect> and <fert> with STEP-BY-STEP actions, exact names, amounts, and timing. Each bullet must be 2 short sentences. Use very simple words. Short sentences. No big words. Like talking to a village farmer. Do not mention that you are AI or suggest consulting experts.'''
                
                response = model.generate_content([prompt, pil_image])
                print(f"Gemini raw response: {response.text}")  # Debug logging

                # Parse the formatted response
                try:
                    # Try strict closed tags first, then fall back to open-tag sequences
                    plant_match = re.search(r'<plant>(.*?)</plant>', response.text, re.DOTALL) or \
                                   re.search(r'<plant>(.*?)<disease>', response.text, re.DOTALL)
                    disease_match = re.search(r'<disease>(.*?)</disease>', response.text, re.DOTALL) or \
                                     re.search(r'<disease>(.*?)<confidence>', response.text, re.DOTALL)
                    confidence_match = re.search(r'<confidence>(.*?)</confidence>', response.text, re.DOTALL) or \
                                       re.search(r'<confidence>(.*?)<desc>', response.text, re.DOTALL)
                    description_match = re.search(r'<desc>(.*?)<causes>', response.text, re.DOTALL)
                    causes_match = re.search(r'<causes>(.*?)<protect>', response.text, re.DOTALL)
                    protection_match = re.search(r'<protect>(.*?)<fert>', response.text, re.DOTALL)
                    tips_match = re.search(r'<fert>(.*)', response.text, re.DOTALL)

                    plant_name = plant_match.group(1).strip() if plant_match else "Unknown Plant"
                    disease_name = disease_match.group(1).strip() if disease_match else "Detected Plant Disease"

                    # Fallbacks if tags are missing or not filled by the model
                    if (not plant_match) or (not plant_name) or (plant_name.lower() == "unknown plant"):
                        alt_plant = re.search(r'(?i)\bplant\s*[:\-]\s*([A-Za-z][A-Za-z0-9 \-()]*)', response.text)
                        if alt_plant:
                            plant_name = alt_plant.group(1).strip()

                    if (not disease_match) or (not disease_name) or (disease_name.lower() in ("", "detected plant disease")):
                        alt_dis = re.search(r'(?i)\bdisease\s*[:\-]\s*([A-Za-z0-9 \-()]+)', response.text)
                        if alt_dis and alt_dis.group(1).strip():
                            disease_name = alt_dis.group(1).strip()
                        else:
                            alt_status = re.search(r'(?i)\bstatus\s*[:\-]\s*([A-Za-z0-9 \-()]+)', response.text)
                            if alt_status and alt_status.group(1).strip():
                                disease_name = alt_status.group(1).strip()
                    
                    # Extract confidence percentage more robustly
                    confidence_text = confidence_match.group(1).strip() if confidence_match else "N/A"
                    # Look for any number in the confidence text
                    confidence_num = re.search(r'(\d+)', confidence_text)
                    confidence = confidence_num.group(1) if confidence_num else "N/A"
                    
                    # Convert to float safely
                    try:
                        confidence_val = float(confidence) / 100 if confidence != "N/A" else 0.0
                    except (ValueError, TypeError):
                        confidence_val = 0.0
                    
                    description = description_match.group(1).strip() if description_match else ""
                    causes = causes_match.group(1).strip() if causes_match else ""
                    natural_protection = protection_match.group(1).strip() if protection_match else ""
                    fertilizer_tips = tips_match.group(1).strip() if tips_match else ""

                    # Keep only first N bullet lines for each section (in case the model returns more)
                    def first_n_lines(text: str, n: int) -> str:
                        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
                        return "\n".join(lines[:n])

                    description = first_n_lines(description, 2)
                    causes = first_n_lines(causes, 2)
                    natural_protection = first_n_lines(natural_protection, 4)
                    fertilizer_tips = first_n_lines(fertilizer_tips, 4)

                    # Combine protection and tips
                    protection_combined = f"**Natural Solutions:**\n{natural_protection}\n\n**Fertilizer Solutions:**\n{fertilizer_tips}"

                except Exception as parse_err:
                    print(f"Parsing error: {parse_err}")
                    # Fallback values - assume healthy with exactly 2 bullets for desc/causes
                    # and 4 bullets for protection/fertilizer
                    plant_name = "Unknown Plant"
                    disease_name = "Healthy Plant"
                    confidence_val = 0.5
                    description = "• Plant looks strong and green. Leaves look fresh.\n• No yellow or brown spots. Plant stands straight."
                    causes = "• Getting enough water. Soil has good food.\n• Plant gets sunlight and fresh air. No pests now."
                    natural_protection = (
                        "• Step 1: Water at the base only. Do not wet leaves.\n"
                        "• Step 2: Remove weeds and check leaves daily.\n"
                        "• Step 3: Keep good spacing for air. Clean fallen leaves.\n"
                        "• Step 4: Spray neem 5 ml/L water every 2 weeks."
                    )
                    fertilizer_tips = (
                        "• Step 1: Add cow dung compost 2 kg/m². Mix into soil monthly.\n"
                        "• Step 2: Add vermicompost 500 g per plant. Apply around roots monthly.\n"
                        "• Step 3: For rice/tomato, use NPK 10-10-10 one spoon. Mix with 1 L water every 15 days.\n"
                        "• Step 4: If needed, use DAP 20 g per plant at flowering. Do not overuse."
                    )
                    protection_combined = f"**Natural Solutions:**\n{natural_protection}\n\n**Fertilizer Solutions:**\n{fertilizer_tips}"

                result['predictions'] = [{
                    "class": disease_name,
                    "confidence": confidence_val
                }]
                result['plant_name'] = plant_name
                result['disease_name'] = disease_name
                result['confidence'] = confidence_val
                result['status'] = 'healthy' if 'healthy' in disease_name.lower() else 'diseased'
                
                # For healthy plants, provide different content
                if 'healthy' in disease_name.lower():
                    result['disease_details'] = {
                        "name": "Healthy Plant",
                        "description": "• Plant looks strong and green. Leaves look fresh.\n• No yellow or brown spots. Plant stands straight.",
                        "causes": "• Getting enough water. Soil has good food.\n• Plant gets sunlight and fresh air. No pests now.",
                        "protection": (
                            "**Natural Solutions:**\n"
                            "• Step 1: Water at the base only. Do not wet leaves.\n"
                            "• Step 2: Remove weeds and check leaves daily.\n"
                            "• Step 3: Keep good spacing for air. Clean fallen leaves.\n"
                            "• Step 4: Spray neem 5 ml/L water every 2 weeks.\n\n"
                            "**Fertilizer Solutions:**\n"
                            "• Step 1: Add cow dung compost 2 kg/m². Mix into soil monthly.\n"
                            "• Step 2: Add vermicompost 500 g per plant. Apply around roots monthly.\n"
                            "• Step 3: For rice/tomato, use NPK 10-10-10 one spoon. Mix with 1 L water every 15 days.\n"
                            "• Step 4: If needed, use DAP 20 g per plant at flowering. Do not overuse."
                        )
                    }
                else:
                    result['disease_details'] = {
                        "name": disease_name,
                        "description": description,
                        "causes": causes,
                        "protection": protection_combined.strip()
                    }
            except Exception as e:
                print(f"Gemini API error: {e}")
                error_msg = str(e)
                
                # Handle quota exceeded error
                if "429" in error_msg or "quota" in error_msg.lower():
                    return JSONResponse(content={
                        "error": "Daily limit reached. Please try again tomorrow or upgrade your Gemini API plan.",
                        "details": "You've used all 50 free requests for today. Free tier resets daily.",
                        "solution": "Consider upgrading to Gemini API paid plan for unlimited requests."
                    }, status_code=429)
                
                return JSONResponse(content={"error": f"Gemini analysis failed: {e}"}, status_code=500)
        else:
            return JSONResponse(content={"error": "Gemini API key not configured"}, status_code=500)
        
        result['image_url'] = f"/uploads/{unique_filename}"
        
        return JSONResponse(content=result)
    except Exception as e:
        tb = traceback.format_exc(limit=2)
        return JSONResponse(content={"error": str(e), "trace": tb}, status_code=500)
