import uuid
from sqlalchemy import (
    Column, Boolean , DateTime,
    Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.db import Base

class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, onupdate=func.now())

    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime)
    
    version = Column(Integer, default=1, nullable=False)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = func.now()
