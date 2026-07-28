import secrets
from dataclasses import asdict

from sqladmin import ModelView, expose
from sqladmin.filters import AllUniqueStringValuesFilter, BooleanFilter
from starlette.requests import Request
from starlette.responses import JSONResponse
from wtforms import PasswordField, validators

from app.adapters.container import container
from app.adapters.gateways.address.composite_address_lookup_gateway import (
    normalize_country_code,
)
from app.adapters.models.cattle import Cattle
from app.adapters.models.company import Company
from app.adapters.models.device import Device
from app.adapters.models.gateway import Gateway
from app.adapters.models.role import Role
from app.adapters.models.user import User
from app.application.dtos.address_dto import AddressLookupRequestDTO
from app.domain.exceptions.address import UnsupportedCountryError


class CompanyAdmin(ModelView, model=Company):
    name = "Company"
    name_plural = "Companies"
    icon = "fa-solid fa-building"

    create_template = "sqladmin/company_create.html"
    edit_template = "sqladmin/company_edit.html"

    column_list = [
        Company.id,
        Company.name,
        Company.city,
        Company.state,
        Company.is_active,
        Company.created_at,
    ]
    column_searchable_list = [Company.name, Company.email, Company.city]
    column_sortable_list = [Company.id, Company.name, Company.is_active]
    column_filters = [
        BooleanFilter(Company.is_active),
        AllUniqueStringValuesFilter(Company.state),
        AllUniqueStringValuesFilter(Company.city),
    ]
    form_columns = [
        Company.name,
        Company.description,
        Company.country,
        Company.zip_code,
        Company.address,
        Company.city,
        Company.state,
        Company.phone,
        Company.email,
        Company.is_active,
    ]
    form_args = {
        "country": {
            "description": (
                "Use Brazil / BR for CEP autofill (ViaCEP). Other countries later."
            ),
        },
        "zip_code": {
            "description": (
                "Brazilian CEP: leave the field to autofill address, city and state."
            ),
        },
    }

    @expose("/address-lookup", methods=["GET"])
    async def address_lookup(self, request: Request):
        postal_code = (request.query_params.get("postal_code") or "").strip()
        country = (request.query_params.get("country") or "").strip() or "BR"

        if not postal_code:
            return JSONResponse(
                {"found": False, "detail": "postal_code is required."},
                status_code=400,
            )

        use_case = container.lookup_address_use_case(
            payload=AddressLookupRequestDTO(
                postal_code=postal_code,
                country=country,
            )
        )
        try:
            use_case.run()
        except UnsupportedCountryError as exc:
            return JSONResponse(
                {
                    "found": False,
                    "detail": (
                        f"Address lookup is not available for '{exc.country_code}' yet."
                    ),
                },
                status_code=501,
            )

        if use_case.data is None:
            return JSONResponse(
                {"found": False, "detail": "CEP not found."},
                status_code=404,
            )

        return JSONResponse({"found": True, **asdict(use_case.data)})

    async def on_model_change(self, data, model, is_created, request):
        """Server-side fallback: enrich empty address fields from CEP when Brazil."""
        postal_code = (data.get("zip_code") or "").strip()
        country = (data.get("country") or "").strip() or "BR"
        if not postal_code:
            return
        if normalize_country_code(country) != "BR":
            return

        use_case = container.lookup_address_use_case(
            payload=AddressLookupRequestDTO(
                postal_code=postal_code,
                country=country,
            )
        )
        try:
            use_case.run()
        except UnsupportedCountryError:
            return

        address = use_case.data
        if address is None:
            return

        if not (data.get("address") or "").strip() and address.address_line:
            data["address"] = address.address_line
        if not (data.get("city") or "").strip() and address.city:
            data["city"] = address.city
        if not (data.get("state") or "").strip() and address.state:
            data["state"] = address.state
        if address.postal_code:
            data["zip_code"] = address.postal_code
        if not (data.get("country") or "").strip():
            data["country"] = "Brazil"


