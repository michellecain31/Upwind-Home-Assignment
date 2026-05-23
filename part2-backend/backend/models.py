# מגדיר את מבנה הנתונים שנכנס ויוצא מה-API

from pydantic import BaseModel, EmailStr
from typing import Optional


# מה שמגיע מהפרונטאנד בעת התחברות
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# מה שחוזר אחרי התחברות מוצלחת
class LoginResponse(BaseModel):
    token: str
    user: "UserResponse"


# מה שמגיע כשיוצרים משתמש חדש
class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "analyst"


# מה שחוזר כשמבקשים פרטי משתמש - בלי סיסמה!
class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    status: str

    class Config:
        from_attributes = True


# מה שחוזר מה-API של האירועים
class EventResponse(BaseModel):
    id: str
    timestamp: str
    severity: str
    title: str
    description: str
    assetHostname: str
    assetIp: str
    sourceIp: str
    tags: list
    userId: str