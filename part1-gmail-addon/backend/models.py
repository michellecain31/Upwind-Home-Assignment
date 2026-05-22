# מגדיר את מבנה הנתונים שעובר במערכת - מה נכנס ומה יוצא מכל endpoint

from pydantic import BaseModel
from typing import List, Optional


# מה שמגיע מה-Apps Script - פרטי האימייל שנבדק
class EmailRequest(BaseModel):
    subject: str
    sender: str
    reply_to: Optional[str] = None  # לא תמיד קיים
    body: str
    urls: List[str] = []


# תוצאה של סיגנל בודד - שם, כמה נקודות הוסיף, והסבר
class SignalResult(BaseModel):
    name: str
    score: int
    detail: str


# התוצאה הסופית שחוזרת ל-Apps Script
class ScanResult(BaseModel):
    total_score: int
    verdict: str  # SAFE / SUSPICIOUS / MALICIOUS
    signals: List[SignalResult]