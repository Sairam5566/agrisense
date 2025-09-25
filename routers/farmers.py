"""
Farmer-specific routes and functionality
"""

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Farmer, Crop

router = APIRouter()

@router.get("/profile/{farmer_id}")
async def get_farmer_profile(farmer_id: int, db: Session = Depends(get_db)):
    """Get farmer profile information"""
    farmer = db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    return {
        "farmer_id": farmer.farmer_id,
        "name": farmer.farmer_name,
        "email": farmer.email,
        "phone": farmer.phone_no,
        "state": farmer.state,
        "district": farmer.district,
        "address": farmer.address
    }

@router.get("/crops")
async def get_all_crops(db: Session = Depends(get_db)):
    """Get all available crops"""
    crops = db.query(Crop).all()
    return {"crops": [{"id": crop.crop_id, "name": crop.crop_name, "n": crop.n_value, "p": crop.p_value, "k": crop.k_value} for crop in crops]}
