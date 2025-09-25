"""
Database models for Agriculture Portal
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from database import Base

class Admin(Base):
    __tablename__ = "admin"
    
    admin_id = Column(Integer, primary_key=True, index=True)
    admin_name = Column(String(100), nullable=False)
    admin_password = Column(String(100), nullable=False)

class Customer(Base):
    __tablename__ = "custlogin"
    
    cust_id = Column(Integer, primary_key=True, index=True)
    cust_name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    address = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    pincode = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    phone_no = Column(String(255), nullable=False)
    otp = Column(Integer, default=0)

class Farmer(Base):
    __tablename__ = "farmers"
    
    farmer_id = Column(Integer, primary_key=True, index=True)
    farmer_name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    # Email optional for farmers now; keep a placeholder if needed
    email = Column(String(255), nullable=True)
    # Mobile (phone_no) is the primary login identifier
    phone_no = Column(String(255), nullable=False, unique=True)
    gender = Column(String(10), nullable=True)
    dob = Column(String(20), nullable=True)
    state = Column(String(255), nullable=True)
    district = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    otp = Column(Integer, default=0)

class Crop(Base):
    __tablename__ = "crops"
    
    crop_id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(255), nullable=False)
    n_value = Column(Float, nullable=False)
    p_value = Column(Float, nullable=False)
    k_value = Column(Float, nullable=False)

class State(Base):
    __tablename__ = "state"
    
    st_code = Column(Integer, primary_key=True, index=True)
    state_name = Column(String(200), nullable=False)

class District(Base):
    __tablename__ = "district"
    
    dist_code = Column(Integer, primary_key=True, index=True)
    st_code = Column(Integer, nullable=False)
    district_name = Column(String(200), nullable=False)

class ContactUs(Base):
    __tablename__ = "contactus"
    
    c_id = Column(Integer, primary_key=True, index=True)
    c_name = Column(String(100), nullable=False)
    c_mobile = Column(String(100), nullable=False)
    c_email = Column(String(100), nullable=False)
    c_address = Column(String(500), nullable=False)
    c_message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Cart(Base):
    __tablename__ = "cart"
    
    id = Column(Integer, primary_key=True, index=True)
    cropname = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    customer_id = Column(Integer, nullable=True)


# New tables to support farmer postings and buyer requirements
class FarmerListing(Base):
    __tablename__ = "farmer_listings"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, nullable=False)
    crop_name = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="kg")
    price_per_unit = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class BuyerRequirement(Base):
    __tablename__ = "buyer_requirements"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, nullable=True)
    contact_name = Column(String(100), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(120), nullable=True)
    requirement = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_satisfied = Column(Boolean, default=False)
    satisfied_by_farmer_id = Column(Integer, nullable=True)


class FarmerProposal(Base):
    __tablename__ = "farmer_proposals"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, nullable=False)
    buyer_requirement_id = Column(Integer, nullable=False)
    proposed_quantity = Column(Float, nullable=False)
    proposed_price_per_unit = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="kg")
    status = Column(String(20), nullable=False, default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
