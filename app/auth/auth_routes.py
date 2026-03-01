from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(payload: dict):
    return register_user(payload)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    payload = {
        "email": form_data.username,
        "password": form_data.password
    }
    return login_user(payload)