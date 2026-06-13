from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from scalar_fastapi import Layout, Theme, get_scalar_api_reference


def register_documentation(app: FastAPI) -> None:
    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
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
