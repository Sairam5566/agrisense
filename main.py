"""
Agriculture Portal - Python FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, Request, Depends, HTTPException, status, Body
from dotenv import load_dotenv

load_dotenv()
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import uvicorn
import requests
import json
import os

# Market price scraping imports
import sqlite3
import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Optional

from database import engine, get_db
from models import Base
from routers import auth, farmers, customers, admin, ml_predictions, speech, multi_language, chatbot, weather, translate_api, soil_analysis, marketplace, disease

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agriculture Portal",
    description="A comprehensive agriculture portal with ML predictions and e-commerce",
    version="2.0.0"
)

# Mount static files
app.mount("/template", StaticFiles(directory="templates"), name="templates")
# Serve uploaded files (for disease image previews)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(farmers.router, prefix="/api/farmers", tags=["Farmers"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

app.include_router(ml_predictions.router, prefix="/api/ml", tags=["ML Predictions"])
app.include_router(speech.router, prefix="/api/speech", tags=["Speech Features"])
app.include_router(multi_language.router, prefix="/api/translate", tags=["Translation"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["AI Chatbot"])
app.include_router(weather.router, tags=["Weather"])
app.include_router(translate_api.router)
app.include_router(soil_analysis.router)
app.include_router(marketplace.router)
app.include_router(disease, prefix="/api/disease", tags=["Disease"])

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login Page (default landing)"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    """Agriculture Portal Home Page"""
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    """AI Chatbot Standalone Page"""
    return templates.TemplateResponse("chatbot.html", {"request": request})

@app.get("/speech-to-text", response_class=HTMLResponse)
async def speech_to_text_page(request: Request):
    """Speech to Text Page for Farmers"""
    return templates.TemplateResponse("speech_to_text.html", {"request": request})

@app.get("/text-to-speech", response_class=HTMLResponse)
async def text_to_speech_page(request: Request):
    """Text to Speech Page for Farmers"""
    return templates.TemplateResponse("text_to_speech.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Contact Page"""
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/buyer", response_class=HTMLResponse)
async def buyer_page(request: Request):
    """Buyer Portal Page"""
    return templates.TemplateResponse("buyer.html", {"request": request})

@app.get("/farmer", response_class=HTMLResponse)
async def farmer_page(request: Request):
    """Farmer Portal Page"""
    return templates.TemplateResponse("farmer.html", {"request": request})

@app.get("/weather", response_class=HTMLResponse)
async def weather_page(request: Request):
    """Weather Forecast Page"""
    return templates.TemplateResponse("weather.html", {"request": request})

@app.get("/news", response_class=HTMLResponse)
async def news_page(request: Request):
    """Agricultural News Page"""
    newsapi_key = os.getenv("NEWSAPI_KEY")
    if not newsapi_key:
        return templates.TemplateResponse("news.html", {"request": request, "articles": [], "error": "NewsAPI key not configured"})

    try:
        # Fetch agriculture news from India (use top-headlines; everything doesn't support 'country')
        endpoint = "https://newsapi.org/v2/top-headlines"
        params = {
            "q": "agriculture OR farming OR crops",
            "country": "in",
            "pageSize": 12,
            "sortBy": "publishedAt",
            "apiKey": newsapi_key,
        }
        response = requests.get(endpoint, params=params, timeout=6)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])

        # Fallback: if no articles from top-headlines, try 'everything' endpoint (no country filter)
        if not articles:
            alt_endpoint = "https://newsapi.org/v2/everything"
            alt_params = {
                "q": "(agriculture OR farming OR crops) AND (India OR भारतीय OR किसान)",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 12,
                "apiKey": newsapi_key,
            }
            alt_resp = requests.get(alt_endpoint, params=alt_params, timeout=6)
            alt_resp.raise_for_status()
            alt_data = alt_resp.json()
            articles = alt_data.get("articles", [])
        return templates.TemplateResponse("news.html", {"request": request, "articles": articles, "error": None})
    except Exception as e:
        return templates.TemplateResponse("news.html", {"request": request, "articles": [], "error": f"Failed to fetch news: {str(e)}"})

@app.get("/soil-analysis", response_class=HTMLResponse)
async def soil_analysis_page(request: Request):
    """Static page to upload a soil image and see analysis."""
    return templates.TemplateResponse("soil_analysis.html", {"request": request})

@app.get("/market", response_class=HTMLResponse)
async def crop_market_page(request: Request):
    """Serve the new market price SPA"""
    return templates.TemplateResponse("crop_market.html", {"request": request})

