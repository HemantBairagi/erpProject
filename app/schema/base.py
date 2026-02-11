from datetime import datetime
from typing import Optional
from  pydantic import BaseModel
from uuid import UUID
class UUIDModel(BaseModel):
    id: UUID

    model_config = {"from_attributes": True}


class AuditMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None