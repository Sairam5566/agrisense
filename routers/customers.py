"""
Customer-specific routes and functionality
"""

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Customer, Cart

router = APIRouter()

@router.get("/profile/{customer_id}")
async def get_customer_profile(customer_id: int, db: Session = Depends(get_db)):
    """Get customer profile information"""
    customer = db.query(Customer).filter(Customer.cust_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {
        "customer_id": customer.cust_id,
        "name": customer.cust_name,
        "email": customer.email,
        "phone": customer.phone_no,
        "address": customer.address,
        "city": customer.city,
        "state": customer.state,
        "pincode": customer.pincode
    }

@router.post("/cart/add")
async def add_to_cart(
    customer_id: int = Form(...),
    cropname: str = Form(...),
    quantity: int = Form(...),
    price: int = Form(...),
    db: Session = Depends(get_db)
):
    """Add item to customer cart"""
    cart_item = Cart(
        cropname=cropname,
        quantity=quantity,
        price=price,
        customer_id=customer_id
    )
    
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    
    return {"message": "Item added to cart successfully", "cart_id": cart_item.id}

@router.get("/cart/{customer_id}")
async def get_cart(customer_id: int, db: Session = Depends(get_db)):
    """Get customer cart items"""
    cart_items = db.query(Cart).filter(Cart.customer_id == customer_id).all()
    
    total_price = sum(item.price * item.quantity for item in cart_items)
    
    return {
        "cart_items": [
            {
                "id": item.id,
                "cropname": item.cropname,
                "quantity": item.quantity,
                "price": item.price,
                "total": item.price * item.quantity
            } for item in cart_items
        ],
        "total_price": total_price
    }