@app.get("/disease", response_class=HTMLResponse)
async def disease_page(request: Request):
    """Plant Disease Prediction Page"""
    return templates.TemplateResponse("disease.html", {"request": request})

@app.get("/schemes", response_class=HTMLResponse)
async def schemes_page(request: Request):
    """Government Schemes Page"""
    return templates.TemplateResponse("schemes.html", {"request": request})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = "market_prices.db"

# Supported states (display names) for convenience in frontend
SUPPORTED_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Puducherry",
    "Jammu and Kashmir", "Ladakh"
]

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT,
            unit TEXT,
            local_names TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS markets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT,
            state TEXT NOT NULL,
            market_type TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            commodity_id INTEGER,
            market_id INTEGER,
            price REAL,
            min_price REAL,
            max_price REAL,
            modal_price REAL,
            date TEXT,
            trend_percent REAL,
            FOREIGN KEY (commodity_id) REFERENCES commodities (id),
            FOREIGN KEY (market_id) REFERENCES markets (id)
        )
    """)

    # Alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id TEXT,
            commodity TEXT NOT NULL,
            target_price REAL NOT NULL,
            alert_type TEXT CHECK(alert_type IN ('below','above')) NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT (datetime('now')),
            triggered_at TEXT
        )
    """)

    # Government schemes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS government_schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            eligibility TEXT,
            income_category TEXT,
            application_process TEXT,
            required_documents TEXT,
            benefits TEXT,
            target_beneficiaries TEXT,
            state_applicability TEXT,
            application_link TEXT,
            last_updated TEXT,
            scraped_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


def get_or_create_commodity(commodity_name):
    """Get commodity ID or create new commodity"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if commodity exists
    cursor.execute("SELECT id FROM commodities WHERE name = ?", (commodity_name,))
    result = cursor.fetchone()

    if result:
        commodity_id = result[0]
    else:
        # Create new commodity
        cursor.execute(
            "INSERT INTO commodities (name, category, unit) VALUES (?, ?, ?)",
            (commodity_name, "vegetable", "kg")
        )
        commodity_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return commodity_id


def get_or_create_market(market_name, city, state):
    """Get market ID or create new market"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if market exists
    cursor.execute(
        "SELECT id FROM markets WHERE name = ? AND city = ? AND state = ?",
        (market_name, city, state)
    )
    result = cursor.fetchone()

    if result:
        market_id = result[0]
    else:
        # Create new market
        cursor.execute(
            "INSERT INTO markets (name, city, state, market_type) VALUES (?, ?, ?, ?)",
            (market_name, city, state, "wholesale")
        )
        market_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return market_id


def save_price_data(commodity_name, market_name, city, state, price, min_price, max_price, modal_price):
    """Save price data to database"""
    try:
        # Get or create commodity
        commodity_id = get_or_create_commodity(commodity_name)

        # Get or create market
        market_id = get_or_create_market(market_name, city, state)

        # Save price data
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if price data for today already exists
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT id FROM daily_prices
            WHERE commodity_id = ? AND market_id = ? AND date = ?
        """, (commodity_id, market_id, today))

        result = cursor.fetchone()

        if result:
            # Update existing record
            cursor.execute("""
                UPDATE daily_prices
                SET price = ?, min_price = ?, max_price = ?, modal_price = ?
                WHERE id = ?
            """, (price, min_price, max_price, modal_price, result[0]))
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO daily_prices
                (commodity_id, market_id, price, min_price, max_price, modal_price, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (commodity_id, market_id, price, min_price, max_price, modal_price, today))

        conn.commit()
        conn.close()

        logger.info(f"Saved price data for {commodity_name} in {market_name}, {city}, {state}")
        return True
    except Exception as e:
        logger.error(f"Error saving price data: {e}")
        return False


def _slugify_state(state_name: str) -> str:
    """Convert state display name to vegetablemarketprice.com slug"""
    name = state_name.strip().lower()
    name = re.sub(r"&", " and ", name)
    name = re.sub(r"\s+", "-", name)
    name = re.sub(r"[^a-z\-]", "", name)
    return name


def scrape_state_data(state_name: str) -> List[dict]:
    """Scrape vegetable market prices for given state from vegetablemarketprice.com"""
    state_slug = _slugify_state(state_name)
    url = f"https://vegetablemarketprice.com/market/{state_slug}/today"


def save_scheme_to_db(scheme):
    """Save a scheme to the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if scheme already exists
        cursor.execute("SELECT id FROM government_schemes WHERE name = ?", (scheme['name'],))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing scheme
            cursor.execute("""
                UPDATE government_schemes 
                SET description=?, eligibility=?, income_category=?, application_process=?,
                    required_documents=?, benefits=?, target_beneficiaries=?, state_applicability=?,
                    application_link=?, last_updated=?, scraped_at=datetime('now')
                WHERE name=?
            """, (
                scheme['description'], scheme['eligibility'], ','.join(scheme['income_category']),
                scheme['application_process'], ','.join(scheme['required_documents']), scheme['benefits'],
                scheme['target_beneficiaries'], scheme['state_applicability'], scheme['application_link'],
                scheme['last_updated'], scheme['name']
            ))
        else:
            # Insert new scheme
            cursor.execute("""
                INSERT INTO government_schemes 
                (name, description, eligibility, income_category, application_process, required_documents,
                 benefits, target_beneficiaries, state_applicability, application_link, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scheme['name'], scheme['description'], scheme['eligibility'], ','.join(scheme['income_category']),
                scheme['application_process'], ','.join(scheme['required_documents']), scheme['benefits'],
                scheme['target_beneficiaries'], scheme['state_applicability'], scheme['application_link'],
                scheme['last_updated']
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving scheme to database: {e}")
        return False


def get_schemes_from_db() -> List[dict]:
    """Get schemes from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, eligibility, income_category, application_process,
                   required_documents, benefits, target_beneficiaries, state_applicability,
                   application_link, last_updated
            FROM government_schemes
            ORDER BY scraped_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        schemes = []
        for row in rows:
            schemes.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "eligibility": row[3],
                "income_category": row[4].split(',') if row[4] else [],
                "application_process": row[5],
                "required_documents": row[6].split(',') if row[6] else [],
                "benefits": row[7],
                "target_beneficiaries": row[8],
                "state_applicability": row[9],
                "application_link": row[10],
                "last_updated": row[11]
            })
        
        return schemes
    except Exception as e:
        logger.error(f"Error getting schemes from database: {e}")
        return []


