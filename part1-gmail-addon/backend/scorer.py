# הלב של המערכת - כאן קורה כל הניתוח של האימייל
# כל פונקציה בודקת דבר אחד ומחזירה כמה נקודות סיכון הוא מוסיף

import re
import json
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

URGENT_PATTERNS = re.compile(
    r"\b(urgent|urgently|immediately|action required|act now|verify now"
    r"|limited time|expires? (soon|today|in \d+)|your account (will be|has been) (suspended|locked|deactivated)"
    r"|confirm (your|account)|click (here|below|now)|update (your|billing|payment)"
    r"|unusual (activity|sign.?in)|unauthorized access|security alert"
    r"|you (have|'ve) won|congratulations|prize|reward|bonus)\b",
    re.IGNORECASE,
)

SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".club", ".online", ".site", ".tk", ".ml", ".ga",
    ".cf", ".gq", ".pw", ".work", ".click", ".link", ".download",
}

BRAND_SPOOF_PATTERNS = re.compile(
    r"\b(paypal|amazon|apple|microsoft|google|facebook|netflix|bank|wells.?fargo"
    r"|chase|citibank|irs|fedex|ups|dhl|instagram|twitter|linkedin)\b",
    re.IGNORECASE,
)

URL_REGEX = re.compile(r"https?://[^\s\"'<>()]+", re.IGNORECASE)
EMAIL_REGEX = re.compile(r"[\w.\-+]+@[\w.\-]+\.[a-zA-Z]{2,}")

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "aol.com", "mail.com", "protonmail.com", "yandex.com",
}


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


# בודקת שה-From וה-Reply-To מאותו דומיין - טריק נפוץ של תוקפים
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


# שולחת את ה-URLs ל-API של גוגל שיודע אילו אתרים ידועים כזדוניים
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


# יותר מ-5 לינקים באימייל זה חשוד
def check_url_count(body: str) -> SignalResult:
    urls = re.findall(r'https?://\S+', body)
    if len(urls) > 5:
        return SignalResult(
            name="URL Count",
            score=15,
            detail=f"Email contains {len(urls)} URLs which is unusually high"
        )
    return SignalResult(name="URL Count", score=0, detail=f"URL count looks normal ({len(urls)})")


# זיהוי תווים בינלאומיים מתחזים בשם הדומיין
def check_homoglyphs(sender: str) -> SignalResult:
    try:
        sender_domain = sender.split("@")[-1].strip(">").lower()
        if re.search(r'[^\x00-\x7F]', sender_domain):
            return SignalResult(
                name="Homoglyph Detection",
                score=40,
                detail=f"Non-ASCII characters detected in sender domain ({sender_domain}). High risk of brand impersonation."
            )
    except Exception:
        pass
    return SignalResult(name="Homoglyph Detection", score=0, detail="Sender domain contains valid ASCII characters")


# בדיקת גיל הדומיין באמצעות פרוטוקול RDAP
def check_domain_age(sender: str) -> SignalResult:
    try:
        sender_domain = sender.split("@")[-1].strip(">").lower()

        if sender_domain in FREE_EMAIL_DOMAINS:
            return SignalResult(name="Domain Age Check", score=0, detail="Sender uses a trusted public email provider")

        response = requests.get(f"https://rdap.org/domain/{sender_domain}", timeout=4)
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])

            for event in events:
                if event.get("eventAction") == "registration":
                    reg_date_str = event.get("eventDate")[:10]
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
        pass

    return SignalResult(name="Domain Age Check", score=0, detail="Domain age validation skipped or unavailable")


# בודקת אם ה-URL מגיע מדומיין עם TLD חשוד
def check_suspicious_tlds(body: str) -> SignalResult:
    urls = URL_REGEX.findall(body)
    flagged = []

    for url in urls:
        for tld in SUSPICIOUS_TLDS:
            domain_part = url.split("/")[2] if "/" in url else url
            if domain_part.endswith(tld):
                flagged.append(url)
                break

    if flagged:
        return SignalResult(
            name="Suspicious TLD",
            score=20,
            detail=f"URLs with high-risk domain extensions found: {', '.join(flagged[:3])}"
        )
    return SignalResult(name="Suspicious TLD", score=0, detail="No suspicious domain extensions found")


# בודקת אם האימייל מתחזה למותג מוכר בזמן שנשלח מדומיין לא קשור
def check_brand_spoofing(sender: str, body: str) -> SignalResult:
    brand_in_body = BRAND_SPOOF_PATTERNS.search(body)
    if not brand_in_body:
        return SignalResult(name="Brand Spoofing", score=0, detail="No brand impersonation detected")

    sender_domain = sender.split("@")[-1].strip(">").lower()
    brand = brand_in_body.group(0).lower()

    if brand not in sender_domain:
        return SignalResult(
            name="Brand Spoofing",
            score=30,
            detail=f"Email mentions '{brand}' but was sent from '{sender_domain}'"
        )
    return SignalResult(name="Brand Spoofing", score=0, detail="Sender domain matches the mentioned brand")


# מריצה את כל הבדיקות, מחברת את הציונים ומחליטה על verdict סופי
def score_email(email: EmailRequest) -> ScanResult:
    signals = [
        check_phishing_keywords(email.body),
        check_sender_mismatch(email.sender, email.reply_to or ""),
        check_urls_safe_browsing(email.urls),
        check_url_count(email.body),
        check_homoglyphs(email.sender),
        check_domain_age(email.sender),
        check_suspicious_tlds(email.body),
        check_brand_spoofing(email.sender, email.body)
    ]

    total = sum(s.score for s in signals)
    total = min(total, 100)

    if total >= 60:
        verdict = "MALICIOUS"
    elif total >= 40:
        verdict = "SUSPICIOUS"
    else:
        verdict = "SAFE"

    return ScanResult(total_score=total, verdict=verdict, signals=signals)