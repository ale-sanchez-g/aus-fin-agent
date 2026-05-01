from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.core.logging import configure_logging
from app.api.routes import health, products, discovery, reports, providers, auth

configure_logging()
log = structlog.get_logger()


def _log_aws_connectivity() -> None:
    try:
        import boto3

        identity = boto3.client("sts", region_name=settings.AWS_REGION).get_caller_identity()
        log.info(
            "aws_identity_verified",
            account=identity.get("Account"),
            arn=identity.get("Arn"),
            region=settings.AWS_REGION,
        )
    except Exception as exc:
        log.warning("aws_identity_verification_failed", error=str(exc), region=settings.AWS_REGION)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("startup", environment=settings.ENVIRONMENT)
    _log_aws_connectivity()
    yield
    log.info("shutdown")


app = FastAPI(
    title="AUS Fin Agent API",
    description="Australian open banking product discovery platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(discovery.router, prefix="/api/v1/discovery", tags=["discovery"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(providers.router, prefix="/api/v1/providers", tags=["providers"])


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
