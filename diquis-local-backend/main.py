import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.logger import custom_logger as logger
from app.api.dependencies import get_db
from app.api.endpoints import auth, users, categories, transactions, accounts, scheduled, analytics
from app.core.config import settings
from app.core.limiter import limiter
from app.services.scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida: arranca scheduler al iniciar, lo para al cerrar."""
    logger.info("🚀 Iniciando aplicación...")
    start_scheduler()
    yield
    logger.info("🛑 Cerrando aplicación...")
    stop_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME, 
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = settings.BACKEND_CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Autenticación"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Usuarios"])
app.include_router(categories.router, prefix=f"{settings.API_V1_STR}/categories", tags=["Categorías"])
app.include_router(transactions.router, prefix=f"{settings.API_V1_STR}/transactions", tags=["Transacciones"])
app.include_router(accounts.router, prefix=f"{settings.API_V1_STR}/accounts", tags=["Cuentas"])
app.include_router(scheduled.router, prefix=f"{settings.API_V1_STR}/scheduled", tags=["Programados"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analítica y Proyecciones"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "Desconocida")
    
    query_params = request.url.query
    query_text = f"?{query_params}" if query_params else ""
    
    logger.info(f"➡️ IN: {request.method} {request.url.path}{query_text} | IP: {client_ip}")
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    
    if response.status_code >= 500:
        logger.error(f"❌ OUT: {request.method} {request.url.path} - Estado: {response.status_code} - Tiempo: {formatted_process_time}ms")
    elif response.status_code >= 400:
        logger.warning(f"⚠️ OUT: {request.method} {request.url.path} - Estado: {response.status_code} - Tiempo: {formatted_process_time}ms")
    else:
        logger.info(f"✅ OUT: {request.method} {request.url.path} - Estado: {response.status_code} - Tiempo: {formatted_process_time}ms")
    
    return response

@app.get("/")
def read_root():
    logger.debug("Ping recibido en la raíz.")
    return {"mensaje": f"¡{settings.PROJECT_NAME} activo y monitoreado en entorno: {settings.ENVIRONMENT}!"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        logger.info("Health Check: Exitoso")
        return {
            "api_status": "ok", 
            "environment": settings.ENVIRONMENT,
            "database_status": "conectada 🚀",
            "mensaje": "¡PostgreSQL y FastAPI están hablando a la perfección!"
        }
    except Exception as e:
        logger.error(f"Fallo crítico al conectar con la Base de Datos: {e}")
        raise HTTPException(status_code=500, detail="Error conectando a la base de datos")