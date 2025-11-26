from datetime import date
from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

# from ..deps import require_manager_or_admin
from ..deps import require_admin
from ..db import get_session
from ..models import User, Employee, OnboardingTask

router = APIRouter(prefix="/onboarding", tags=["onboarding"])
templates = Jinja2Templates(directory="app/templates")

# 🔹 Simple default tasks; you can later move this to a template table
DEFAULT_TASK_TITLES = [
    "Collect W-4 / W-9",
    "I-9 + ID verification",
    "Handbook acknowledgement",
    "Set up email account",
    "Provide safety training",
    "30-day check-in",
    "60-day check-in",
    "90-day check-in",
]


def ensure_onboarding_tasks_for_employee(session: Session, employee: Employee):
    existing = session.exec(
        select(OnboardingTask).where(OnboardingTask.employee_id == employee.id)
    ).all()
    if not existing:
        for title in DEFAULT_TASK_TITLES:
            task = OnboardingTask(
                employee_id=employee.id,
                title=title,
                due_date=None,
            )
            session.add(task)
        session.commit()


@router.get("")
def onboarding_overview(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
):
    employees = session.exec(select(Employee)).all()
    overview = []

    for emp in employees:
        ensure_onboarding_tasks_for_employee(session, emp)
        tasks = session.exec(
            select(OnboardingTask).where(OnboardingTask.employee_id == emp.id)
        ).all()
        total = len(tasks)
        done = sum(1 for t in tasks if t.is_complete)
        percent = int(done * 100 / total) if total else 0
        overview.append({"employee": emp, "total": total, "done": done, "percent": percent})

    return templates.TemplateResponse(
        "onboarding.html",
        {"request": request, "user": user, "overview": overview},
    )


@router.get("/{employee_id}")
def onboarding_employee_detail(
    employee_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
):
    emp = session.get(Employee, employee_id)
    if not emp:
        return RedirectResponse("/onboarding", status_code=303)

    ensure_onboarding_tasks_for_employee(session, emp)
    tasks = session.exec(
        select(OnboardingTask).where(OnboardingTask.employee_id == emp.id)
    ).all()

    return templates.TemplateResponse(
        "onboarding_employee.html",
        {"request": request, "user": user, "employee": emp, "tasks": tasks},
    )


@router.post("/{employee_id}/tasks/{task_id}/toggle")
def toggle_onboarding_task(
    employee_id: int,
    task_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
):
    task = session.get(OnboardingTask, task_id)
    if task and task.employee_id == employee_id:
        task.is_complete = not task.is_complete
        if task.is_complete and not task.completed_at:
            from datetime import datetime
            task.completed_at = datetime.utcnow()
        session.add(task)
        session.commit()
    return RedirectResponse(f"/onboarding/{employee_id}", status_code=303)
