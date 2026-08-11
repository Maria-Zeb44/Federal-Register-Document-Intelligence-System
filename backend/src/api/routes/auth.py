from fastapi import APIRouter, HTTPException
from src.schemas.auth import UserCreate, UserLogin
from src.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup")
async def signup(user_data: UserCreate):
    service = AuthService()
    user = service.create_user(user_data.name, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="User already exists")
    return {"message": "User created successfully", "user": user}

@router.post("/login")
async def login(login_data: UserLogin):
    service = AuthService()
    user = service.authenticate(login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user": user}


@router.get("/auto-login")
async def auto_login():
    """Auto-login for testing - bypasses password"""
    return {
        "message": "Auto-login successful",
        "user": {
            "id": 1,
            "name": "Test User",
            "email": "test@123.com"
        }
    }