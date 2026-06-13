import time

from fastapi import Request

from app.core.logger import logger


def register_middlewares(app):

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        logger.info(
            "HTTP Request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=round(duration, 3),
        )

        return response
