# create_initial_user.py

import os
from sqlmodel import Session, select
from app.db import engine, init_db
from app.models import User, Employee, UserRole
from app.auth import hash_password
from datetime import date

def create_initial_user():
    print("Initializing database...")
    init_db()

    with Session(engine) as session:
        # Check if an admin user already exists
        admin = session.exec(select(User).where(User.role == UserRole.ADMIN)).first()

        if admin:
            print("Admin user already exists:", admin.email)
            return

        print("Creating initial admin employee...")
        emp = Employee(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            employment_type="W2",
            start_date=date(2025, 1, 1)
        )
        session.add(emp)
        session.commit()
        session.refresh(emp)

        print("Creating admin login user...")
        admin_user = User(
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN,
            employee_id=emp.id,
        )
        session.add(admin_user)
        session.commit()

        print("Admin user created successfully!")
        print("Login email: admin@example.com")
        print("Login password: admin123")

if __name__ == "__main__":
    create_initial_user()
