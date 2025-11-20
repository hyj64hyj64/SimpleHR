from datetime import date
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

# from ..deps import require_manager_or_admin
from ..deps import require_admin
from ..models import Employee, User, Timesheet, OnboardingTask
from ..db import get_session

router = APIRouter(prefix="/employees")
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def list_employees(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
):
    employees = session.exec(select(Employee)).all()
    return templates.TemplateResponse(
        "employees.html", {"request": request, "user": user, "employees": employees}
    )


@router.get("/new")
def new_employee_page(
    request: Request,
    user: User = Depends(require_admin),
):
    # Reuse the same template for add/edit
    return templates.TemplateResponse(
        "employee_new.html",
        {
            "request": request,
            "user": user,
            "employee": None,
            "title": "Add New Employee",
            "action_url": "/employees/new",
        },
    )

@router.post("/new")
def create_employee(
    #request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    employment_type: str = Form(...),
    start_date: str = Form(...),
    position: str = Form(""),
    department: str = Form(""),
    notes: str = Form(""),
):
    emp = Employee(
        first_name=first_name,
        last_name=last_name,
        email=email,
        employment_type=employment_type,
        start_date=date.fromisoformat(start_date),
        position=position or None,
        department=department or None,
        notes=notes or None,
    )
    session.add(emp)
    session.commit()
    return RedirectResponse("/employees", status_code=303)

@router.get("/{employee_id}/edit")
def edit_employee_page(
    employee_id: int,
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
):
    emp = session.get(Employee, employee_id)
    if not emp:
        return RedirectResponse("/employees", status_code=303)

    return templates.TemplateResponse(
        "employee_new.html",
        {
            "request": request,
            "user": user,
            "employee": emp,
            "title": "Edit Employee",
            "action_url": f"/employees/{employee_id}/edit",
        },
    )


@router.post("/{employee_id}/edit")
def update_employee(
    employee_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    employment_type: str = Form(...),
    start_date: str = Form(...),
    position: str = Form(""),
    department: str = Form(""),
    notes: str = Form(""),
):
    emp = session.get(Employee, employee_id)
    if not emp:
        return RedirectResponse("/employees", status_code=303)

    emp.first_name = first_name
    emp.last_name = last_name
    emp.email = email
    emp.employment_type = employment_type
    emp.start_date = date.fromisoformat(start_date)
    emp.position = position or None
    emp.department = department or None
    emp.notes = notes or None

    session.add(emp)
    session.commit()
    return RedirectResponse("/employees", status_code=303)

@router.post("/{employee_id}/delete")
def delete_employee(
    employee_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),  # or require_admin if you want admin-only
):
    emp = session.get(Employee, employee_id)
    if not emp:
        return RedirectResponse("/employees", status_code=303)

    # 1) Delete onboarding tasks for this employee
    tasks = session.exec(
        select(OnboardingTask).where(OnboardingTask.employee_id == employee_id)
    ).all()
    for t in tasks:
        session.delete(t)

    # 2) Delete timesheets for this employee
    sheets = session.exec(
        select(Timesheet).where(Timesheet.employee_id == employee_id)
    ).all()
    for ts in sheets:
        session.delete(ts)

    # 3) Detach any user accounts linked to this employee
    users = session.exec(select(User).where(User.employee_id == employee_id)).all()
    for u in users:
        u.employee_id = None
        session.add(u)

    # 4) Finally, delete the employee
    session.delete(emp)
    session.commit()

    return RedirectResponse("/employees", status_code=303)
