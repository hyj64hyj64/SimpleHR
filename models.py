from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class Employee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str
    employment_type: str
    status: str = "active"
    start_date: date
    position: Optional[str] = None
    department: Optional[str] = None
    notes: Optional[str] = None

    user: Optional["User"] = Relationship(back_populates="employee")
    timesheets: List["Timesheet"] = Relationship(back_populates="employee")
    # 🔹 NEW:
    onboarding_tasks: List["OnboardingTask"] = Relationship(back_populates="employee")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.EMPLOYEE)
    employee_id: Optional[int] = Field(default=None, foreign_key="employee.id")

    employee: Optional[Employee] = Relationship(back_populates="user")


class TimesheetStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Timesheet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employee.id")
    week_start: date
    total_hours: float
    notes: Optional[str] = None
    status: TimesheetStatus = Field(default=TimesheetStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    employee: Employee = Relationship(back_populates="timesheets")


# 🔹 NEW – Candidate & Hiring

class CandidateStage(str, Enum):
    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    INTERVIEW = "INTERVIEW"
    BACKGROUND = "BACKGROUND"
    OFFER = "OFFER"
    HIRED = "HIRED"
    REJECTED = "REJECTED"


class Candidate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    source: Optional[str] = None  # e.g. Indeed, Referral
    stage: CandidateStage = Field(default=CandidateStage.APPLIED)
    resume_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# 🔹 NEW – Onboarding Task

class OnboardingTask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employee.id")
    title: str
    is_complete: bool = Field(default=False)
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None

    employee: Employee = Relationship(back_populates="onboarding_tasks")
