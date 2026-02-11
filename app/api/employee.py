"""
HR endpoints – departments, employees, attendance, leave requests.
"""

from uuid import UUID
from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.api.auth import get_current_user
from app.schema.employee_schema import (
    DepartmentCreate, DepartmentUpdate, DepartmentOut,
    EmployeeCreate, EmployeeUpdate, EmployeeOut,
    AttendanceCreate, AttendanceUpdate, AttendanceOut,
    LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestOut,
)
from models import Department, Employee, Attendance, LeaveRequest, User

router = APIRouter(tags=["HR"])


# ===========================================================================
# DEPARTMENTS
# ===========================================================================

dept_router = APIRouter(prefix="/departments")


@dept_router.get("", response_model=List[DepartmentOut], summary="List departments")
def list_departments(
    is_active: Optional[bool] = None,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Department).filter(Department.is_deleted == False)
    if is_active is not None:
        q = q.filter(Department.is_active == is_active)
    return q.offset(skip).limit(limit).all()


@dept_router.post("", response_model=DepartmentOut, status_code=201, summary="Create department")
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    dept = Department(**payload.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@dept_router.get("/{dept_id}", response_model=DepartmentOut)
def get_department(dept_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    dept = db.query(Department).filter(Department.id == dept_id, Department.is_deleted == False).first()
    if not dept:
        raise HTTPException(404, "Department not found")
    return dept


@dept_router.patch("/{dept_id}", response_model=DepartmentOut)
def update_department(
    dept_id: UUID, payload: DepartmentUpdate,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    dept = db.query(Department).filter(Department.id == dept_id, Department.is_deleted == False).first()
    if not dept:
        raise HTTPException(404, "Department not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(dept, k, v)
    db.commit()
    db.refresh(dept)
    return dept


@dept_router.delete("/{dept_id}", status_code=204)
def delete_department(dept_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    dept = db.query(Department).filter(Department.id == dept_id, Department.is_deleted == False).first()
    if not dept:
        raise HTTPException(404, "Department not found")
    dept.soft_delete()
    db.commit()


router.include_router(dept_router)



emp_router = APIRouter(prefix="/employees")


@emp_router.get("", response_model=List[EmployeeOut], summary="List employees")
def list_employees(
    department_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    q = db.query(Employee).filter(Employee.is_deleted == False)
    if department_id:
        q = q.filter(Employee.department_id == department_id)
    if is_active is not None:
        q = q.filter(Employee.is_active == is_active)
    return q.offset(skip).limit(limit).all()


@emp_router.post("", response_model=EmployeeOut, status_code=201)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    if db.query(Employee).filter(Employee.employee_number == payload.employee_number).first():
        raise HTTPException(409, "Employee number already exists")
    emp = Employee(**payload.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@emp_router.get("/{emp_id}", response_model=EmployeeOut)
def get_employee(emp_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.id == emp_id, Employee.is_deleted == False).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    return emp


@emp_router.patch("/{emp_id}", response_model=EmployeeOut)
def update_employee(
    emp_id: UUID, payload: EmployeeUpdate,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    emp = db.query(Employee).filter(Employee.id == emp_id, Employee.is_deleted == False).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(emp, k, v)
    db.commit()
    db.refresh(emp)
    return emp


@emp_router.delete("/{emp_id}", status_code=204)
def delete_employee(emp_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    emp = db.query(Employee).filter(Employee.id == emp_id, Employee.is_deleted == False).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    emp.soft_delete()
    db.commit()


router.include_router(emp_router)


# ===========================================================================
# ATTENDANCE
# ===========================================================================

att_router = APIRouter(prefix="/attendance")


@att_router.get("", response_model=List[AttendanceOut], summary="List attendance records")
def list_attendance(
    employee_id: Optional[UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    q = db.query(Attendance).filter(Attendance.is_deleted == False)
    if employee_id:
        q = q.filter(Attendance.employee_id == employee_id)
    if start_date:
        q = q.filter(Attendance.attendance_date >= start_date)
    if end_date:
        q = q.filter(Attendance.attendance_date <= end_date)
    return q.order_by(Attendance.attendance_date.desc()).offset(skip).limit(limit).all()


@att_router.post("", response_model=AttendanceOut, status_code=201)
def create_attendance(
    payload: AttendanceCreate,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    existing = db.query(Attendance).filter(
        Attendance.employee_id == payload.employee_id,
        Attendance.attendance_date == payload.attendance_date,
        Attendance.is_deleted == False,
    ).first()
    if existing:
        raise HTTPException(409, "Attendance record for this date already exists")
    att = Attendance(**payload.model_dump())
    db.add(att)
    db.commit()
    db.refresh(att)
    return att


@att_router.get("/{att_id}", response_model=AttendanceOut)
def get_attendance(att_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    att = db.query(Attendance).filter(Attendance.id == att_id, Attendance.is_deleted == False).first()
    if not att:
        raise HTTPException(404, "Attendance record not found")
    return att


@att_router.patch("/{att_id}", response_model=AttendanceOut)
def update_attendance(
    att_id: UUID, payload: AttendanceUpdate,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    att = db.query(Attendance).filter(Attendance.id == att_id, Attendance.is_deleted == False).first()
    if not att:
        raise HTTPException(404, "Attendance record not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(att, k, v)
    db.commit()
    db.refresh(att)
    return att


router.include_router(att_router)


# ===========================================================================
# LEAVE REQUESTS
# ===========================================================================

leave_router = APIRouter(prefix="/leave-requests")


@leave_router.get("", response_model=List[LeaveRequestOut])
def list_leave_requests(
    employee_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    q = db.query(LeaveRequest).filter(LeaveRequest.is_deleted == False)
    if employee_id:
        q = q.filter(LeaveRequest.employee_id == employee_id)
    if status:
        q = q.filter(LeaveRequest.status == status)
    return q.order_by(LeaveRequest.created_at.desc()).offset(skip).limit(limit).all()


@leave_router.post("", response_model=LeaveRequestOut, status_code=201)
def create_leave_request(
    payload: LeaveRequestCreate,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    leave = LeaveRequest(**payload.model_dump())
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


@leave_router.get("/{leave_id}", response_model=LeaveRequestOut)
def get_leave_request(leave_id: UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id, LeaveRequest.is_deleted == False).first()
    if not leave:
        raise HTTPException(404, "Leave request not found")
    return leave


@leave_router.patch("/{leave_id}", response_model=LeaveRequestOut, summary="Approve / Reject leave")
def update_leave_request(
    leave_id: UUID, payload: LeaveRequestUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id, LeaveRequest.is_deleted == False).first()
    if not leave:
        raise HTTPException(404, "Leave request not found")
    if payload.status:
        leave.status = payload.status
        leave.approved_by = current_user.id
        from datetime import datetime
        leave.approved_at = datetime.utcnow()
    if payload.rejection_reason:
        leave.rejection_reason = payload.rejection_reason
    db.commit()
    db.refresh(leave)
    return leave


router.include_router(leave_router)
