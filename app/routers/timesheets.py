from datetime import date
from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from ..deps import require_user, require_manager_or_admin
from ..db import get_session
from ..models import Timesheet, TimesheetStatus, User

router = APIRouter(prefix="/timesheets")
templates = Jinja2Templates(directory="app/templates")


@router.get("/me")
def my_timesheets(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_user),
):
    if not user.employee_id:
        timesheets = []
    else:
        timesheets = session.exec(
            select(Timesheet).where(Timesheet.employee_id == user.employee_id)
        ).all()

    return templates.TemplateResponse(
        "my_timesheet.html", {"request": request, "user": user, "timesheets": timesheets}
    )


@router.post("/me")
def submit_timesheet(
    session: Session = Depends(get_session),
    user: User = Depends(require_user),
    week_start: str = Form(...),
    total_hours: float = Form(...),
    notes: str = Form(""" """),
):
    if not user.employee_id:
        return RedirectResponse("/timesheets/me", status_code=303)

    ts = Timesheet(
        employee_id=user.employee_id,
        week_start=date.fromisoformat(week_start),
        total_hours=total_hours,
        notes=notes or None,
        status=TimesheetStatus.PENDING,
    )
    session.add(ts)
    session.commit()
    return RedirectResponse("/timesheets/me", status_code=303)


@router.get("/approvals")
def approval_list(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_manager_or_admin),
):
    pending = session.exec(
        select(Timesheet).where(Timesheet.status == TimesheetStatus.PENDING)
    ).all()
    return templates.TemplateResponse(
        "timesheet_approvals.html",
        {"request": request, "user": user, "pending": pending},
    )


@router.post("/{timesheet_id}/approve")
def approve(timesheet_id: int,
            session: Session = Depends(get_session),
            user: User = Depends(require_manager_or_admin)):
    ts = session.get(Timesheet, timesheet_id)
    if ts:
        ts.status = TimesheetStatus.APPROVED
        session.add(ts)
        session.commit()
    return RedirectResponse("/timesheets/approvals", status_code=303)


@router.post("/{timesheet_id}/reject")
def reject(timesheet_id: int,
           session: Session = Depends(get_session),
           user: User = Depends(require_manager_or_admin)):
    ts = session.get(Timesheet, timesheet_id)
    if ts:
        ts.status = TimesheetStatus.REJECTED
        session.add(ts)
        session.commit()
    return RedirectResponse("/timesheets/approvals", status_code=303)
