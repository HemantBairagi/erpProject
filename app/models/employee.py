from enum import Enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, String, Boolean, Enum as SQLEnum, Index, DateTime,
     ForeignKey, CheckConstraint, Text, Date, Numeric,
    UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from app.db.db import Base
from pydantic import BaseModel

from app.models.EmunType import EmploymentType


class Department(BaseModel):
    """Organization departments"""
    __tablename__ = "departments"
    
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True)
    parent_id = Column(ForeignKey("departments.id", ondelete="SET NULL"))
    manager_id = Column(ForeignKey("users.id", ondelete="SET NULL"))
    
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    parent = relationship("Department", remote_side="Department.id", backref="sub_departments")
    manager = relationship("User")

class Employee(BaseModel):
    """
    Employee HR records linked to User accounts.
    Contains employment details, salary, leave balances, etc.
    """
    __tablename__ = "employees"

    # Link to User
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Employee Details
    employee_number = Column(String(50), unique=True, nullable=False, index=True)
    department_id = Column(ForeignKey("departments.id", ondelete="SET NULL"))
    job_title = Column(String(100))
    employment_type = Column(SQLEnum(EmploymentType), default=EmploymentType.FULL_TIME)
    
    # Dates
    joining_date = Column(Date, nullable=False)
    confirmation_date = Column(Date)
    resignation_date = Column(Date)
    last_working_date = Column(Date)
    
    # Manager
    manager_id = Column(ForeignKey("employees.id", ondelete="SET NULL"))
    
    # Compensation
    current_salary = Column(Numeric(12, 2))
    currency = Column(String(3), default='INR')
    
    # Leave Balances
    annual_leave_balance = Column(Numeric(5, 2), default=0)
    sick_leave_balance = Column(Numeric(5, 2), default=0)
    casual_leave_balance = Column(Numeric(5, 2), default=0)
    
    # Emergency Contact
    emergency_contact_name = Column(String(100))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relation = Column(String(50))
    
    # Address
    current_address = Column(Text)
    permanent_address = Column(Text)
    
    # Documents (JSON array of document metadata)
    documents = Column(JSON, default=[])
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="employee_profile")
    department = relationship("Department")
    manager = relationship("Employee", remote_side="Employee.id", backref="team_members")
    attendances = relationship("Attendance", back_populates="employee")
    
    __table_args__ = (
        CheckConstraint("current_salary >= 0", name="ck_employee_salary"),
        CheckConstraint("annual_leave_balance >= 0", name="ck_annual_leave"),
        Index("idx_employees_active", "is_active"),
        Index("idx_employees_department", "department_id"),
    )

class Attendance(BaseModel):
    """Daily attendance records with check-in/check-out"""
    __tablename__ = "attendances"

    employee_id = Column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    
    # Calculated fields
    worked_hours = Column(Numeric(5, 2))
    overtime_hours = Column(Numeric(5, 2), default=0)
    
    # Status
    is_present = Column(Boolean, default=True)
    is_late = Column(Boolean, default=False)
    is_half_day = Column(Boolean, default=False)
    
    notes = Column(Text)
    
    # Relationships
    employee = relationship("Employee", back_populates="attendances")
    
    __table_args__ = (
        UniqueConstraint("employee_id", "attendance_date", name="uq_attendance_employee_date"),
        CheckConstraint("worked_hours >= 0", name="ck_worked_hours"),
        Index("idx_attendance_date", "attendance_date"),
    )

class LeaveRequest(BaseModel):
    """Employee leave/vacation requests"""
    __tablename__ = "leave_requests"
    
    employee_id = Column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type = Column(String(50), nullable=False)  # annual, sick, casual, unpaid
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_count = Column(Numeric(5, 2), nullable=False)
    
    reason = Column(Text)
    status = Column(String(20), default='pending')  # pending, approved, rejected
    
    approved_by = Column(ForeignKey("users.id", ondelete="SET NULL"))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Relationships
    employee = relationship("Employee")
    approver = relationship("User")
    
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="ck_leave_dates"),
        CheckConstraint("days_count > 0", name="ck_leave_days"),
        Index("idx_leave_status", "status"),
        Index("idx_leave_dates", "start_date", "end_date"),
    )