from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from ..db import get_session
from ..deps import require_admin
from ..models import User, UserRole, Employee
from ..auth import hash_password

router = APIRouter(prefix="/users", tags=["users"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def list_users(
    request: Request,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    users = session.exec(select(User)).all()
    employees = {e.id: e for e in session.exec(select(Employee)).all()}
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "user": admin,          # current logged-in user
            "users": users,
            "employees": employees,
        },
    )


@router.get("/new")
def new_user_page(
    request: Request,
    admin=Depends(require_admin),
    session: Session = Depends(get_session),
):
    employees = session.exec(select(Employee)).all()
    return templates.TemplateResponse(
        "user_new.html",
        {
            "request": request,
            "user": admin,
            "employees": employees,
            "roles": list(UserRole),
        },
    )


@router.post("/new")
def create_user(
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    employee_id: int = Form(0),
):
    # Basic duplicate check
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        return RedirectResponse("/users", status_code=303)

    employee_id_val = employee_id or None
    if employee_id_val:
        emp = session.get(Employee, employee_id_val)
        if not emp:
            employee_id_val = None

    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=UserRole(role),
        employee_id=employee_id_val,
    )
    session.add(user)
    session.commit()
    return RedirectResponse("/users", status_code=303)

@router.get("/{user_id}/edit")
def edit_user_page(
    user_id: int,
    request: Request,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),  # Only admin can edit users
):
    target = session.get(User, user_id)
    if not target:
        return RedirectResponse("/users", status_code=303)

    employees = session.exec(select(Employee)).all()
    roles = [UserRole.ADMIN, UserRole.MANAGER, UserRole.EMPLOYEE]

    return templates.TemplateResponse(
        "user_edit.html",
        {
            "request": request,
            "user": admin,
            "target_user": target,
            "employees": employees,
            "roles": roles,
        },
    )


@router.post("/{user_id}/edit")
def update_user(
    user_id: int,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
    email: str = Form(...),
    role: str = Form(...),
    employee_id: int = Form(0),
):
    target = session.get(User, user_id)
    if not target:
        return RedirectResponse("/users", status_code=303)

    # Prevent admin from accidentally locking themselves out by removing their admin role if desired
    requested_role = UserRole(role)
    if target.id == admin.id and requested_role != UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="You cannot remove your own admin role")

    target.email = email
    target.role = requested_role

    employee_id_val = employee_id or None
    if employee_id_val:
        emp = session.get(Employee, employee_id_val)
        if not emp:
            employee_id_val = None
    target.employee_id = employee_id_val

    session.add(target)
    session.commit()
    return RedirectResponse("/users", status_code=303)


@router.post("/{user_id}/delete")
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    target = session.get(User, user_id)
    if not target:
        return RedirectResponse("/users", status_code=303)

    # Don't allow deleting yourself
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    session.delete(target)
    session.commit()
    return RedirectResponse("/users", status_code=303)

@router.get("/{user_id}/password")
def change_password_page(
    user_id: int,
    request: Request,
    admin=Depends(require_admin),
    session: Session = Depends(get_session),
):
    user_obj = session.get(User, user_id)
    if not user_obj:
        return RedirectResponse("/users", status_code=303)

    return templates.TemplateResponse(
        "user_password.html",
        {
            "request": request,
            "user": admin,
            "target_user": user_obj,
        },
    )


@router.post("/{user_id}/password")
def change_password(
    user_id: int,
    new_password: str = Form(...),
    session: Session = Depends(get_session),
    admin=Depends(require_admin),
):
    user_obj = session.get(User, user_id)
    if user_obj:
        user_obj.hashed_password = hash_password(new_password)
        session.add(user_obj)
        session.commit()
    return RedirectResponse("/users", status_code=303)
