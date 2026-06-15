from app.bootstrap.container import init_container
from app.bootstrap.docs import register_documentation
from app.bootstrap.health import router as health_router
from app.bootstrap.logging import init_logging
from app.bootstrap.middleware import register_middlewares
from app.bootstrap.openapi import API_DESCRIPTION, DocumentedFastAPI
from app.bootstrap.routes import register_routes


def create_app() -> DocumentedFastAPI:
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
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    init_logging()
    init_container(app)
    register_middlewares(app)
    register_documentation(app)
    app.include_router(health_router)
    register_routes(app)

    return app


app = create_app()