def scrape_government_schemes() -> List[dict]:
    """Scrape government schemes for farmers from multiple sources"""
    schemes = []
    
    # Primary source: myscheme.gov.in
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Scrape from myscheme.gov.in
        try:
            url = "https://www.myscheme.gov.in/search"
            params = {
                'category': 'agriculture',
                'beneficiary': 'farmer'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for scheme cards or listings
                scheme_cards = soup.find_all(['div', 'article'], class_=lambda x: x and ('scheme' in x.lower() or 'card' in x.lower()))
                
                for i, card in enumerate(scheme_cards[:5]):  # Limit to first 5 schemes
                    try:
                        title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'h5'], class_=lambda x: x and ('title' in x.lower() or 'name' in x.lower()))
                        if not title_elem:
                            title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                        
                        desc_elem = card.find(['p', 'div'], class_=lambda x: x and ('desc' in x.lower() or 'summary' in x.lower()))
                        if not desc_elem:
                            desc_elem = card.find('p')
                        
                        if title_elem and desc_elem:
                            schemes.append({
                                "id": len(schemes) + 1,
                                "name": title_elem.get_text().strip()[:100],
                                "description": desc_elem.get_text().strip()[:300],
                                "eligibility": "Farmers as per scheme guidelines",
                                "income_category": ["small", "medium"],
                                "application_process": "Online application through official portal",
                                "required_documents": ["Aadhaar card", "Bank account details", "Land documents"],
                                "benefits": "As per scheme guidelines",
                                "target_beneficiaries": "Farmers",
                                "state_applicability": "All states",
                                "application_link": "https://www.myscheme.gov.in/",
                                "last_updated": datetime.now().strftime('%Y-%m-%d')
                            })
                    except Exception as e:
                        logger.warning(f"Error parsing scheme card: {e}")
                        continue
                        
        except Exception as e:
            logger.warning(f"Error scraping myscheme.gov.in: {e}")
        
        # Try scraping from additional sources
        try:
            # Scrape from agriwelfare.gov.in
            agri_url = "https://agriwelfare.gov.in/"
            agri_response = requests.get(agri_url, headers=headers, timeout=10)
            if agri_response.status_code == 200:
                soup = BeautifulSoup(agri_response.content, 'html.parser')
                
                # Look for scheme links or mentions
                scheme_links = soup.find_all('a', href=lambda x: x and ('scheme' in x.lower() or 'yojana' in x.lower()))
                
                for link in scheme_links[:3]:  # Limit to first 3
                    try:
                        scheme_name = link.get_text().strip()
                        if len(scheme_name) > 10 and len(scheme_name) < 100:
                            schemes.append({
                                "id": len(schemes) + 1,
                                "name": scheme_name,
                                "description": f"Government scheme for agricultural development and farmer welfare. Details available on the official agriculture ministry website.",
                                "eligibility": "Farmers as per scheme guidelines",
                                "income_category": ["small", "medium"],
                                "application_process": "Through state agriculture departments",
                                "required_documents": ["Aadhaar card", "Bank account details", "Land documents"],
                                "benefits": "Financial assistance and support as per scheme",
                                "target_beneficiaries": "Farmers",
                                "state_applicability": "All states",
                                "application_link": "https://agriwelfare.gov.in/",
                                "last_updated": datetime.now().strftime('%Y-%m-%d')
                            })
                    except Exception as e:
                        continue
                        
        except Exception as e:
            logger.warning(f"Error scraping agriwelfare.gov.in: {e}")
        
        # If we still don't have enough schemes, add reliable fallback data
        if len(schemes) < 8:
            fallback_schemes = [
            {
                "id": 1,
                "name": "PM Kisan Samman Nidhi Yojana",
                "description": "Provides financial support to small and marginal farmer families with cultivable land up to 2 hectares. ₹6,000 per year is provided in 3 equal installments directly into the bank accounts of beneficiary farmers.",
                "eligibility": "Farmers with cultivable land up to 2 hectares",
                "income_category": ["small", "medium"],
                "application_process": "Online registration through state government portal",
                "required_documents": ["Aadhaar card", "Bank account details", "Land documents"],
                "benefits": "₹6,000 per year in 3 installments",
                "target_beneficiaries": "Small and marginal farmers",
                "state_applicability": "All states",
                "application_link": "https://pmkisan.gov.in/",
                "last_updated": datetime.now().strftime('%Y-%m-%d')
            },
            {
                "id": 2,
                "name": "Pradhan Mantri Fasal Bima Yojana",
                "description": "Provides insurance coverage and financial support to farmers in the event of crop failure due to natural calamities, pests & diseases. Premium to be paid by farmers is very low with government subsidy.",
                "eligibility": "All farmers including sharecroppers and tenant farmers",
                "income_category": ["small", "medium", "large"],
                "application_process": "Registration through insurance company empanelled by government",
                "required_documents": ["Farmer ID", "Land records", "Bank account details"],
                "benefits": "Comprehensive insurance coverage for crop loss",
                "target_beneficiaries": "All farmers",
                "state_applicability": "All states",
                "application_link": "https://pmfby.gov.in/",
                "last_updated": datetime.now().strftime('%Y-%m-%d')
            },
            {
                "id": 3,
                "name": "Paramparagat Krishi Vikas Yojana",
                "description": "Promotes organic farming through adoption of organic villages by cluster approach and Participatory Guarantee System (PGS) certification. Provides financial assistance for organic farming clusters.",
                "eligibility": "Farmer groups forming clusters of 50 acres",
                "income_category": ["small", "medium"],
                "application_process": "Cluster formation and PGS certification",
                "required_documents": ["Cluster formation documents", "PGS certification"],
                "benefits": "Financial assistance for organic farming",
                "target_beneficiaries": "Organic farming clusters",
                "state_applicability": "All states",
                "application_link": "https://agriwelfare.gov.in/en/Programmes/Paramparagat-Krishi-Vikas-Yojana",
                "last_updated": datetime.now().strftime('%Y-%m-%d')
            },
            {
                "id": 4,
                "name": "Kisan Credit Card Scheme",
                "description": "Provides timely and adequate credit support to farmers through a Kisan Credit Card (KCC) for their cultivation needs. Covers post-harvest expenses, produce marketing loans and consumption requirements.",
                "eligibility": "All farmers irrespective of landholding size",
                "income_category": ["small", "medium", "large"],
                "application_process": "Application through banks",
                "required_documents": ["Aadhaar card", "Bank account details", "Land documents"],
                "benefits": "Credit facility for cultivation and other needs",
                "target_beneficiaries": "All farmers",
                "state_applicability": "All states",
                "application_link": "https://agriwelfare.gov.in/en/Programmes/Kisan-Credit-Card-Scheme",
                "last_updated": datetime.now().strftime('%Y-%m-%d')
            },
            {
                "id": 5,
                "name": "Soil Health Card Scheme",
                "description": "Provides soil health cards to farmers which carry crop-wise recommendations of nutrients and fertilizers required for individual farms to help farmers improve productivity through judicious use of inputs.",
                "eligibility": "All farmers with agricultural land",
                "income_category": ["small", "medium"],
                "application_process": "Application through agriculture department",
                "required_documents": ["Land ownership documents", "Aadhaar card"],
                "benefits": "Free soil testing and nutrient recommendations",
                "target_beneficiaries": "All farmers",
                "state_applicability": "All states",
                "application_link": "https://soilhealth.dac.gov.in/",
                "last_updated": datetime.now().strftime('%Y-%m-%d')
            },
            {
                "id": 6,
                "name": "National Agriculture Market (e-NAM)",
                "description": "A pan-India electronic trading portal which networks the existing APMC mandis to create a unified national market for agricultural commodities.",
                "eligibility": "All farmers and traders",
                "income_category": ["small", "medium", "large"],
                "application_process": "Online registration on e-NAM portal",
                "required_documents": ["Aadhaar card", "Bank account details", "Trade license"],
                "benefits": "Better price discovery and transparent trading",
                "target_beneficiaries": "Farmers and agricultural traders",
                "state_applicability": "All states",
                "application_link": "https://enam.gov.in/",
                "last_updated": datetime.now().strftime('%Y-%m-%d')
            },
            {
                "id": 7,
                "name": "Pradhan Mantri Krishi Sinchai Yojana",
                "description": "Aims to achieve convergence of investments in irrigation at the field level, expand cultivable area under assured irrigation, improve on-farm water use efficiency to reduce wastage of water.",
                "eligibility": "Farmers with agricultural land",
                "income_category": ["small", "medium", "large"],
                "application_process": "Application through state irrigation department",
                "required_documents": ["Land documents", "Water source proof", "Project proposal"],
                "benefits": "Subsidy on irrigation infrastructure",
                "target_beneficiaries": "All farmers",
                "state_applicability": "All states",
                "application_link": "https://pmksy.gov.in/",
                "last_updated": datetime.now().strftime('%Y-%m-%d')
            },
            {
                "id": 8,
                "name": "Sub-Mission on Agricultural Mechanization",
                "description": "Promotes farm mechanization for increasing efficiency and reducing the cost of cultivation. Provides financial assistance for purchase of agricultural machinery and equipment.",
                "eligibility": "Individual farmers, FPOs, and custom hiring centers",
                "income_category": ["medium", "large"],
                "application_process": "Application through agriculture department",
                "required_documents": ["Aadhaar card", "Bank account details", "Land documents"],
                "benefits": "25-50% subsidy on agricultural machinery",
                "target_beneficiaries": "Progressive farmers and FPOs",
                "state_applicability": "All states",
                "application_link": "https://agrimachinery.nic.in/",
                "last_updated": datetime.now().strftime('%Y-%m-%d')
            },
            {
                "id": 9,
                "name": "National Mission for Sustainable Agriculture",
                "description": "Promotes sustainable agriculture practices through climate resilient technologies, soil health management, and efficient use of natural resources.",
                "eligibility": "All categories of farmers",
                "income_category": ["small", "medium"],
                "application_process": "Through state agriculture departments",
                "required_documents": ["Farmer ID", "Land records", "Project proposal"],
                "benefits": "Financial assistance for sustainable farming practices",
                "target_beneficiaries": "Environmentally conscious farmers",
                "state_applicability": "All states",
                "application_link": "https://nmsa.dac.gov.in/",
                "last_updated": datetime.now().strftime('%Y-%m-%d')
            },
            {
                "id": 10,
                "name": "Rashtriya Krishi Vikas Yojana",
                "description": "Provides flexibility and autonomy to states in planning and executing agriculture and allied sector schemes according to their agro-climatic conditions and development priorities.",
                "eligibility": "State governments and farmer groups",
                "income_category": ["small", "medium", "large"],
                "application_process": "State-wise implementation through agriculture departments",
                "required_documents": ["Project proposals", "State government approval"],
                "benefits": "Flexible funding for agriculture development",
                "target_beneficiaries": "All farmers through state programs",
                "state_applicability": "All states",
                "application_link": "https://rkvy.nic.in/",
                "last_updated": datetime.now().strftime('%Y-%m-%d')
            },
            {
                "id": 11,
                "name": "Interest Subvention Scheme",
                "description": "Provides short-term crop loans to farmers at subsidized interest rates. Farmers get loans at 7% interest rate and additional 3% subvention on prompt repayment.",
                "eligibility": "Farmers availing crop loans from banks",
                "income_category": ["small", "medium"],
                "application_process": "Through scheduled commercial banks and cooperative banks",
                "required_documents": ["KCC or loan application", "Land documents", "Aadhaar card"],
                "benefits": "4% interest rate on prompt repayment of crop loans",
                "target_beneficiaries": "Small and marginal farmers",
                "state_applicability": "All states",
                "application_link": "https://www.nabard.org/",
                "last_updated": datetime.now().strftime('%Y-%m-%d')
            },
            {
                "id": 12,
                "name": "Formation and Promotion of FPOs",
                "description": "Supports formation of Farmer Producer Organizations (FPOs) to enable farmers to collectively leverage their produce for better income through economies of scale.",
                "eligibility": "Groups of farmers (minimum 300 for plains, 100 for hills)",
                "income_category": ["small", "medium"],
                "application_process": "Through NABARD and state implementing agencies",
                "required_documents": ["Group formation documents", "Business plan", "Registration papers"],
                "benefits": "Financial support up to ₹18.75 lakh per FPO",
                "target_beneficiaries": "Small and marginal farmers in groups",
                "state_applicability": "All states",
                "application_link": "https://sfac.in/",
                "last_updated": datetime.now().strftime('%Y-%m-%d')
            }
        ]
            
            # Merge fallback schemes with scraped schemes
            for fallback_scheme in fallback_schemes:
                if not any(s['name'] == fallback_scheme['name'] for s in schemes):
                    schemes.append(fallback_scheme)
        
        # Save all schemes to database
        for scheme in schemes:
            save_scheme_to_db(scheme)
        
        logger.info(f"Successfully scraped and saved {len(schemes)} government schemes")
        
        # Return schemes from database (includes both new and existing)
        return get_schemes_from_db()
        
    except Exception as e:
        logger.error(f"Error scraping government schemes: {e}")
        # Return existing schemes from database if scraping fails
        return get_schemes_from_db()


