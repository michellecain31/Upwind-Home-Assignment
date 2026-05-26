# Database Configuration & ORM Architecture: Sets up SQLAlchemy connection engine, tables, and seeding context.

import uuid
from sqlalchemy import Column, create_engine, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./penguwave.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ORM Schema mapping application identity metadata to the persistent storage layer
class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="analyst")  # admin / analyst / viewer
    status = Column(String, default="active")  # active / disabled


# Bootstraps operational database schema and injects default role profiles if absent
def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    from auth import hash_password

    # 1. Seeds default administrative credentials with RBAC elevation privileges
    admin_exists = (
        db.query(UserModel).filter(UserModel.email == "admin@penguwave.io").first()
    )
    if not admin_exists:
        admin = UserModel(
            email="admin@penguwave.io",
            hashed_password=hash_password("admin123"),
            role="admin",
            status="active",
        )
        db.add(admin)

    # 2. Seeds default analytics engineering access profile bounds
    analyst_exists = (
        db.query(UserModel)
        .filter(UserModel.email == "analyst@penguwave.io")
        .first()
    )
    if not analyst_exists:
        analyst = UserModel(
            email="analyst@penguwave.io",
            hashed_password=hash_password("pass456"),
            role="analyst",
            status="active",
        )
        db.add(analyst)

    # 3. Seeds restricted observer persona deactivated by default scope contract rules
    viewer_exists = (
        db.query(UserModel)
        .filter(UserModel.email == "viewer@penguwave.io")
        .first()
    )
    if not viewer_exists:
        viewer = UserModel(
            email="viewer@penguwave.io",
            hashed_password=hash_password("view789"),
            role="viewer",
            status="disabled",
        )
        db.add(viewer)

    db.commit()
    db.close()


# Dependency Middleware: Provides isolated, request-scoped session contexts with reliable cleanup
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()