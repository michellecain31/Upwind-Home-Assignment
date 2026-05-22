# הלב של המערכת - כאן קורה כל הניתוח של האימייל
# כל פונקציה בודקת דבר אחד ומחזירה כמה נקודות סיכון הוא מוסיף

import re
import requests
import os
from datetime import datetime
from models import EmailRequest, SignalResult, ScanResult
from dotenv import load_dotenv

load_dotenv()

SAFE_BROWSING_API_KEY = os.getenv("SAFE_BROWSING_API_KEY")

# ביטויים קלאסיים שמופיעים הרבה באימיילי phishing
PHISHING_KEYWORDS = [
    "verify your account", "urgent action required", "click here immediately",
    "your account has been suspended", "confirm your identity", "unusual activity",
    "update your payment", "you have won", "limited time offer"
]

# מחפשת ביטויים חשודים בתוכן האימייל - מוסיפה 30 נקודות אם מוצאת
def check_phishing_keywords(body: str) -> SignalResult:
    body_lower = body.lower()
    found = [kw for kw in PHISHING_KEYWORDS if kw in body_lower]

    if found:
        return SignalResult(
            name="Phishing Keywords",
            score=30,
            detail=f"Found suspicious phrases: {', '.join(found)}"
        )
    return SignalResult(name="Phishing Keywords", score=0, detail="No suspicious phrases found")

# בודקת שה-From וה-Reply-To מאותו דומיין - טריק נפוץ של תוקפים לשלוח מדומיין אחד ולקבל תשובות לאחר
def check_sender_mismatch(sender: str, reply_to: str) -> SignalResult:
    if not reply_to:
        return SignalResult(name="Sender Mismatch", score=0, detail="No Reply-To header")

    sender_domain = sender.split("@")[-1].strip(">").lower()
    reply_domain = reply_to.split("@")[-1].strip(">").lower()

    if sender_domain != reply_domain:
        return SignalResult(
            name="Sender Mismatch",
            score=25,
            detail=f"From domain ({sender_domain}) differs from Reply-To ({reply_domain})"
        )
    return SignalResult(name="Sender Mismatch", score=0, detail="Sender and Reply-To match")

# שולחת את ה-URLs ל-API של גוגל שיודע אילו אתרים ידועים כזדוניים - הסיגנל הכי חמור
def check_urls_safe_browsing(urls: list) -> SignalResult:
    if not urls or not SAFE_BROWSING_API_KEY:
        return SignalResult(name="URL Reputation", score=0, detail="No URLs to check")

    payload = {
        "client": {"clientId": "email-scorer", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url} for url in urls]
        }
    }

    try:
        response = requests.post(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={SAFE_BROWSING_API_KEY}",
            json=payload,
            timeout=5
        )
        data = response.json()

        if data.get("matches"):
            flagged = list(set(m["threat"]["url"] for m in data["matches"]))
            return SignalResult(
                name="URL Reputation",
                score=50,
                detail=f"Malicious URLs detected: {', '.join(flagged)}"
            )
    except Exception:
        pass

    return SignalResult(name="URL Reputation", score=0, detail="All URLs appear clean")

# יותר מ-5 לינקים באימייל זה חשוד - אימיילים לגיטימיים בדרך כלל לא מציפים בלינקים
def check_url_count(body: str) -> SignalResult:
    urls = re.findall(r'https?://\S+', body)
    if len(urls) > 5:
        return SignalResult(
            name="URL Count",
            score=15,
            detail=f"Email contains {len(urls)} URLs which is unusually high"
        )
    return SignalResult(name="URL Count", score=0, detail=f"URL count looks normal ({len(urls)})")

# זיהוי תווים בינלאומיים מתחזים בשם הדומיין (Homoglyph Attack)
def check_homoglyphs(sender: str) -> SignalResult:
    try:
        sender_domain = sender.split("@")[-1].strip(">").lower()
        # בדיקה האם קיימים תווים מחוץ לטווח ה-ASCII הסטנדרטי
        if re.search(r'[^\x00-\x7F]', sender_domain):
            return SignalResult(
                name="Homoglyph Detection",
                score=40,
                detail=f"Non-ASCII characters detected in sender domain ({sender_domain}). High risk of brand impersonation."
            )
    except Exception:
        pass
    return SignalResult(name="Homoglyph Detection", score=0, detail="Sender domain contains valid ASCII characters")

#  בדיקת גיל הדומיין באמצעות פרוטוקול RDAP 
def check_domain_age(sender: str) -> SignalResult:
    try:
        sender_domain = sender.split("@")[-1].strip(">").lower()
        
        # דילוג על ספקי מייל חינמיים נפוצים כדי לא לבצע קריאות מיותרות
        if sender_domain in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
            return SignalResult(name="Domain Age Check", score=0, detail="Sender uses a trusted public email provider")

        # פנייה לשרת RDAP ציבורי לקבלת מטא-דאטה של הדומיין
        response = requests.get(f"https://rdap.org/domain/{sender_domain}", timeout=4)
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])
            
            # חיפוש אירוע הרישום של הדומיין
            for event in events:
                if event.get("eventAction") == "registration":
                    reg_date_str = event.get("eventDate")[:10]  # חילוץ YYYY-MM-DD
                    reg_date = datetime.strptime(reg_date_str, "%Y-%m-%d")
                    age_days = (datetime.utcnow() - reg_date).days
                    
                    if age_days < 30:
                        return SignalResult(
                            name="Domain Age Check",
                            score=35,
                            detail=f"Sender domain is newly registered ({age_days} days old). High phishing correlation."
                        )
                    return SignalResult(name="Domain Age Check", score=0, detail=f"Domain age is stable ({age_days} days old)")
    except Exception:
        pass  # דגרדציה חלקה במידה וה-API לא זמין או שהדומיין לא נמצא

    return SignalResult(name="Domain Age Check", score=0, detail="Domain age validation skipped or unavailable")

# מריצה את כל הבדיקות, מחברת את הציונים ומחליטה על verdict סופי
def score_email(email: EmailRequest) -> ScanResult:
    signals = [
        check_phishing_keywords(email.body),
        check_sender_mismatch(email.sender, email.reply_to or ""),
        check_urls_safe_browsing(email.urls),
        check_url_count(email.body),
        check_homoglyphs(email.sender),
        check_domain_age(email.sender)
    ]

    total = sum(s.score for s in signals)
    total = min(total, 100)

    if total >= 60:
        verdict = "MALICIOUS"
    elif total >= 30:
        verdict = "SUSPICIOUS"
    else:
        verdict = "SAFE"

    return ScanResult(total_score=total, verdict=verdict, signals=signals)