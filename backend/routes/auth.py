from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from models import User
from auth_utils import hash_password, verify_password, create_access_token, verify_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class SignupRequest(BaseModel):
    name: str
    email: EmailStr         
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_name: str
    user_id: int

# signup
@router.post("/signup", status_code=201)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    1. Check if email already exists
    2. Hash the password
    3. Save new user to DB
    4. Return success message
    """

    # Check duplicate email
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered. Please login."
        )

    # Hash password before saving
    hashed = hash_password(request.password)

    # Create new user object
    new_user = User(
        name=request.name,
        email=request.email,
        password_hash=hashed
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": f"Welcome to AY-VocabVault, {new_user.name}! 🎉",
        "user_id": new_user.id
    }

# login
@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    1. Find user by email
    2. Verify password
    3. Create JWT token
    4. Return token to frontend
    """

    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create token
    token = create_access_token(data={"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_name": user.name,
        "user_id": user.id
    }

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    This is a DEPENDENCY — not a route
    Other routes will use this to know WHO is making the request
    Just add:  current_user: User = Depends(get_current_user)
    to any route that needs login
    """
    try:
        email = verify_token(token)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Returns logged in user's info"""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "joined": current_user.created_at
    }