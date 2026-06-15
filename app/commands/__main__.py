import click

from app.adapters.database.session_factory import SessionFactory
from app.commands.services import (
    create_cattle_record,
    create_company_record,
    create_device_record,
    create_farmer_record,
    run_seed,
    run_setup,
)
from app.domain.enums.role_enum import RoleEnum


@click.group()
def cli():
    """CowTrack management commands."""


@cli.command("setup")
def setup():
    """Initialize database tables, roles, and superuser for local development."""
    run_setup()


@cli.command("seed")
def seed():
    """Initialize database and load idempotent dev sample data."""
    run_setup()
    run_seed()


@cli.command("create-company")
@click.option("--name", required=True, help="Company name")
def create_company(name: str):
    """Create a new company (farm)."""
    db = SessionFactory.create()
    try:
        create_company_record(db, name)
    finally:
        db.close()


@cli.command("create-farmer")
@click.option("--full-name", required=True, help="Farmer full name")
@click.option("--email", required=True, help="Farmer email")
@click.option("--password", required=True, help="Farmer password")
@click.option("--birth-date", required=True, type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option("--company-id", required=True, type=int, help="Company ID")
@click.option(
    "--role",
    default=RoleEnum.MANAGER.value,
    type=click.Choice([role.value for role in RoleEnum]),
    help="Farmer role",
)
def create_farmer(full_name, email, password, birth_date, company_id, role):
    """Create a farmer user linked to a company."""
    db = SessionFactory.create()
    try:
        create_farmer_record(
            db=db,
            full_name=full_name,
            email=email,
            password=password,
            birth_date=birth_date.date(),
            company_id=company_id,
            role=RoleEnum(role),
        )
    finally:
        db.close()


@cli.command("create-cattle")
@click.option("--tag", required=True, help="Cattle tag identifier")
@click.option("--company-id", required=True, type=int, help="Company ID")
def create_cattle(tag: str, company_id: int):
    """Register a new cattle animal for a company."""
    db = SessionFactory.create()
    try:
        create_cattle_record(db, tag, company_id)
    finally:
        db.close()


@cli.command("create-device")
@click.option("--serial", required=True, help="LoRa device serial number")
@click.option("--cattle-id", required=True, type=int, help="Cattle ID to attach")
@click.option("--company-id", required=True, type=int, help="Company ID")
@click.option("--name", default=None, help="Optional device name")
def create_device(serial: str, cattle_id: int, company_id: int, name: str | None):
    """Register a LoRa GPS device linked to a cattle and company."""
    db = SessionFactory.create()
    try:
        create_device_record(db, serial, cattle_id, company_id, name)
    finally:
        db.close()


if __name__ == "__main__":
    cli()
