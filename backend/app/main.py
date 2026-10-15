import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.db.migrator import run_migrations
from app.db.pool import close_db_pool, init_db_pool
from app.routers import auth, dashboard, health, stream
from app.services.scheduler import run_all_collectors_once, start_scheduler, stop_scheduler

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("api")

# Rate limiter (keyed by client remote address)
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Economic Indicators Dashboard API...")
    try:
        await run_migrations()
    except Exception as e:
        logger.error(f"Migration error during startup: {e}")
    await init_db_pool()

    if settings.enable_scheduler:
        start_scheduler()
        # Warmup collection in background
        asyncio.create_task(run_all_collectors_once())

    yield
    logger.info("Shutting down API...")
    if settings.enable_scheduler:
        stop_scheduler()
    await close_db_pool()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ==========================================
# CORS MIDDLEWARE (Strict origin list)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ==========================================
# SECURITY HEADERS & LIMITS MIDDLEWARES
# ==========================================
MAX_REQUEST_SIZE = 1024 * 1024  # 1 MB


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        return JSONResponse(
            status_code=413,
            content={"error": {"code": "PAYLOAD_TOO_LARGE", "message": "Request payload exceeds 1MB limit"}},
        )
    return await call_next(request)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    if settings.app_env.lower() == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# ==========================================
# GLOBAL ERROR ENVELOPE HANDLER
# ==========================================
@app.exception_handler(StarletteHTTPException)
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: Exception):
    status_code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", "Internal server error")
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=status_code, content=detail)
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": "HTTP_ERROR" if status_code != 404 else "NOT_FOUND", "message": str(detail)}}
    )


# ==========================================
# ROUTERS
# ==========================================
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(stream.router)