# Initialize database
init_db()

# Scrape government schemes on startup
print("🔄 Scraping government schemes data on startup...")
scrape_government_schemes()
print("✅ Government schemes scraping completed!")

# Scrape data on startup (Jharkhand as seed)
print("🔄 Scraping Jharkhand market data on startup...")
scrape_state_data("Jharkhand")
print("✅ Data scraping completed!")


# Routes
@app.get("/states", response_model=List[str])
def get_supported_states():
    """Get list of supported states for market price data"""
    return SUPPORTED_STATES


@app.get("/scrape/state/{state_name}")
def trigger_state_scrape(state_name: str):
    """Manually trigger data scraping for a specific state"""
    try:
        prices = scrape_state_data(state_name)
        return {"message": f"Scraped {len(prices)} prices for {state_name} successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping error: {str(e)}")


@app.get("/alerts", response_model=List[dict])
def get_price_alerts():
    """Get all active price alerts"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, farmer_id, commodity, target_price, alert_type, status, created_at
            FROM price_alerts
            WHERE status = 'active'
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        alerts = []
        for row in rows:
            alerts.append({
                "id": row[0],
                "farmer_id": row[1],
                "commodity": row[2],
                "target_price": row[3],
                "alert_type": row[4],
                "status": row[5],
                "created_at": row[6]
            })

        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.post("/alerts")
def create_price_alert(
    farmer_id: Optional[str] = Body(None),
    commodity: str = Body(...),
    target_price: float = Body(...),
    alert_type: str = Body(...)
):
    """Create a new price alert"""
    try:
        # Auto-generate farmer_id if not provided
        if not farmer_id:
            farmer_id = f"F{datetime.now().strftime('%Y%m%d%H%M%S')}"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO price_alerts (farmer_id, commodity, target_price, alert_type)
            VALUES (?, ?, ?, ?)
        """, (farmer_id, commodity, target_price, alert_type))

        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {"message": "Alert created successfully", "alert_id": alert_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.delete("/alerts/{alert_id}")
def delete_price_alert(alert_id: int):
    """Delete a price alert by ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE price_alerts
            SET status = 'deleted'
            WHERE id = ?
        """, (alert_id,))

        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Alert not found")

        conn.commit()
        conn.close()

        return {"message": "Alert deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def evaluate_price_alerts(commodity: str, current_price: float):
    """Evaluate active price alerts for a commodity and mark triggered ones"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get active alerts for this commodity
        cursor.execute("""
            SELECT id, farmer_id, target_price, alert_type
            FROM price_alerts
            WHERE commodity = ? AND status = 'active'
        """, (commodity,))

        alerts = cursor.fetchall()

        triggered_alerts = []
        for alert in alerts:
            alert_id, farmer_id, target_price, alert_type = alert

            # Check if alert condition is met
            if (alert_type == 'below' and current_price <= target_price) or \
               (alert_type == 'above' and current_price >= target_price):
                # Mark alert as triggered
                cursor.execute("""
                    UPDATE price_alerts
                    SET status = 'triggered', triggered_at = datetime('now')
                    WHERE id = ?
                """, (alert_id,))

                triggered_alerts.append({
                    "id": alert_id,
                    "farmer_id": farmer_id,
                    "commodity": commodity,
                    "current_price": current_price,
                    "target_price": target_price,
                    "alert_type": alert_type
                })

        conn.commit()
        conn.close()

        # Log triggered alerts
        for alert in triggered_alerts:
            logger.info(f"Alert triggered for Farmer {alert['farmer_id']} - "
                        f"{alert['commodity']} price {alert['alert_type']} "
                        f"target ₹{alert['target_price']}, current ₹{alert['current_price']}")

        return triggered_alerts
    except Exception as e:
        logger.error(f"Error evaluating price alerts: {e}")
        return []


@app.get("/prices/today", response_model=List[dict])
def get_today_prices(state: Optional[str] = None):
    """Get today's market prices for all commodities"""
    try:
        # If a specific state is requested, scrape it to refresh then filter by state
        if state:
            scrape_state_data(state)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT dp.id, c.name, m.name, m.city, m.state, dp.price,
                   dp.min_price, dp.max_price, dp.modal_price, dp.date, dp.trend_percent
            FROM daily_prices dp
            JOIN commodities c ON dp.commodity_id = c.id
            JOIN markets m ON dp.market_id = m.id
            WHERE (? IS NULL OR m.state LIKE ?)
            ORDER BY dp.date DESC, c.name
        """, [state, f"%{state}%"] if state else [None, None])

        rows = cursor.fetchall()
        conn.close()

        prices = []
        for row in rows:
            prices.append({
                "id": row[0],
                "commodity": row[1],
                "market_name": row[2],
                "city": row[3],
                "state": row[4],
                "price": row[5],
                "min_price": row[6],
                "max_price": row[7],
                "modal_price": row[8],
                "date": row[9],
                "trend_percent": row[10]
            })

        return prices
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/prices/today/{commodity}", response_model=List[dict])
def get_today_prices_by_commodity(commodity: str, state: Optional[str] = None):
    """Get today's prices for a specific commodity"""
    try:
        # If a specific state is requested, scrape it to refresh then filter by state
        if state:
            scrape_state_data(state)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT dp.id, c.name, m.name, m.city, m.state, dp.price,
                   dp.min_price, dp.max_price, dp.modal_price, dp.date, dp.trend_percent
            FROM daily_prices dp
            JOIN commodities c ON dp.commodity_id = c.id
            JOIN markets m ON dp.market_id = m.id
            WHERE c.name LIKE ? AND (? IS NULL OR m.state LIKE ?)
            ORDER BY dp.date DESC
        """, (f"%{commodity}%", state, f"%{state}%"))

        rows = cursor.fetchall()
        conn.close()

        prices = []
        for row in rows:
            prices.append({
                "id": row[0],
                "commodity": row[1],
                "market_name": row[2],
                "city": row[3],
                "state": row[4],
                "price": row[5],
                "min_price": row[6],
                "max_price": row[7],
                "modal_price": row[8],
                "date": row[9],
                "trend_percent": row[10]
            })

        return prices
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/prices/state/{state_name}", response_model=List[dict])
def get_state_prices(state_name: str):
    """Get prices for a specific state"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT dp.id, c.name, m.name, m.city, m.state, dp.price,
                   dp.min_price, dp.max_price, dp.modal_price, dp.date, dp.trend_percent
            FROM daily_prices dp
            JOIN commodities c ON dp.commodity_id = c.id
            JOIN markets m ON dp.market_id = m.id
            WHERE m.state LIKE ?
            ORDER BY dp.date DESC, c.name
        """, (f"%{state_name}%",))

        rows = cursor.fetchall()
        conn.close()

        prices = []
        for row in rows:
            prices.append({
                "id": row[0],
                "commodity": row[1],
                "market_name": row[2],
                "city": row[3],
                "state": row[4],
                "price": row[5],
                "min_price": row[6],
                "max_price": row[7],
                "modal_price": row[8],
                "date": row[9],
                "trend_percent": row[10]
            })

        return prices
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/prices/search", response_model=List[dict])
def search_prices(
    commodity: Optional[str] = None,
    state: Optional[str] = None,
    market: Optional[str] = None
):
    """Search prices by commodity, state, and market"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Build query dynamically
        query = """
            SELECT dp.id, c.name, m.name, m.city, m.state, dp.price,
                   dp.min_price, dp.max_price, dp.modal_price, dp.date, dp.trend_percent
            FROM daily_prices dp
            JOIN commodities c ON dp.commodity_id = c.id
            JOIN markets m ON dp.market_id = m.id
            WHERE 1=1
        """
        params = []

        if commodity:
            query += " AND c.name LIKE ?"
            params.append(f"%{commodity}%")

        if state:
            query += " AND m.state LIKE ?"
            params.append(f"%{state}%")

        if market:
            query += " AND m.name LIKE ?"
            params.append(f"%{market}%")

        query += " ORDER BY dp.date DESC, c.name"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        prices = []
        for row in rows:
            prices.append({
                "id": row[0],
                "commodity": row[1],
                "market_name": row[2],
                "city": row[3],
                "state": row[4],
                "price": row[5],
                "min_price": row[6],
                "max_price": row[7],
                "modal_price": row[8],
                "date": row[9],
                "trend_percent": row[10]
            })

        return prices
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/prices/history/{commodity}/{days}", response_model=List[dict])
def get_price_history(commodity: str, days: int):
    """Get historical price data for a commodity"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT dp.date, AVG(dp.price) as avg_price, COUNT(*) as count
            FROM daily_prices dp
            JOIN commodities c ON dp.commodity_id = c.id
            WHERE c.name LIKE ? AND dp.date >= date('now', '-{} days')
            GROUP BY dp.date
            ORDER BY dp.date DESC
        """.format(days), (f"%{commodity}%",))

        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            history.append({
                "date": row[0],
                "avg_price": row[1],
                "count": row[2]
            })

        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# Government Schemes API Endpoints
