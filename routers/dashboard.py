from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from ..deps import require_user
from ..db import get_session
from ..models import Employee, Timesheet, User, TimesheetStatus

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def dashboard(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_user),
):
    employees = session.exec(select(Employee)).all()
    num_employees = len(employees)

    pending = session.exec(
        select(Timesheet).where(Timesheet.status == TimesheetStatus.PENDING)
    ).all()
    pending_timesheets = len(pending)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "num_employees": num_employees,
            "pending_timesheets": pending_timesheets,
        },
    )