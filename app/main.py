from app.adapters.models import Gateway as _Gateway  # noqa: F401
from app.bootstrap.admin import register_admin
from app.bootstrap.container import init_container
from app.bootstrap.docs import register_documentation
from app.bootstrap.health import router as health_router
from app.bootstrap.logging import init_logging
from app.bootstrap.middleware import register_middlewares
from app.bootstrap.openapi import API_DESCRIPTION, DocumentedFastAPI
from app.bootstrap.routes import register_routes
from app.core.config import settings

# Ensure all ORM mappers (incl. Gateway) are registered at startup.
_ = _Gateway


def create_app() -> DocumentedFastAPI:
    docs_enabled = settings.is_docs_enabled

    app = DocumentedFastAPI(
        title="CowTrack API",
        description=API_DESCRIPTION,
        version="1.0.0",
        contact={
            "name": "CowTrack Team",
            "email": "vitormateusmiolo@gmail.com",
        },
        license_info={
            "name": "Proprietary",
        },
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )

    init_logging()
    init_container(app)
    register_middlewares(app)
    register_documentation(app)
    app.include_router(health_router)
    register_routes(app)
    register_admin(app)

    return app


app = create_app()