@app.get("/api/schemes/")
def get_all_schemes(category: Optional[str] = None, state: Optional[str] = None):
    """Get all government schemes with optional filtering by category and state"""
    try:
        schemes = scrape_government_schemes()
        
        # Apply filters if provided
        if category:
            schemes = [scheme for scheme in schemes if category in scheme["income_category"]]
        
        if state:
            schemes = [scheme for scheme in schemes if state.lower() in scheme["state_applicability"].lower() or scheme["state_applicability"] == "All states"]
        
        return schemes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schemes: {str(e)}")


@app.get("/api/schemes/eligible/{income}")
def get_eligible_schemes(income: float):
    """Get government schemes eligible for a farmer based on their income"""
    try:
        schemes = scrape_government_schemes()
        
        # Filter schemes based on income
        if income < 200000:  # Small/Marginal Farmers
            eligible_schemes = [scheme for scheme in schemes if "small" in scheme["income_category"]]
        elif income <= 1000000:  # Medium Farmers
            eligible_schemes = [scheme for scheme in schemes if "medium" in scheme["income_category"]]
        else:  # Large Farmers
            eligible_schemes = [scheme for scheme in schemes if "large" in scheme["income_category"]]
        
        return eligible_schemes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering schemes: {str(e)}")


@app.get("/api/schemes/{scheme_id}")
def get_scheme_details(scheme_id: int):
    """Get details of a specific government scheme by ID"""
    try:
        schemes = scrape_government_schemes()
        
        # Find scheme by ID
        scheme = next((s for s in schemes if s["id"] == scheme_id), None)
        
        if not scheme:
            raise HTTPException(status_code=404, detail="Scheme not found")
        
        return scheme
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scheme details: {str(e)}")


