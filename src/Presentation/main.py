from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.Infrastructure.Persistence.database import build_engine, build_session_factory
from src.Presentation.ExceptionHandlers import register_exception_handlers
from src.Presentation.Routers.business import (
    auth_router,
    bookings_router,
    business_router,
    services_router,
    users_router,
)
from src.Presentation.Routers.client import (
    bookings_router as client_bookings_router,
    business_router as client_business_router,
    services_router as client_services_router,
)
from src.Settings.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización de dependencias globales al arrancar la app
    settings = Settings()
    engine = build_engine(settings.DATABASE_URL)
    app.state.session_factory = build_session_factory(engine)
    
    yield
    
    # Limpieza al apagar la app
    await engine.dispose()


app = FastAPI(title="Atlas B2B API", version="1.0.0", lifespan=lifespan)

# CORS (configurable en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handlers de excepciones
register_exception_handlers(app)

# ─── Business API Routers ───
app.include_router(auth_router, prefix="/api/v1/business/auth", tags=["Auth"])
app.include_router(business_router, prefix="/api/v1/business", tags=["Business"])
app.include_router(users_router, prefix="/api/v1/business/me/users", tags=["Business Users"])
app.include_router(services_router, prefix="/api/v1/business/me/services", tags=["Business Services"])
app.include_router(bookings_router, prefix="/api/v1/business/me/bookings", tags=["Business Bookings"])

# ─── Client API Routers ───
app.include_router(client_business_router, prefix="/api/v1/client", tags=["Client - Business"])
app.include_router(client_services_router, prefix="/api/v1/client", tags=["Client - Services"])
app.include_router(client_bookings_router, prefix="/api/v1/client", tags=["Client - Bookings"])
