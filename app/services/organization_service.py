from sqlalchemy.orm import Session
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from uuid import UUID

def create(db: Session, data: OrganizationCreate):
    org = Organization(**data.dict())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

def get(db: Session, org_id: str):
    return db.query(Organization).filter(Organization.id == UUID(org_id)).first()

def list_all(db: Session):
    return db.query(Organization).all()

def list_by_owner(db: Session, owner_id: str):
    return db.query(Organization).filter(Organization.owner_id == UUID(owner_id)).all()

def update(db: Session, org_id: str, data: OrganizationUpdate):
    org = get(db, org_id)
    if not org:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(org, key, value)
    db.commit()
    db.refresh(org)
    return org

def delete(db: Session, org_id: str):
    org = get(db, org_id)
    if not org:
        return None
    db.delete(org)
    db.commit()
    return True
