# Authentication & Authorization Layer: Handles password hashing, JWT operations, and RBAC guard middleware.

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import bcrypt
from database import UserModel, get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "changeme-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 1

security = HTTPBearer()


# Hashes a plaintext password using bcrypt cryptographic salt stretching
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# Evaluates matching integrity between plaintext and persistent hashed values
def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# Generates signed JWT payload containing identity context and expiration bounds
def create_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Validates signature and decodes bearer token structures
def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


# Guard Middleware: Mandates authenticated bearer token validation across protected scopes
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> UserModel:
    payload = decode_token(credentials.credentials)
    user = db.query(UserModel).filter(UserModel.id == payload["sub"]).first()
    if not user or user.status == "disabled":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled",
        )
    return user


# RBAC Middleware: Restricts system administration operations strictly to the admin role
def require_admin(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user