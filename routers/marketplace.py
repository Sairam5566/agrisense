"""
Marketplace endpoints for farmer listings and buyer requirements
"""
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import FarmerListing, BuyerRequirement, FarmerProposal
from sqlalchemy import and_, or_

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


@router.post("/proposals")
async def create_proposal(
    farmer_id: int = Form(...),
    buyer_requirement_id: int = Form(...),
    proposed_quantity: float = Form(...),
    proposed_price_per_unit: float = Form(...),
    unit: str = Form("kg"),
    db: Session = Depends(get_db),
):
    # Check if requirement already satisfied
    requirement = db.query(BuyerRequirement).filter(BuyerRequirement.id == buyer_requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    if requirement.is_satisfied:
        raise HTTPException(status_code=400, detail="Requirement already satisfied")
    
    # Create proposal
    proposal = FarmerProposal(
        farmer_id=farmer_id,
        buyer_requirement_id=buyer_requirement_id,
        proposed_quantity=proposed_quantity,
        proposed_price_per_unit=proposed_price_per_unit,
        unit=unit,
        status="pending"
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return {"message": "Proposal created", "id": proposal.id}


@router.get("/proposals/requirement/{requirement_id}")
async def list_proposals_for_requirement(requirement_id: int, db: Session = Depends(get_db)):
    rows = db.query(FarmerProposal).filter(FarmerProposal.buyer_requirement_id == requirement_id).all()
    return {
        "count": len(rows),
        "items": [
            {
                "id": r.id,
                "farmer_id": r.farmer_id,
                "buyer_requirement_id": r.buyer_requirement_id,
                "proposed_quantity": r.proposed_quantity,
                "proposed_price_per_unit": r.proposed_price_per_unit,
                "unit": r.unit,
                "status": r.status,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            for r in rows
        ],
    }


@router.post("/proposals/{proposal_id}/accept")
async def accept_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.query(FarmerProposal).filter(FarmerProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Check if the requirement is already satisfied
    requirement = db.query(BuyerRequirement).filter(BuyerRequirement.id == proposal.buyer_requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    if requirement.is_satisfied:
        raise HTTPException(status_code=400, detail="Requirement already satisfied by another farmer")
    
    # Accept the proposal
    proposal.status = "accepted"
    requirement.is_satisfied = True
    requirement.satisfied_by_farmer_id = proposal.farmer_id
    
    db.commit()
    db.refresh(proposal)
    db.refresh(requirement)
    
    return {"message": "Proposal accepted", "proposal": proposal_id}


@router.post("/proposals/{proposal_id}/reject")
async def reject_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.query(FarmerProposal).filter(FarmerProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Reject the proposal
    proposal.status = "rejected"
    db.commit()
    db.refresh(proposal)
    
    return {"message": "Proposal rejected", "proposal": proposal_id}


@router.get("/proposals/farmer/{farmer_id}")
async def list_proposals_by_farmer(farmer_id: int, db: Session = Depends(get_db)):
    # Join with BuyerRequirement to get requirement text
    rows = db.query(FarmerProposal, BuyerRequirement.requirement.label("requirement_text")).join(BuyerRequirement, FarmerProposal.buyer_requirement_id == BuyerRequirement.id).filter(FarmerProposal.farmer_id == farmer_id).all()
    
    items = []
    for row in rows:
        proposal = row[0]  # FarmerProposal object
        requirement_text = row[1]  # requirement text from BuyerRequirement
        
        items.append({
            "id": proposal.id,
            "farmer_id": proposal.farmer_id,
            "buyer_requirement_id": proposal.buyer_requirement_id,
            "requirement_text": requirement_text,
            "proposed_quantity": proposal.proposed_quantity,
            "proposed_price_per_unit": proposal.proposed_price_per_unit,
            "unit": proposal.unit,
            "status": proposal.status,
            "created_at": proposal.created_at,
            "updated_at": proposal.updated_at,
        })
    
    return {
        "count": len(items),
        "items": items,
    }


@router.get("/proposals/farmer/{farmer_id}/requirement/{requirement_id}")
async def check_farmer_proposal_for_requirement(farmer_id: int, requirement_id: int, db: Session = Depends(get_db)):
    proposal = db.query(FarmerProposal).filter(
        and_(FarmerProposal.farmer_id == farmer_id, 
             FarmerProposal.buyer_requirement_id == requirement_id)
    ).first()
    
    if proposal:
        return {
            "has_proposed": True,
            "proposal_id": proposal.id,
            "status": proposal.status
        }
    else:
        return {
            "has_proposed": False
        }
