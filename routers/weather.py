import os
import requests
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="")
templates = Jinja2Templates(directory="templates")

AGROMONITORING_API_KEY = os.getenv("AGROMONITORING_API_KEY")

@router.get("/weather", response_class=HTMLResponse)
async def get_weather_page(request: Request):
    return templates.TemplateResponse("weather.html", {"request": request, "weather_data": None})

@router.post("/weather", response_class=HTMLResponse)
async def get_weather_data(request: Request, lat: float = Form(...), lon: float = Form(...)):
    weather_url = f"http://api.agromonitoring.com/agro/1.0/weather?lat={lat}&lon={lon}&appid={AGROMONITORING_API_KEY}"
    
    try:
        response = requests.get(weather_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        weather_data = response.json()
    except requests.exceptions.RequestException as e:
        weather_data = {"error": f"Could not retrieve weather data: {e}"}
    
    return templates.TemplateResponse("weather.html", {"request": request, "weather_data": weather_data})


@router.get("/api/weather/forecast")
async def get_weather_forecast(lat: float, lon: float):
    """Proxy AgroMonitoring forecast endpoint using server-side API key.
    Returns raw JSON list as provided by the API.
    """
    if not AGROMONITORING_API_KEY:
        return JSONResponse(status_code=500, content={"error": "AGROMONITORING_API_KEY is not configured on the server."})

    url = (
        f"https://api.agromonitoring.com/agro/1.0/weather/forecast?lat={lat}&lon={lon}&appid={AGROMONITORING_API_KEY}&units=metric"
    )
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        return JSONResponse(status_code=200, content=resp.json())
    except requests.exceptions.RequestException as e:
        return JSONResponse(status_code=502, content={"error": f"Failed to fetch forecast: {e}"})
