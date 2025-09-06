from sqlalchemy.orm import Session
import models, schemas
from auth import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, nickname=user.nickname)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

from sqlalchemy.orm import joinedload

def get_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Message).options(joinedload(models.Message.sender)).order_by(models.Message.timestamp.asc()).offset(skip).limit(limit).all()

def create_message(db: Session, message: schemas.MessageCreate, user_id: int):
    db_message = models.Message(**message.dict(), sender_id=user_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
