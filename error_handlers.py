from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

def setup_error_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def generic_error(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )