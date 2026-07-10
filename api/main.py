# api/main.py
"""FastAPI application entry point – minimal version for authentication."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from configs.settings import settings
from utils.logger import setup_logging
from core.exceptions import AppException
from fastapi.responses import JSONResponse

# Import only the routers we need
from api.routers import auth, health, predict

# Setup logging (this uses a simple config – you can keep it)
setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Human Behavior Intelligence Platform API (Authentication only)",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(predict.router, prefix="/api/v1/predict", tags=["Prediction"])

# Global exception handler for our custom exceptions
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

# Root endpoint
@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}

# Custom OpenAPI schema (adds Bearer auth security)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi