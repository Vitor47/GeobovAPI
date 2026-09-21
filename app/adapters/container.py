from dependency_injector import containers, providers

from app.adapters.gateways.address import build_address_lookup_gateway
from app.adapters.repositories.cattle_data_repository import CattleDataRepository
from app.adapters.repositories.cattle_repository import CattleRepository
from app.adapters.repositories.company_repository import CompanyRepository
from app.adapters.repositories.device_repository import DeviceRepository
from app.adapters.repositories.gateway_repository import GatewayRepository
from app.adapters.repositories.user_repository import UserRepository
from app.application.use_cases.address.lookup_address_use_case import (
    LookupAddressUseCase,
)
from app.application.use_cases.cattle.create_cattle_use_case import (
    CreateCattleUseCase,
)
from app.application.use_cases.cattle.get_cattle_use_case import (
    GetCattleUseCase,
)
from app.application.use_cases.cattle.list_cattles_use_case import (
    ListCattlesUseCase,
)
from app.application.use_cases.cattle.update_cattle_use_case import (
    UpdateCattleUseCase,
)
from app.application.use_cases.company.create_company_use_case import (
    CreateCompanyUseCase,
)
from app.application.use_cases.company.get_company_use_case import (
    GetCompanyUseCase,
)
from app.application.use_cases.company.list_companies_use_case import (
    ListCompaniesUseCase,
)
from app.application.use_cases.device.create_device_use_case import (
    CreateDeviceUseCase,
)
from app.application.use_cases.device.get_device_use_case import (
    GetDeviceUseCase,
)
from app.application.use_cases.device.get_devices_use_case import (
    GetDevicesUseCase,
)
from app.application.use_cases.gateway.create_gateway_use_case import (
    CreateGatewayUseCase,
)
from app.application.use_cases.gateway.get_gateway_use_case import (
    GetGatewayUseCase,
)
from app.application.use_cases.gateway.get_gateways_use_case import (
    GetGatewaysUseCase,
)
from app.application.use_cases.gateway.ingest_gateway_telemetry_use_case import (
    IngestGatewayTelemetryUseCase,
)
from app.application.use_cases.telemetry.create_telemetry_use_case import (
    CreateTelemetryUseCase,
)
from app.application.use_cases.telemetry.downsample_telemetry_use_case import (
    DownsampleTelemetryUseCase,
)
from app.application.use_cases.telemetry.get_telemetry_use_case import (
    GetTelemetryUseCase,
)
from app.application.use_cases.telemetry.list_telemetry_use_case import (
    ListTelemetryUseCase,
)
from app.application.use_cases.user.authenticate_user_use_case import (
    AuthenticateUserUseCase,
)
from app.application.use_cases.user.create_user_use_case import (
    CreateUserUseCase,
)
from app.core.database import get_db
from app.core.mongo import get_mongo_db


class Container(containers.DeclarativeContainer):
    db = providers.Resource(get_db)
    mongo_db = providers.Singleton(get_mongo_db)

    cattle_repository = providers.Factory(CattleRepository, db=db)
    cattle_data_repository = providers.Factory(
        CattleDataRepository,
        db=mongo_db,
    )
    user_repository = providers.Factory(UserRepository, db=db)
    company_repository = providers.Factory(CompanyRepository, db=db)
    device_repository = providers.Factory(DeviceRepository, db=db)
    gateway_repository = providers.Factory(GatewayRepository, db=db)

    address_lookup_gateway = providers.Singleton(build_address_lookup_gateway)

    create_cattle_use_case = providers.Factory(
        CreateCattleUseCase,
        repository=cattle_repository,
    )
    get_cattle_use_case = providers.Factory(
        GetCattleUseCase,
        repository=cattle_repository,
    )
    list_cattles_use_case = providers.Factory(
        ListCattlesUseCase,
        repository=cattle_repository,
    )
    update_cattle_use_case = providers.Factory(
        UpdateCattleUseCase,
        repository=cattle_repository,
    )

    create_telemetry_use_case = providers.Factory(
        CreateTelemetryUseCase,
        repository=cattle_data_repository,
        cattle_repository=cattle_repository,
    )
    get_telemetry_use_case = providers.Factory(
        GetTelemetryUseCase,
        repository=cattle_data_repository,
    )
    list_telemetry_use_case = providers.Factory(
        ListTelemetryUseCase,
        repository=cattle_data_repository,
    )
    downsample_telemetry_use_case = providers.Factory(
        DownsampleTelemetryUseCase,
        repository=cattle_data_repository,
    )

    create_device_use_case = providers.Factory(
        CreateDeviceUseCase,
        repository=device_repository,
    )
    get_device_use_case = providers.Factory(
        GetDeviceUseCase,
        repository=device_repository,
    )
    get_devices_use_case = providers.Factory(
        GetDevicesUseCase,
        repository=device_repository,
    )

    create_gateway_use_case = providers.Factory(
        CreateGatewayUseCase,
        repository=gateway_repository,
    )
    get_gateway_use_case = providers.Factory(
        GetGatewayUseCase,
        repository=gateway_repository,
    )
    get_gateways_use_case = providers.Factory(
        GetGatewaysUseCase,
        repository=gateway_repository,
    )
    ingest_gateway_telemetry_use_case = providers.Factory(
        IngestGatewayTelemetryUseCase,
        gateway_repository=gateway_repository,
        cattle_repository=cattle_repository,
        device_repository=device_repository,
        cattle_data_repository=cattle_data_repository,
    )

    create_user_use_case = providers.Factory(
        CreateUserUseCase,
        repository=user_repository,
    )
    authenticate_user_use_case = providers.Factory(
        AuthenticateUserUseCase,
        repository=user_repository,
    )

    create_company_use_case = providers.Factory(
        CreateCompanyUseCase,
        repository=company_repository,
    )
    get_company_use_case = providers.Factory(
        GetCompanyUseCase,
        repository=company_repository,
    )
    list_companies_use_case = providers.Factory(
        ListCompaniesUseCase,
        repository=company_repository,
    )
    lookup_address_use_case = providers.Factory(
        LookupAddressUseCase,
        gateway=address_lookup_gateway,
    )


container: Container = Container()
