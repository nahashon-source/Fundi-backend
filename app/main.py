"""
FastAPI application entry point.

Responsible only for: creating the app, registering middleware,
mounting routers, and wiring global exception handlers.
No business logic lives here.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.exceptions import (
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ValidationException,
    ConflictException,
)
from app.api.auth import router as auth_router
from app.api.fundis import router as fundis_router
from app.api.categories import router as categories_router
from app.api.jobs import router as jobs_router
from app.api.invoices import router as invoices_router

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Centralized exception handlers ---
# Each maps a custom exception to the correct HTTP status, while keeping
# the {success, message, errors} envelope consistent across every error.

@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException) -> JSONResponse:
    return JSONResponse(status_code=404, content={"success": False, "message": exc.message, "errors": None})


@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(request: Request, exc: UnauthorizedException) -> JSONResponse:
    return JSONResponse(status_code=401, content={"success": False, "message": exc.message, "errors": None})


@app.exception_handler(ForbiddenException)
async def forbidden_handler(request: Request, exc: ForbiddenException) -> JSONResponse:
    return JSONResponse(status_code=403, content={"success": False, "message": exc.message, "errors": None})


@app.exception_handler(ValidationException)
async def validation_handler(request: Request, exc: ValidationException) -> JSONResponse:
    return JSONResponse(status_code=422, content={"success": False, "message": exc.message, "errors": None})


@app.exception_handler(ConflictException)
async def conflict_handler(request: Request, exc: ConflictException) -> JSONResponse:
    return JSONResponse(status_code=409, content={"success": False, "message": exc.message, "errors": None})


@app.get("/health")
def health_check() -> dict:
    """Basic liveness check - confirms the API process is up and responding."""
    return {"success": True, "message": "FundiHub API is running", "data": None}

app.include_router(invoices_router, prefix="/invoices", tags=["invoices"])
app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
app.include_router(categories_router, prefix="/categories", tags=["categories"])
app.include_router(fundis_router, prefix="/fundis", tags=["fundis"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])