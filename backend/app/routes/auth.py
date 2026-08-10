# ============================================================
# NexRay AI - Auth Routes
# Handles doctor registration and login.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Doctor
from app.services.auth import hash_password, verify_password, create_token, verify_token

router = APIRouter(
    prefix="/auth",
    tags=["Doctor Authentication"]
)

# HTTPBearer reads the token from the Authorization header
oauth2_scheme = HTTPBearer()

# ── Request Models ──
class RegisterRequest(BaseModel):
    full_name: str       # Doctor's full name
    email: str           # Doctor's email - used to log in
    password: str        # Plain password - will be hashed before storing
    licence_number: str  # Medical licence number

class LoginRequest(BaseModel):
    email: str      # Doctor's email
    password: str   # Doctor's password

# ── Dependency: Get Current Doctor ──
def get_current_doctor(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # --------------------------------------------------------
    # This function is used as a dependency in protected routes
    # It checks the JWT token and returns the logged in doctor
    # If the token is invalid or expired it raises a 401 error
    # --------------------------------------------------------
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    doctor = db.query(Doctor).filter(Doctor.email == payload.get("sub")).first()
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Doctor account not found."
        )
    return doctor

# ── Register Route ──
@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # --------------------------------------------------------
    # Registers a new doctor account.
    # Checks that the email and licence number are not already
    # in use, hashes the password and saves the doctor to the DB.
    # --------------------------------------------------------

    # Check if email is already registered
    existing_email = db.query(Doctor).filter(Doctor.email == request.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Check if licence number is already registered
    existing_licence = db.query(Doctor).filter(Doctor.licence_number == request.licence_number).first()
    if existing_licence:
        raise HTTPException(status_code=400, detail="Licence number already registered.")

    # Create the new doctor account
    doctor = Doctor(
        full_name=request.full_name,
        email=request.email,
        hashed_password=hash_password(request.password),  # Hash the password
        licence_number=request.licence_number
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return {
        "message": "Doctor account created successfully.",
        "doctor_id": doctor.id,
        "full_name": doctor.full_name,
        "email": doctor.email
    }

# ── Login Route ──
@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    # --------------------------------------------------------
    # Logs in a doctor and returns a JWT token.
    # The token must be sent with every protected request.
    # --------------------------------------------------------

    # Find the doctor by email
    doctor = db.query(Doctor).filter(Doctor.email == request.email).first()

    # Check if doctor exists and password is correct
    if not doctor or not verify_password(request.password, doctor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    # Create a JWT token for this doctor
    token = create_token({"sub": doctor.email})

    return {
        "access_token": token,       # The token the doctor will use
        "token_type": "bearer",      # Standard token type
        "doctor_id": doctor.id,
        "full_name": doctor.full_name,
        "email": doctor.email
    }

# ── Get Current Doctor Profile ──
@router.get("/me")
async def get_me(current_doctor: Doctor = Depends(get_current_doctor)):
    # Returns the currently logged in doctor's profile
    return {
        "doctor_id": current_doctor.id,
        "full_name": current_doctor.full_name,
        "email": current_doctor.email,
        "licence_number": current_doctor.licence_number,
        "created_at": current_doctor.created_at
    }