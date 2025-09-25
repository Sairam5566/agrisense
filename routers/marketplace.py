"""
Marketplace endpoints for farmer listings and buyer requirements
"""
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import FarmerListing, BuyerRequirement

router = APIRouter(prefix="/api/marketplace", tags=["Marketplace"]) 


@router.post("/listings")
async def create_listing(
    farmer_id: int = Form(...),
    crop_name: str = Form(...),
    quantity: float = Form(...),
    unit: str = Form("kg"),
    price_per_unit: float = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    listing = FarmerListing(
        farmer_id=farmer_id,
        crop_name=crop_name,
        quantity=quantity,
        unit=unit,
        price_per_unit=price_per_unit,
        description=description,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return {"message": "Listing created", "id": listing.id}


@router.get("/listings")
async def list_listings(db: Session = Depends(get_db)):
    rows = db.query(FarmerListing).order_by(FarmerListing.created_at.desc()).all()
    return {
        "count": len(rows),
        "items": [
            {
                "id": r.id,
                "farmer_id": r.farmer_id,
                "crop_name": r.crop_name,
                "quantity": r.quantity,
                "unit": r.unit,
                "price_per_unit": r.price_per_unit,
                "description": r.description,
                "created_at": r.created_at,
            }
            for r in rows
        ],
    }


@router.get("/listings/count")
async def listings_count(db: Session = Depends(get_db)):
    cnt = db.query(FarmerListing).count()
    return {"count": cnt}


@router.post("/requirements")
async def create_requirement(
    requirement: str = Form(...),
    buyer_id: Optional[int] = Form(None),
    contact_name: Optional[str] = Form(None),
    contact_phone: Optional[str] = Form(None),
    contact_email: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    req = BuyerRequirement(
        buyer_id=buyer_id,
        contact_name=contact_name,
        contact_phone=contact_phone,
        contact_email=contact_email,
        requirement=requirement,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"message": "Requirement posted", "id": req.id}


@router.get("/requirements")
async def list_requirements(db: Session = Depends(get_db)):
    rows = db.query(BuyerRequirement).order_by(BuyerRequirement.created_at.desc()).all()
    return {
        "count": len(rows),
        "items": [
            {
                "id": r.id,
                "buyer_id": r.buyer_id,
                "contact_name": r.contact_name,
                "contact_phone": r.contact_phone,
                "contact_email": r.contact_email,
                "requirement": r.requirement,
                "created_at": r.created_at,
            }
            for r in rows
        ],
    }
