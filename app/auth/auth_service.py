import bcrypt
from fastapi import HTTPException

from app.db.database import get_db_connection
from app.auth.jwt_handler import create_access_token


# ------------------------
# REGISTER
# ------------------------

def register_user(payload: dict):
    email = payload["email"]
    password = payload["password"]

    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT id FROM users WHERE email=?", (email,))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    c.execute(
        "INSERT INTO users (email, password) VALUES (?,?)",
        (email, hashed)
    )

    conn.commit()
    conn.close()

    return {"message": "User registered successfully"}


# ------------------------
# LOGIN
# ------------------------

def login_user(payload: dict):
    email = payload["email"]
    password = payload["password"]

    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT id, password FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = user["id"]
    hashed_password = user["password"]

    if not bcrypt.checkpw(password.encode(), hashed_password.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": user_id,
        "email": email
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }