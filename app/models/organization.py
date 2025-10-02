from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP, text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    industry = Column(String)
    country = Column(String)
    company_size = Column(String)
    employees_number = Column(Integer)
    website = Column(String)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))

    owner = relationship("User", back_populates="organizations")

