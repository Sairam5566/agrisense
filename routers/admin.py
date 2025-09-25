"""
Admin-specific routes and functionality
"""

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Admin, Farmer, Customer, ContactUs

router = APIRouter()

@router.get("/farmers")
async def get_all_farmers(db: Session = Depends(get_db)):
    """Get all registered farmers"""
    farmers = db.query(Farmer).all()
    return {
        "farmers": [
            {
                "id": farmer.farmer_id,
                "name": farmer.farmer_name,
                "email": farmer.email,
                "phone": farmer.phone_no,
                "state": farmer.state,
                "district": farmer.district
            } for farmer in farmers
        ]
    }

@router.get("/customers")
async def get_all_customers(db: Session = Depends(get_db)):
    """Get all registered customers"""
    customers = db.query(Customer).all()
    return {
        "customers": [
            {
                "id": customer.cust_id,
                "name": customer.cust_name,
                "email": customer.email,
                "phone": customer.phone_no,
                "city": customer.city,
                "state": customer.state
            } for customer in customers
        ]
    }

@router.get("/contact-messages")
async def get_contact_messages(db: Session = Depends(get_db)):
    """Get all contact form messages"""
    messages = db.query(ContactUs).all()
    return {
        "messages": [
            {
                "id": msg.c_id,
                "name": msg.c_name,
                "email": msg.c_email,
                "mobile": msg.c_mobile,
                "address": msg.c_address,
                "message": msg.c_message,
                "created_at": msg.created_at
            } for msg in messages
        ]
    }
