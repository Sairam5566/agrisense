"""
Authentication router for farmers, customers, and admin
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import secrets

from database import get_db
from sqlalchemy.exc import IntegrityError
from models import Farmer, Customer, Admin
from pydantic import BaseModel

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = secrets.token_urlsafe(32)  # Generate random secret for zero-cost deployment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    phone_no: str
    state: str
    district: str
    address: str
    gender: str = None
    dob: str = None

class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/farmer/register")
async def register_farmer(
    name: str = Form(...),
    phone_no: str = Form(...),
    password: str = Form(...),
    email: str | None = Form(None),
    db: Session = Depends(get_db)
):
    """Register a new farmer with minimal fields: name, phone_no, password (email optional)."""
    # Check if phone already exists
    existing_phone = db.query(Farmer).filter(Farmer.phone_no == phone_no).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Mobile already registered")

    # Normalize/derive email for legacy DBs that may enforce NOT NULL + UNIQUE on email.
    # If email not provided, synthesize a unique placeholder using phone number.
    norm_email = (email or "").strip() or f"{phone_no}@local"

    # Optional: also prevent duplicate email when provided (and not empty)
    existing_email = db.query(Farmer).filter(Farmer.email == norm_email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        hashed_password = get_password_hash(password)
        # Provide safe defaults for legacy databases where these columns may be NOT NULL
        farmer = Farmer(
            farmer_name=name,
            phone_no=phone_no,
            email=norm_email,
            password=hashed_password,
            gender="",
            dob="",
            state="",
            district="",
            address="",
        )

        db.add(farmer)
        db.commit()
        db.refresh(farmer)
    except IntegrityError as ie:
        db.rollback()
        # Most common: UNIQUE constraint failed or NOT NULL constraint failed
        raise HTTPException(status_code=400, detail=str(ie.orig))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

    return {"message": "Farmer registered successfully", "farmer_id": farmer.farmer_id}

@router.post("/customer/register")
async def register_customer(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone_no: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    pincode: str = Form(...),
    state: str = Form(...),
    db: Session = Depends(get_db)
):
    """Register a new customer"""
    # Check if customer already exists
    existing_customer = db.query(Customer).filter(Customer.email == email).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new customer
    hashed_password = get_password_hash(password)
    customer = Customer(
        cust_name=name,
        email=email,
        password=hashed_password,
        phone_no=phone_no,
        address=address,
        city=city,
        pincode=pincode,
        state=state
    )
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return {"message": "Customer registered successfully", "customer_id": customer.cust_id}

@router.post("/login")
async def login(
    email: str | None = Form(None),
    password: str = Form(...),
    user_type: str = Form(...),  # farmer, customer, admin
    phone_no: str | None = Form(None),
    db: Session = Depends(get_db)
):
    """Login for farmers, customers, and admin"""
    user = None
    
    if user_type == "farmer":
        # Allow login by phone_no (preferred) or email fallback
        if phone_no:
            user = db.query(Farmer).filter(Farmer.phone_no == phone_no).first()
        elif email:
            user = db.query(Farmer).filter(Farmer.email == email).first()
        else:
            raise HTTPException(status_code=400, detail="Provide mobile (phone_no) or email for farmer login")
        if user and verify_password(password, user.password):
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.phone_no or user.email or str(user.farmer_id), "type": "farmer", "id": user.farmer_id},
                expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer", "user_type": "farmer", "user_id": user.farmer_id}
    
    elif user_type == "customer":
        user = db.query(Customer).filter(Customer.email == email).first()
        if user and verify_password(password, user.password):
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.email, "type": "customer", "id": user.cust_id},
                expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer", "user_type": "customer", "user_id": user.cust_id}
    
    elif user_type == "admin":
        user = db.query(Admin).filter(Admin.admin_name == email).first()
        if user and user.admin_password == password:  # Simple password check for admin
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.admin_name, "type": "admin", "id": user.admin_id},
                expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer", "user_type": "admin", "user_id": user.admin_id}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
