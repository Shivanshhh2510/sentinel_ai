import bcrypt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.auth.jwt_handler import create_access_token


# ------------------------
# REGISTER
# ------------------------

def register_user(payload: dict, db: Session):
    email = payload["email"]
    password = payload["password"]

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    new_user = User(
        email=email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


# ------------------------
# LOGIN
# ------------------------

def login_user(payload: dict, db: Session):
    email = payload["email"]
    password = payload["password"]

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": user.id,
        "email": user.email
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }