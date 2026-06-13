from datetime import date

import click
from sqlalchemy.orm import Session

from app.adapters.models.cattle import Cattle
from app.adapters.models.company import Company
from app.adapters.models.device import Device
from app.adapters.models.role import Role
from app.adapters.models.user import User
from app.adapters.repositories.device_repository import DeviceRepository
from app.application.dtos.device_dto import DeviceCreateDTO
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.domain.enums.role_enum import RoleEnum


def get_db() -> Session:
    return SessionLocal()


def seed_roles(db: Session) -> None:
    for role_name in RoleEnum:
        exists = db.query(Role).filter(Role.name == role_name.value).first()
        if not exists:
            db.add(Role(name=role_name.value))
    db.commit()


def create_superuser(db: Session) -> User:
    admin_role = db.query(Role).filter(Role.name == RoleEnum.ADMIN.value).first()
    existing = db.query(User).filter(User.email == settings.SUPERUSER_EMAIL).first()

    if existing:
        click.echo(f"Superuser already exists: {existing.email}")
        return existing

    user = User(
        full_name=settings.SUPERUSER_FULL_NAME,
        birth_date=date(1990, 1, 1),
        email=settings.SUPERUSER_EMAIL,
        is_superuser=True,
        company_id=None,
        role=admin_role,
    )
    user.set_password(settings.SUPERUSER_PASSWORD)
    db.add(user)
    db.commit()
    db.refresh(user)
    click.echo(f"Superuser created: {user.email}")
    return user


def run_setup() -> None:
    Base.metadata.create_all(bind=engine)
    db = get_db()
    try:
        seed_roles(db)
        create_superuser(db)
        click.echo("Setup completed successfully.")
    finally:
        db.close()


def create_company_record(db: Session, name: str) -> Company:
    company = Company(name=name)
    db.add(company)
    db.commit()
    db.refresh(company)
    click.echo(f"Company created: id={company.id} name={company.name}")
    return company


def create_farmer_record(
    db: Session,
    full_name: str,
    email: str,
    password: str,
    birth_date: date,
    company_id: int,
    role: RoleEnum,
) -> User:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise click.ClickException(f"Company {company_id} not found")

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise click.ClickException(f"User already exists: {email}")

    role_record = db.query(Role).filter(Role.name == role.value).first()
    if not role_record:
        raise click.ClickException(f"Role {role.value} not found. Run setup first.")

    user = User(
        full_name=full_name,
        birth_date=birth_date,
        email=email,
        company_id=company_id,
        role=role_record,
        is_superuser=False,
    )
    user.set_password(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    click.echo(
        f"Farmer created: id={user.id} email={user.email} company_id={company_id}"
    )
    return user


def create_cattle_record(db: Session, tag: str, company_id: int) -> Cattle:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise click.ClickException(f"Company {company_id} not found")

    cattle = Cattle(tag=tag, company_id=company_id)
    db.add(cattle)
    db.commit()
    db.refresh(cattle)
    click.echo(
        f"Cattle created: id={cattle.id} tag={cattle.tag} company_id={company_id}"
    )
    return cattle


def create_device_record(
    db: Session,
    serial_number: str,
    cattle_id: int,
    company_id: int,
    name: str | None = None,
) -> Device:
    repository = DeviceRepository(db=db)
    device = repository.create_device(
        DeviceCreateDTO(
            serial_number=serial_number,
            cattle_id=cattle_id,
            company_id=company_id,
            name=name,
        )
    )
    click.echo(
        f"Device created: id={device.id} serial={device.serial_number} "
        f"api_key={device.api_key}"
    )
    return device
