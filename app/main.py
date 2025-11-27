from fastapi import FastAPI, Request, Form, Depends, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from .db import init_db, engine, get_session
from .models import User, UserRole, Employee
from .auth import verify_password, hash_password, create_session_cookie, clear_session_cookie
from .routers import dashboard, employees, timesheets, hiring, onboarding, quickbooks, users

from datetime import date

app = FastAPI(title="Simple HR")

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup():
    init_db()
    with Session(engine) as session:
        admin = session.exec(select(User).where(User.role == UserRole.ADMIN)).first()
        if not admin:
            emp = Employee(
                first_name="Admin",
                last_name="User",
                email="admin@example.com",
                employment_type="W2",
                start_date=date(2025, 1, 1),  # ✅ proper Python date
            )
            session.add(emp)
            session.commit()
            session.refresh(emp)

            admin_user = User(
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                employee_id=emp.id,
            )
            session.add(admin_user)
            session.commit()


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": None}
    )


@app.post("/login")
def login_action(
    request: Request,
    session: Session = Depends(get_session),
    email: str = Form(...),
    password: str = Form(...),
):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"},
            status_code=400,
        )
#    create_session_cookie(response, user.id)

    # 🔹 Redirect based on role:
#    if user.role == UserRole.ADMIN:
#        target = "/"
#    else:
#        target = "/timesheets/me"

#    return RedirectResponse(target, status_code=303)
    # Create the redirect *first*
    response = RedirectResponse(url="/", status_code=303)
    # Attach the cookie to THAT response
    create_session_cookie(response, user.id)
    return response


@app.get("/logout")
def logout(response: Response):
    clear_session_cookie(response)
    return RedirectResponse("/login", status_code=303)

@app.get("/")
def read_root():
    return {"status": "ok"}

app.include_router(dashboard.router)
app.include_router(employees.router)
app.include_router(timesheets.router)
app.include_router(hiring.router)
app.include_router(onboarding.router)
app.include_router(users.router)   # NEW
app.include_router(quickbooks.router)  # NEW
