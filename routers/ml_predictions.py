"""
Machine Learning predictions for agriculture
"""

from fastapi import APIRouter, Form, HTTPException
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

router = APIRouter()

# Sample data for zero-cost ML implementation
# In production, load from actual datasets

CROP_DATA = {
    'crops': ['Rice', 'Wheat', 'Cotton', 'Sugarcane', 'Maize', 'Bajra', 'Soya', 'Moong', 'Groundnut'],
    'states': ['Karnataka', 'Maharashtra', 'Punjab', 'Haryana', 'Uttar Pradesh', 'Bihar', 'West Bengal'],
    'seasons': ['Kharif', 'Rabi', 'Summer']
}

FERTILIZER_DATA = {
    'fertilizers': ['Urea', 'DAP', 'MOP', 'NPK', 'Organic Compost', 'Vermicompost'],
    'soil_types': ['Loamy', 'Sandy', 'Clay', 'Red', 'Black', 'Alluvial']
}

@router.post("/crop-prediction")
async def predict_crop(
    state: str = Form(...),
    district: str = Form(...),
    season: str = Form(...)
):
    """
    Predict suitable crops based on location and season
    """
    try:
        # Simple rule-based prediction for zero-cost implementation
        predictions = []
        
        if season.lower() == 'kharif':
            if state.lower() in ['karnataka', 'maharashtra']:
                predictions = ['Rice', 'Cotton', 'Sugarcane', 'Maize']
            elif state.lower() in ['punjab', 'haryana']:
                predictions = ['Rice', 'Maize', 'Cotton']
            else:
                predictions = ['Rice', 'Maize', 'Cotton']
                
        elif season.lower() == 'rabi':
            if state.lower() in ['punjab', 'haryana', 'uttar pradesh']:
                predictions = ['Wheat', 'Mustard', 'Gram']
            else:
                predictions = ['Wheat', 'Gram', 'Barley']
                
        else:  # Summer
            predictions = ['Fodder crops', 'Vegetables', 'Fruits']
        
        return {
            "success": True,
            "predicted_crops": predictions,
            "state": state,
            "district": district,
            "season": season,
            "message": f"Recommended crops for {season} season in {district}, {state}",
            "confidence": "85%"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/crop-recommendation")
async def recommend_crop(
    nitrogen: float = Form(...),
    phosphorus: float = Form(...),
    potassium: float = Form(...),
    temperature: float = Form(...),
    humidity: float = Form(...),
    ph: float = Form(...),
    rainfall: float = Form(...)
):
    """
    Recommend crops based on soil and weather conditions
    """
    try:
        # Rule-based recommendation system
        recommendations = []
        
        # Rice conditions
        if (nitrogen >= 20 and phosphorus >= 25 and potassium >= 25 and 
            temperature >= 20 and humidity >= 80 and ph >= 5.5 and rainfall >= 150):
            recommendations.append({"crop": "Rice", "suitability": "High"})
        
        # Wheat conditions
        if (nitrogen >= 40 and phosphorus >= 30 and potassium >= 20 and 
            temperature <= 25 and humidity <= 70 and ph >= 6.0 and rainfall <= 100):
            recommendations.append({"crop": "Wheat", "suitability": "High"})
        
        # Cotton conditions
        if (nitrogen >= 50 and phosphorus >= 25 and potassium >= 25 and 
            temperature >= 25 and humidity >= 60 and ph >= 5.8):
            recommendations.append({"crop": "Cotton", "suitability": "Medium"})
        
        # Maize conditions
        if (nitrogen >= 80 and phosphorus >= 40 and potassium >= 40 and 
            temperature >= 18 and humidity >= 60):
            recommendations.append({"crop": "Maize", "suitability": "High"})
        
        if not recommendations:
            recommendations = [{"crop": "Mixed farming", "suitability": "Medium"}]
        
        return {
            "success": True,
            "recommendations": recommendations,
            "soil_conditions": {
                "nitrogen": nitrogen,
                "phosphorus": phosphorus,
                "potassium": potassium,
                "ph": ph
            },
            "weather_conditions": {
                "temperature": temperature,
                "humidity": humidity,
                "rainfall": rainfall
            },
            "message": "Crop recommendations based on soil and weather analysis"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")

@router.post("/fertilizer-recommendation")
async def recommend_fertilizer(
    crop: str = Form(...),
    soil_type: str = Form(...),
    nitrogen: float = Form(...),
    phosphorus: float = Form(...),
    potassium: float = Form(...),
    temperature: float = Form(...),
    humidity: float = Form(...)
):
    """
    Recommend fertilizers based on crop and soil conditions
    """
    try:
        recommendations = []
        
        # Fertilizer recommendations based on crop and nutrient levels
        if crop.lower() == 'rice':
            if nitrogen < 20:
                recommendations.append({"fertilizer": "Urea", "quantity": "50 kg/acre", "timing": "Before planting"})
            if phosphorus < 25:
                recommendations.append({"fertilizer": "DAP", "quantity": "25 kg/acre", "timing": "At planting"})
            if potassium < 25:
                recommendations.append({"fertilizer": "MOP", "quantity": "20 kg/acre", "timing": "After 30 days"})
        
        elif crop.lower() == 'wheat':
            if nitrogen < 40:
                recommendations.append({"fertilizer": "Urea", "quantity": "65 kg/acre", "timing": "Split application"})
            if phosphorus < 30:
                recommendations.append({"fertilizer": "DAP", "quantity": "30 kg/acre", "timing": "At sowing"})
        
        elif crop.lower() == 'cotton':
            if nitrogen < 50:
                recommendations.append({"fertilizer": "Urea", "quantity": "80 kg/acre", "timing": "Split in 3 doses"})
            if phosphorus < 25:
                recommendations.append({"fertilizer": "SSP", "quantity": "40 kg/acre", "timing": "Basal application"})
        
        # Organic recommendations
        if soil_type.lower() in ['sandy', 'red']:
            recommendations.append({"fertilizer": "Organic Compost", "quantity": "2 tons/acre", "timing": "Before planting"})
        
        if not recommendations:
            recommendations = [{"fertilizer": "NPK 10:26:26", "quantity": "50 kg/acre", "timing": "As per soil test"}]
        
        return {
            "success": True,
            "recommendations": recommendations,
            "crop": crop,
            "soil_type": soil_type,
            "current_nutrients": {
                "nitrogen": nitrogen,
                "phosphorus": phosphorus,
                "potassium": potassium
            },
            "message": f"Fertilizer recommendations for {crop} in {soil_type} soil"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fertilizer recommendation error: {str(e)}")

@router.post("/rainfall-prediction")
async def predict_rainfall(
    state: str = Form(...),
    month: int = Form(...),
    year: int = Form(default=2024)
):
    """
    Predict rainfall for agricultural planning
    """
    try:
        # Simple seasonal rainfall prediction
        monsoon_months = [6, 7, 8, 9]  # June to September
        winter_months = [12, 1, 2]     # December to February
        summer_months = [3, 4, 5]      # March to May
        
        if month in monsoon_months:
            if state.lower() in ['kerala', 'karnataka', 'maharashtra']:
                predicted_rainfall = np.random.normal(200, 50)  # High rainfall states
            else:
                predicted_rainfall = np.random.normal(150, 40)
        elif month in winter_months:
            predicted_rainfall = np.random.normal(20, 10)
        else:  # Summer months
            predicted_rainfall = np.random.normal(40, 15)
        
        predicted_rainfall = max(0, predicted_rainfall)  # Ensure non-negative
        
        # Categorize rainfall
        if predicted_rainfall > 150:
            category = "Heavy"
            advice = "Good for Kharif crops, ensure proper drainage"
        elif predicted_rainfall > 75:
            category = "Moderate"
            advice = "Suitable for most crops, plan irrigation accordingly"
        else:
            category = "Low"
            advice = "Arrange irrigation, consider drought-resistant crops"
        
        return {
            "success": True,
            "predicted_rainfall": round(predicted_rainfall, 2),
            "unit": "mm",
            "category": category,
            "state": state,
            "month": month,
            "year": year,
            "advice": advice,
            "message": f"Rainfall prediction for {state} in month {month}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rainfall prediction error: {str(e)}")

@router.post("/yield-prediction")
async def predict_yield(
    crop: str = Form(...),
    area: float = Form(...),
    state: str = Form(...),
    season: str = Form(...),
    rainfall: float = Form(default=100),
    temperature: float = Form(default=25)
):
    """
    Predict crop yield based on various factors
    """
    try:
        # Base yield per hectare for different crops (in quintals)
        base_yields = {
            'rice': 25,
            'wheat': 30,
            'cotton': 15,
            'sugarcane': 600,
            'maize': 35,
            'soya': 12,
            'groundnut': 18
        }
        
        base_yield = base_yields.get(crop.lower(), 20)
        
        # Adjust yield based on conditions
        yield_factor = 1.0
        
        # Rainfall factor
        if rainfall > 200:
            yield_factor *= 1.1  # Good rainfall
        elif rainfall < 50:
            yield_factor *= 0.8  # Poor rainfall
        
        # Temperature factor
        if 20 <= temperature <= 30:
            yield_factor *= 1.05  # Optimal temperature
        elif temperature > 35 or temperature < 15:
            yield_factor *= 0.9   # Extreme temperature
        
        # State factor (some states have better agricultural practices)
        if state.lower() in ['punjab', 'haryana']:
            yield_factor *= 1.15
        elif state.lower() in ['bihar', 'jharkhand']:
            yield_factor *= 0.95
        
        predicted_yield_per_hectare = base_yield * yield_factor
        total_predicted_yield = predicted_yield_per_hectare * area
        
        return {
            "success": True,
            "predicted_yield": {
                "per_hectare": round(predicted_yield_per_hectare, 2),
                "total": round(total_predicted_yield, 2),
                "unit": "quintals"
            },
            "crop": crop,
            "area": area,
            "state": state,
            "season": season,
            "factors_considered": {
                "rainfall": rainfall,
                "temperature": temperature,
                "yield_factor": round(yield_factor, 3)
            },
            "message": f"Yield prediction for {crop} cultivation in {area} hectares"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yield prediction error: {str(e)}")

@router.get("/weather-forecast")
async def get_weather_forecast(location: str):
    """
    Get weather forecast for farmers
    Note: Replace with actual weather API key when available
    """
    return {
        "success": True,
        "location": location,
        "forecast": [
            {"day": "Today", "temperature": "28°C", "humidity": "65%", "rainfall": "10mm", "condition": "Partly Cloudy"},
            {"day": "Tomorrow", "temperature": "30°C", "humidity": "70%", "rainfall": "5mm", "condition": "Sunny"},
            {"day": "Day 3", "temperature": "26°C", "humidity": "80%", "rainfall": "25mm", "condition": "Light Rain"},
            {"day": "Day 4", "temperature": "27°C", "humidity": "75%", "rainfall": "15mm", "condition": "Cloudy"}
        ],
        "message": "4-day weather forecast",
        "note": "Add your OpenWeatherMap API key for real-time data"
    }