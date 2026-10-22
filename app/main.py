from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging_config import RequestIDMiddleware, logger
from app.routers import customers, orders

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Attach request-id middleware
app.add_middleware(RequestIDMiddleware)

# Standardized Error Handlers matching OpenAPI Spec
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation failed: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"code": "VALIDATION_ERROR", "message": str(exc.errors())}
    )

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"code": "NOT_FOUND", "message": getattr(exc, "detail", "Resource not found")}
    )

# Include Routers
app.include_router(customers.router)
app.include_router(orders.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "environment": settings.ENV}