@app.get("/api/schemes/search")
def search_schemes(query: str, category: Optional[str] = None, state: Optional[str] = None):
    """Search government schemes by query term with optional category and state filters"""
    try:
        schemes = scrape_government_schemes()
        
        # Filter by query term in scheme name or description
        filtered_schemes = [
            scheme for scheme in schemes 
            if query.lower() in scheme["name"].lower() or query.lower() in scheme["description"].lower()
        ]
        
        # Apply additional filters if provided
        if category:
            filtered_schemes = [scheme for scheme in filtered_schemes if category in scheme["income_category"]]
        
        if state:
            filtered_schemes = [
                scheme for scheme in filtered_schemes 
                if state.lower() in scheme["state_applicability"].lower() or scheme["state_applicability"] == "All states"
            ]
        
        return filtered_schemes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching schemes: {str(e)}")


@app.post("/api/schemes/refresh")
def refresh_schemes_data():
    """Trigger a refresh of government schemes data"""
    try:
        logger.info("Manual refresh of government schemes triggered")
        schemes = scrape_government_schemes()
        return {
            "message": f"Successfully refreshed {len(schemes)} schemes", 
            "count": len(schemes),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing schemes: {str(e)}")


@app.get("/api/schemes/last-updated")
def get_schemes_last_updated():
    """Get the last updated timestamp for schemes"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT MAX(scraped_at) FROM government_schemes")
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return {"last_updated": result[0]}
        else:
            return {"last_updated": "Never"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting last updated: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
