from dependency_injector import containers, providers

from app.adapters.repositories.cattle_repository import CattleRepository
from app.adapters.repositories.company_repository import CompanyRepository
from app.adapters.repositories.device_repository import DeviceRepository
from app.adapters.repositories.user_repository import UserRepository
from app.application.use_cases.cattle.create_cattle_use_case import (
    CreateCattleUseCase,
)
from app.application.use_cases.cattle.get_cattle_use_case import (
    GetCattleUseCase,
)
from app.application.use_cases.cattle.get_cattles_use_case import (
    GetCattlesUseCase,
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
from app.application.use_cases.device.ingest_telemetry_use_case import (
    IngestTelemetryUseCase,
)
from app.application.use_cases.user.authenticate_user_use_case import (
    AuthenticateUserUseCase,
)
from app.application.use_cases.user.create_user_use_case import (
    CreateUserUseCase,
)


class Container(containers.DeclarativeContainer):

    cattle_repository = providers.Factory(CattleRepository)
    user_repository = providers.Factory(UserRepository)
    company_repository = providers.Factory(CompanyRepository)
    device_repository = providers.Factory(DeviceRepository)

    create_cattle_use_case = providers.Factory(
        CreateCattleUseCase, repository=cattle_repository
    )
    get_cattle_use_case = providers.Factory(
        GetCattleUseCase, repository=cattle_repository
    )
    get_cattles_use_case = providers.Factory(
        GetCattlesUseCase, repository=cattle_repository
    )

    create_device_use_case = providers.Factory(
        CreateDeviceUseCase, repository=device_repository
    )
    get_device_use_case = providers.Factory(
        GetDeviceUseCase, repository=device_repository
    )
    get_devices_use_case = providers.Factory(
        GetDevicesUseCase, repository=device_repository
    )
    ingest_telemetry_use_case = providers.Factory(
        IngestTelemetryUseCase,
        device_repository=device_repository,
        cattle_repository=cattle_repository,
    )

    create_user_use_case = providers.Factory(
        CreateUserUseCase, repository=user_repository
    )
    authenticate_user_use_case = providers.Factory(
        AuthenticateUserUseCase, repository=user_repository
    )

    create_company_use_case = providers.Factory(
        CreateCompanyUseCase, repository=company_repository
    )
    get_company_use_case = providers.Factory(
        GetCompanyUseCase, repository=company_repository
    )
    list_companies_use_case = providers.Factory(
        ListCompaniesUseCase, repository=company_repository
    )


container = Container()
