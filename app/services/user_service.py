from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from uuid import UUID

def create(db: Session, data: UserCreate):
    user = User(**data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get(db: Session, user_id: str):
    return db.query(User).filter(User.id == UUID(user_id)).first()

def list_all(db: Session):
    return db.query(User).all()

def update(db: Session, user_id: str, data: UserUpdate):
    user = get(db, user_id)
    if not user:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def delete(db: Session, user_id: str):
    user = get(db, user_id)
    if not user:
        return None
    db.delete(user)
    db.commit()
    return True
