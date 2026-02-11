from __future__ import annotations
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field, field_validator

from models import EmploymentType


from app.models.EmunType import EmploymentType

from app.schema.base import UUIDModel , AuditMixin



class DepartmentCreate(BaseModel):
    name: str = Field(..., max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    parent_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    description: Optional[str] = None

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    code: Optional[str] = None
    parent_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class DepartmentOut(UUIDModel, AuditMixin):
    name: str
    code: Optional[str] = None
    parent_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    description: Optional[str] = None
    is_active: bool




class EmployeeCreate(BaseModel):
    user_id: UUID
    employee_number: str = Field(..., max_length=50)
    department_id: Optional[UUID] = None
    job_title: Optional[str] = None
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    joining_date: date 
    manager_id: Optional[UUID] = None
    current_salary: Optional[Decimal] = Field(None, ge=0)
    currency: str = "INR"
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None

class EmployeeUpdate(BaseModel):
    department_id: Optional[UUID] = None
    job_title: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    manager_id: Optional[UUID] = None
    current_salary: Optional[Decimal] = Field(None, ge=0)
    annual_leave_balance: Optional[Decimal] = Field(None, ge=0)
    sick_leave_balance: Optional[Decimal] = Field(None, ge=0)
    casual_leave_balance: Optional[Decimal] = Field(None, ge=0)
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None
    is_active: Optional[bool] = None
    resignation_date: Optional[date] = None
    last_working_date: Optional[date] = None

class EmployeeOut(UUIDModel, AuditMixin):
    user_id: UUID
    employee_number: str
    department_id: Optional[UUID] = None
    job_title: Optional[str] = None
    employment_type: EmploymentType
    joining_date: date
    manager_id: Optional[UUID] = None
    current_salary: Optional[Decimal] = None
    currency: str
    annual_leave_balance: Decimal
    sick_leave_balance: Decimal
    casual_leave_balance: Decimal
    is_active: bool




class AttendanceCreate(BaseModel):
    employee_id: UUID
    attendance_date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    is_present: bool = True
    is_late: bool = False
    is_half_day: bool = False
    notes: Optional[str] = None

class AttendanceUpdate(BaseModel):
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    worked_hours: Optional[Decimal] = None
    overtime_hours: Optional[Decimal] = None
    is_present: Optional[bool] = None
    is_late: Optional[bool] = None
    is_half_day: Optional[bool] = None
    notes: Optional[str] = None

class AttendanceOut(UUIDModel, AuditMixin):
    employee_id: UUID
    attendance_date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    worked_hours: Optional[Decimal] = None
    overtime_hours: Optional[Decimal] = None
    is_present: bool
    is_late: bool
    is_half_day: bool
    notes: Optional[str] = None



class LeaveRequestCreate(BaseModel):
    employee_id: UUID
    leave_type: str
    start_date: date
    end_date: date
    days_count: Decimal = Field(..., gt=0)
    reason: Optional[str] = None

class LeaveRequestUpdate(BaseModel):
    status: Optional[str] = None  # pending, approved, rejected
    rejection_reason: Optional[str] = None

class LeaveRequestOut(UUIDModel, AuditMixin):
    employee_id: UUID
    leave_type: str
    start_date: date
    end_date: date
    days_count: Decimal
    reason: Optional[str] = None
    status: str
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
