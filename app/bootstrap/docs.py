from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from scalar_fastapi import Layout, Theme, get_scalar_api_reference

from app.core.config import settings


def register_documentation(app: FastAPI) -> None:
    if not settings.is_docs_enabled:

        @app.get("/", include_in_schema=False)
        async def root_health() -> JSONResponse:
            return JSONResponse({"status": "ok", "service": "CowTrack API"})

        return

    @app.get("/", include_in_schema=False)
    async def root_docs() -> RedirectResponse:
        return RedirectResponse(url="/docs/scalar")

    @app.get("/docs/scalar", include_in_schema=False)
    async def scalar_documentation():
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title=f"{app.title} — API Reference",
            theme=Theme.DEEP_SPACE,
            layout=Layout.MODERN,
            dark_mode=True,
            default_open_all_tags=False,
            hide_models=False,
            show_sidebar=True,
        )
