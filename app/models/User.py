from pydantic import BaseModel
from sqlalchemy import (
    Column, String, Boolean,DateTime,
    Integer
)
from sqlalchemy.dialects.postgresql import JSON
from app.models.base import BaseModel
class User(BaseModel):
    __tablename__ = "users"

    # Basic Info
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))  
    
    # Role & Status
    # role = Column(SQLEnum(UserRole), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Contact
    phone = Column(String(20))
    mobile = Column(String(20))
    
    # Profile
    avatar_url = Column(String(500))
    language = Column(String(10), default='en')
    timezone = Column(String(50), default='UTC')
    
    # Security
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    password_changed_at = Column(DateTime)
    
    # Preferences (JSON for flexibility)
    preferences = Column(JSON, default={})
    
    # Relationships
    # employee_profile = relationship("Employee", back_populates="user", uselist=False)
    # created_sales = relationship("Sale", back_populates="creator", foreign_keys="Sale.created_by")
    # assigned_leads = relationship("Lead", back_populates="sales_rep", foreign_keys="Lead.assigned_to")
    # assigned_tickets = relationship("Ticket", back_populates="assignee", foreign_keys="Ticket.assigned_to")
    
    # __table_args__ = (
    #     CheckConstraint("failed_login_attempts >= 0", name="ck_user_failed_attempts"),
    #     Index("idx_users_active_role", "is_active", "role"),
    # )
