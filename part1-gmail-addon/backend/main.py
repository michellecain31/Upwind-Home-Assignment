# FastAPI Gateway: Manages Gmail Add-on evaluation flows and storage operations.

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import EmailRequest
from scorer import score_email
from database import init_db, save_scan, get_recent_scans


# Ensures persistent database schema initialization on server startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

# CORS: Permits cross-origin resource sharing from Google Apps Script environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# POST /scan: Evaluates payload threat level and registers telemetry logs
@app.post("/scan")
def scan_email(email: EmailRequest):
    result = score_email(email)

    save_scan(
        sender=email.sender,
        subject=email.subject,
        verdict=result.verdict,
        total_score=result.total_score,
        signals=[s.dict() for s in result.signals],
    )

    return result


# GET /history: Fetches chronological evaluation logs for history views
@app.get("/history")
def get_history():
    return get_recent_scans()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)