class CattleAdmin(ModelView, model=Cattle):
    name = "Cattle"
    name_plural = "Cattle"
    icon = "fa-solid fa-cow"

    column_list = [
        Cattle.id,
        Cattle.tag,
        Cattle.name,
        Cattle.breed,
        Cattle.gender,
        Cattle.company,
        Cattle.is_active,
        Cattle.notes,
    ]
    column_searchable_list = [Cattle.tag, Cattle.name, Cattle.breed, Cattle.notes]
    column_sortable_list = [Cattle.id, Cattle.tag, Cattle.name, Cattle.is_active]
    column_filters = [
        BooleanFilter(Cattle.is_active),
        AllUniqueStringValuesFilter(Cattle.breed),
    ]
    form_excluded_columns = [Cattle.device]
    form_ajax_refs = {
        "company": {
            "fields": ("name",),
            "order_by": "name",
        }
    }


class DeviceAdmin(ModelView, model=Device):
    name = "Device"
    name_plural = "Devices"
    icon = "fa-solid fa-microchip"

    column_list = [
        Device.id,
        Device.serial_number,
        Device.name,
        Device.cattle,
        Device.company,
        Device.is_active,
        Device.last_seen_at,
    ]
    column_searchable_list = [Device.serial_number, Device.name]
    column_sortable_list = [Device.id, Device.serial_number, Device.is_active]
    column_filters = [BooleanFilter(Device.is_active)]
    column_details_exclude_list = []
    form_columns = [
        Device.serial_number,
        Device.name,
        Device.cattle,
        Device.company,
        Device.is_active,
        Device.transmission_interval_minutes,
    ]
    form_ajax_refs = {
        "cattle": {
            "fields": ("tag", "name"),
            "order_by": "tag",
        },
        "company": {
            "fields": ("name",),
            "order_by": "name",
        },
    }


class GatewayAdmin(ModelView, model=Gateway):
    name = "Gateway"
    name_plural = "Gateways"
    icon = "fa-solid fa-tower-broadcast"

    column_list = [
        Gateway.id,
        Gateway.serial_number,
        Gateway.name,
        Gateway.company,
        Gateway.is_active,
        Gateway.last_seen_at,
    ]
    column_searchable_list = [Gateway.serial_number, Gateway.name]
    column_sortable_list = [Gateway.id, Gateway.serial_number, Gateway.is_active]
    column_filters = [BooleanFilter(Gateway.is_active)]
    column_details_exclude_list = [Gateway.api_key]
    form_columns = [
        Gateway.serial_number,
        Gateway.name,
        Gateway.company,
        Gateway.is_active,
    ]
    form_ajax_refs = {
        "company": {
            "fields": ("name",),
            "order_by": "name",
        },
    }

    async def on_model_change(self, data, model, is_created, request):
        if is_created:
            data["api_key"] = secrets.token_urlsafe(32)


class RoleAdmin(ModelView, model=Role):
    name = "Role"
    name_plural = "Roles"
    icon = "fa-solid fa-shield-halved"

    column_list = [Role.id, Role.name, Role.created_at]
    column_searchable_list = [Role.name]
    can_create = False
    can_delete = False
    form_excluded_columns = [Role.users]


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_list = [
        User.id,
        User.full_name,
        User.email,
        User.role,
        User.company,
        User.is_superuser,
        User.created_at,
    ]
    column_searchable_list = [User.full_name, User.email, User.cpf, User.phone]
    column_sortable_list = [User.id, User.email, User.is_superuser]
    column_filters = [BooleanFilter(User.is_superuser)]
    form_excluded_columns = ["_password_hash"]
    form_ajax_refs = {
        "role": {
            "fields": ("name",),
            "order_by": "name",
        },
        "company": {
            "fields": ("name",),
            "order_by": "name",
        },
    }
    form_extra_fields = {
        "password": PasswordField(
            "Password",
            validators=[validators.Optional(), validators.Length(min=8)],
            description="Required when creating a user. Leave blank to keep current.",
        )
    }

    async def on_model_change(self, data, model, is_created, request):
        password = data.pop("password", None)
        if is_created and not password:
            raise ValueError("Password is required when creating a user")
        if password:
            model.set_password(password)
