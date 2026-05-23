import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, UserModel, init_db
from auth import hash_password, verify_password, create_token, get_current_user, require_admin
from models import LoginRequest, LoginResponse, CreateUserRequest, UserResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.path.exists("/app/data/mock_events.json"):
    EVENTS_PATH = "/app/data/mock_events.json"
else:
    EVENTS_PATH = os.path.join(BASE_DIR, "data", "mock_events.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/auth/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.status == "disabled":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    token = create_token(user.id, user.email, user.role)
    return {
        "token": token,
        "user": UserResponse.from_orm(user)
    }


@app.get("/api/events")
def get_events(current_user: UserModel = Depends(get_current_user)):
    if not os.path.exists(EVENTS_PATH):
        raise HTTPException(
            status_code=404,
            detail=f"Events file not found. Checked path: {EVENTS_PATH}"
        )

    try:
        with open(EVENTS_PATH, "r", encoding="utf-8") as f:
            events = json.load(f)
        return events
    except json.JSONDecodeError as je:
        raise HTTPException(status_code=500, detail=f"The JSON file is corrupted: {str(je)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error reading events: {str(e)}")


@app.get("/api/users")
def get_users(current_user: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return [UserResponse.from_orm(u) for u in users]


@app.post("/api/users", status_code=201)
def create_user(body: CreateUserRequest, current_user: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    if body.role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = UserModel(
        email=body.email,
        hashed_password=hash_password(body.password),
        role=body.role,
        status="active"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.from_orm(user)


@app.delete("/api/users/{user_id}")
def delete_user(user_id: str, current_user: UserModel = Depends(require_admin), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3001, reload=True)