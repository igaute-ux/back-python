from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import organization_service
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationOut

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.post("/", response_model=OrganizationOut)
def create_organization(data: OrganizationCreate, db: Session = Depends(get_db)):
    return organization_service.create(db, data)

@router.get("/{org_id}", response_model=OrganizationOut)
def get_organization(org_id: str, db: Session = Depends(get_db)):
    org = organization_service.get(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.get("/", response_model=list[OrganizationOut])
def list_organizations(db: Session = Depends(get_db)):
    return organization_service.list_all(db)

@router.get("/owner/{owner_id}", response_model=list[OrganizationOut])
def list_organizations_by_owner(owner_id: str, db: Session = Depends(get_db)):
    return organization_service.list_by_owner(db, owner_id)

@router.put("/{org_id}", response_model=OrganizationOut)
def update_organization(org_id: str, data: OrganizationUpdate, db: Session = Depends(get_db)):
    org = organization_service.update(db, org_id, data)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.delete("/{org_id}")
def delete_organization(org_id: str, db: Session = Depends(get_db)):
    success = organization_service.delete(db, org_id)
    if not success:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {"ok": True}
