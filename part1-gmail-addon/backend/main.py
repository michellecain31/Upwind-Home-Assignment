import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager # <--- הוספת אימפורט זה
from models import EmailRequest
from scorer import score_email
from database import init_db, save_scan, get_recent_scans

# הגדרת ה-lifespan שיוודא שהטבלה נוצרת תמיד, גם בריענון
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db() # יוצר את הטבלה מיד כשהשרת עולה
    yield

# חיבור ה-lifespan לאפליקציה
app = FastAPI(lifespan=lifespan)

# מאפשר ל-Apps Script של גוגל לדבר עם השרת שלנו
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scan")
def scan_email(email: EmailRequest):
    result = score_email(email)

    save_scan(
        sender=email.sender,
        subject=email.subject,
        verdict=result.verdict,
        total_score=result.total_score,
        signals=[s.dict() for s in result.signals]
    )

    return result

@app.get("/history")
def get_history():
    return get_recent_scans()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)