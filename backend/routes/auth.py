# backend/routes/auth.py

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from database import supabase
from auth_utils import hash_password, verify_password, create_access_token, verify_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ─────────────────────────────────────────
# SCHEMAS
# Define what data shape we expect
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
# ─────────────────────────────────────────
@router.post("/signup", status_code=201)
def signup(request: SignupRequest):
    """
    1. Check if email already exists
    2. Hash password
    3. Save user to Supabase
    4. Return success message
    """

    # Check if email already exists
    existing = supabase.table("users")\
        .select("id")\
        .eq("email", request.email)\
        .execute()

    if existing.data:
        raise HTTPException(
            status_code=400,
            detail="Email already registered. Please login."
        )

    # Hash password
    hashed = hash_password(request.password)

    # Save to Supabase
    result = supabase.table("users").insert({
        "name": request.name,
        "email": request.email,
        "password_hash": hashed
    }).execute()

    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )

    new_user = result.data[0]

    return {
        "message": f"Welcome to AY-VocabVault, {new_user['name']}! 🎉",
        "user_id": new_user["id"]
    }


# ─────────────────────────────────────────
# LOGIN
# POST /auth/login
# ─────────────────────────────────────────
@router.post("/login")
def login(request: LoginRequest):
    """
    1. Find user by email
    2. Verify password
    3. Create JWT token
    4. Return token
    """

    # Find user by email
    result = supabase.table("users")\
        .select("*")\
        .eq("email", request.email)\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    user = result.data[0]

    # Verify password
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT token
    token = create_access_token(data={
        "sub": user["email"],
        "user_id": user["id"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_name": user["name"],
        "user_id": user["id"]
    }


# ─────────────────────────────────────────
# GET CURRENT USER
# GET /auth/me
# Protected route — needs token
# ─────────────────────────────────────────
@router.get("/me")
def get_me(authorization: str = Header(...)):
    """
    Reads token from header
    Returns current logged in user info
    """

    # Header format: "Bearer eyJxxx..."
    try:
        token = authorization.split(" ")[1]
        user_data = verify_token(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    # Fetch user from Supabase
    result = supabase.table("users")\
        .select("id, name, email, created_at")\
        .eq("email", user_data["email"])\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return result.data[0]