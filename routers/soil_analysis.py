import io
import math
from typing import Dict

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image, ImageStat

router = APIRouter(prefix="/api/soil", tags=["Soil Analysis"])

# Simple heuristic classifier based on average color features
# This is NOT a scientific model—replace with a trained model when available.


def _rgb_to_hsv(r: float, g: float, b: float):
    r_, g_, b_ = r / 255.0, g / 255.0, b / 255.0
    mx = max(r_, g_, b_)
    mn = min(r_, g_, b_)
    df = mx - mn
    if df == 0:
        h = 0
    elif mx == r_:
        h = (60 * ((g_ - b_) / df) + 360) % 360
    elif mx == g_:
        h = (60 * ((b_ - r_) / df) + 120) % 360
    else:
        h = (60 * ((r_ - g_) / df) + 240) % 360
    s = 0 if mx == 0 else df / mx
    v = mx
    return h, s, v


def _classify(avg_rgb, std_rgb) -> Dict[str, str]:
    r, g, b = avg_rgb
    sr, sg, sb = std_rgb
    h, s, v = _rgb_to_hsv(r, g, b)
    V = v * 255.0  # brightness 0-255
    S = s * 100.0  # saturation %

    # Helper distance -> score
    def gauss(x, mu, sigma):
        # Gaussian-like score in [0,1]
        return math.exp(-((x - mu) ** 2) / (2 * (sigma ** 2)))

    def clamp01(x):
        return max(0.0, min(1.0, x))

    # Feature deltas
    neutral_diff = math.sqrt((r - g) ** 2 + (g - b) ** 2 + (r - b) ** 2) / 3.0
    avg_std = (sr + sg + sb) / 3.0

    scores = {}

    # Black soil: very low V, low saturation, very neutral color, moderate-low texture
    s_brightness = clamp01(gauss(V, 40, 25))
    s_saturation = clamp01(gauss(S, 20, 15))
    s_neutral = clamp01(gauss(neutral_diff, 5, 8))
    s_texture = clamp01(gauss(avg_std, 20, 15))
    scores["Black Soil"] = 0.35 * s_brightness + 0.25 * s_saturation + 0.25 * s_neutral + 0.15 * s_texture

    # Red soil: R >> G,B, medium brightness and moderate saturation
    rg = (r - g)
    rb = (r - b)
    s_redness = clamp01(gauss(rg, 35, 18) * gauss(rb, 45, 20))
    s_brightness = clamp01(gauss(V, 140, 40))
    s_saturation = clamp01(gauss(S, 35, 20))
    scores["Red Soil"] = 0.45 * s_redness + 0.3 * s_brightness + 0.25 * s_saturation

    # Laterite: reddish-brown, higher saturation, medium brightness
    s_red_bias = clamp01(gauss(r - max(g, b), 25, 15))
    s_brightness = clamp01(gauss(V, 130, 45))
    s_saturation = clamp01(gauss(S, 45, 18))
    scores["Laterite Soil"] = 0.4 * s_red_bias + 0.3 * s_saturation + 0.3 * s_brightness

    # Sandy: high brightness, low saturation, near yellow (R and G high, B lower)
    s_brightness = clamp01(gauss(V, 210, 30))
    s_saturation = clamp01(gauss(S, 12, 10))
    yellow_bias = ((r + g) / 2.0) - b
    s_yellow = clamp01(gauss(yellow_bias, 30, 20))
    scores["Sandy Soil"] = 0.4 * s_brightness + 0.35 * s_saturation + 0.25 * s_yellow

    # Clayey: lower brightness than sandy but not black, low saturation, neutral hue, higher texture (std)
    s_brightness = clamp01(gauss(V, 110, 25))
    s_saturation = clamp01(gauss(S, 18, 12))
    s_neutral = clamp01(gauss(neutral_diff, 10, 10))
    s_texture = clamp01(gauss(avg_std, 28, 12))
    scores["Clayey Soil"] = 0.3 * s_brightness + 0.25 * s_saturation + 0.2 * s_neutral + 0.25 * s_texture

    # Alluvial/Loam: balanced features, mid brightness, mid saturation, neutral color
    s_brightness = clamp01(gauss(V, 150, 35))
    s_saturation = clamp01(gauss(S, 28, 15))
    s_neutral = clamp01(gauss(neutral_diff, 12, 12))
    scores["Alluvial/Loam"] = 0.33 * s_brightness + 0.34 * s_saturation + 0.33 * s_neutral

    # Pick best and compute normalized confidence
    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]
    total = sum(scores.values()) or 1.0
    confidence = best_score / total

    notes_map = {
        "Black Soil": "Dark appearance with low brightness indicates black cotton soil (regur).",
        "Red Soil": "Reddish tint suggests iron oxide rich red soil.",
        "Laterite Soil": "Reddish-brown tone with higher saturation resembles laterite soil.",
        "Sandy Soil": "Bright and low-saturation appearance indicates sandy/desert soil.",
        "Clayey Soil": "Moderately dark, low-saturation tone suggests clayey soil.",
        "Alluvial/Loam": "Neutral brown/grey appearance typical of alluvial/loam soils.",
    }

    fert_map = {
        "Black Soil": [
            "Add well-decomposed FYM/compost 5–10 t/ha",
            "Split N applications (urea) to reduce losses",
            "Balanced NPK like 17-17-17 or as per crop need",
        ],
        "Red Soil": [
            "Incorporate FYM/green manure",
            "Start with NPK 20-10-10 at basal; supplement N as topdress",
            "Add phosphorus (DAP/SSP) as per soil test",
        ],
        "Laterite Soil": [
            "Apply lime/dolomite if pH is acidic (as per soil test)",
            "NPK 17-17-17 or crop-specific recommendation",
            "Organic matter 5–8 t/ha",
        ],
        "Sandy Soil": [
            "Heavy organic additions (FYM/compost) 10–15 t/ha",
            "Slow-release N sources; apply in multiple splits",
            "Use mulch to reduce evaporation",
        ],
        "Clayey Soil": [
            "Organic matter to improve structure",
            "Balanced NPK 10-10-10; avoid over-irrigation",
        ],
        "Alluvial/Loam": [
            "Basal: 12-32-16 or 10-26-26 depending on crop",
            "Topdress with urea based on crop stage",
            "Add FYM/compost 5 t/ha annually",
        ],
    }

    advice_map = {
        "Black Soil": [
            "Ensure good drainage; black soils can crack and waterlog",
            "Micronutrients (Zn, B) if deficient after soil test",
        ],
        "Red Soil": [
            "Generally low in N and P — regular organic additions help",
            "Mulch to conserve moisture",
        ],
        "Laterite Soil": [
            "Split fertilizer doses due to leaching risk",
            "Maintain mulch/cover to reduce erosion",
        ],
        "Sandy Soil": [
            "Frequent light irrigations due to low water holding",
            "Add biofertilizers (Azotobacter, PSB)",
        ],
        "Clayey Soil": [
            "Ensure drainage to prevent waterlogging",
            "Gypsum may help with sodicity issues (test-based)",
        ],
        "Alluvial/Loam": [
            "Follow crop-specific recommendations after soil test",
            "Maintain residue mulch for moisture conservation",
        ],
    }

    return {
        "soil_type": best_type,
        "confidence": round(confidence, 2),
        "notes": notes_map[best_type],
        "fertilizer": fert_map[best_type],
        "advice": advice_map[best_type],
    }


@router.post("/analyze")
async def analyze_soil_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file")
    try:
        data = await file.read()
        img = Image.open(io.BytesIO(data)).convert("RGB")
        # Resize to speed up stats and reduce noise
        img = img.resize((256, 256))
        stat = ImageStat.Stat(img)
        r, g, b = stat.mean  # average RGB
        sr, sg, sb = stat.stddev  # channel stddevs for texture-like cue
        result = _classify((r, g, b), (sr, sg, sb))
        return JSONResponse({
            "soil_type": result["soil_type"],
            "confidence": result["confidence"],
            "notes": result["notes"],
            "fertilizer": result["fertilizer"],
            "advice": result["advice"],
            "avg_rgb": [round(r, 1), round(g, 1), round(b, 1)],
            "std_rgb": [round(sr, 1), round(sg, 1), round(sb, 1)],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process image: {e}")
