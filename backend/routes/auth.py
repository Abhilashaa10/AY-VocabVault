
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from database import supabase

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ─────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ─────────────────────────────────────────
# SIGNUP
# POST /auth/signup
# GoTrue 
# ─────────────────────────────────────────
@router.post("/signup", status_code=201)
def signup(request: SignupRequest):
    """
    Supabase GoTrue handles:
    - Email validation
    - Password hashing
    - Storing in auth.users
    - Trigger auto-creates profile row
    """
    try:
        result = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "name": request.name
                }
            }
        })

        if result.user is None:
            raise HTTPException(
                status_code=400,
                detail="Signup failed. Please try again."
            )

        return {
            "message": f"Welcome to AY-VocabVault, {request.name}! 🎉",
            "user_id": result.user.id,
            "email": result.user.email
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─────────────────────────────────────────
# LOGIN
# POST /auth/login
# ─────────────────────────────────────────
@router.post("/login")
def login(request: LoginRequest):
    """
    GoTrue verifies credentials
    Returns JWT access token
    """
    try:
        result = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        if result.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        return {
            "access_token": result.session.access_token,
            "token_type": "bearer",
            "user_id": result.user.id,
            "email": result.user.email
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))