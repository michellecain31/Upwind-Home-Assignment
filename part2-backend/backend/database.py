# מגדיר את החיבור למסד הנתונים ואת מבנה הטבלאות

from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

DATABASE_URL = "sqlite:///./penguwave.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# טבלת המשתמשים
class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # סיסמה מוצפנת בלבד
    role = Column(String, default="analyst")  # admin / analyst / viewer
    status = Column(String, default="active")  # active / disabled


# יוצר את הטבלאות אם לא קיימות, ומאתחל משתמשי ברירת מחדל
def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    from auth import hash_password

    # 1. יצירת משתמש אדמין ברירת מחדל
    admin_exists = db.query(UserModel).filter(UserModel.email == "admin@penguwave.io").first()
    if not admin_exists:
        admin = UserModel(
            email="admin@penguwave.io",
            hashed_password=hash_password("admin123"),
            role="admin",
            status="active"
        )
        db.add(admin)

    # 2. יצירת משתמש אנליסט ברירת מחדל
    analyst_exists = db.query(UserModel).filter(UserModel.email == "analyst@penguwave.io").first()
    if not analyst_exists:
        analyst = UserModel(
            email="analyst@penguwave.io",
            hashed_password=hash_password("pass456"),
            role="analyst",
            status="active"
        )
        db.add(analyst)

    # 3. יצירת משתמש צופה (Viewer) חסום כברירת מחדל לפי ה-Contract הקיים
    viewer_exists = db.query(UserModel).filter(UserModel.email == "viewer@penguwave.io").first()
    if not viewer_exists:
        viewer = UserModel(
            email="viewer@penguwave.io",
            hashed_password=hash_password("view789"),
            role="viewer",
            status="disabled"
        )
        db.add(viewer)

    # שמירת כל השינויים למסד הנתונים במידה ונוצרו משתמשים חדשים
    db.commit()
    db.close()


# מחזיר session למסד הנתונים - נסגר אחרי כל בקשה
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()