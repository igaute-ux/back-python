from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID

class OrganizationBase(BaseModel):
    name: str
    industry: Optional[str] = None
    country: Optional[str] = None
    company_size: Optional[str] = None
    employees_number: Optional[int] = None
    website: Optional[HttpUrl] = None
    owner_id: UUID  # <- requerido

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    company_size: Optional[str] = None
    employees_number: Optional[int] = None
    website: Optional[HttpUrl] = None
    # Si NO quieres permitir transferir propiedad por API, no incluyas owner_id aquí.

class OrganizationOut(OrganizationBase):
    id: UUID
    class Config:
        from_attributes = True

# (Opcional) Para retornar info breve del owner en el mismo payload
class OwnerMini(BaseModel):
    id: UUID
    name: str
    surname: str
    email: str

class OrganizationWithOwner(OrganizationOut):
    owner: OwnerMini
