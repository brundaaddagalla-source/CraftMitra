import sys
from pathlib import Path

# Make `backend/` importable as the root for `app.*` imports,
# even when the process is launched from the project root.
_BACKEND_DIR = Path(__file__).resolve().parent.parent  # .../CraftMitra/backend
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# The `ai` package (voice_catalog, image_enhancement, product_ai, ...)
# lives as a sibling of `backend/`, not inside it - e.g.
# ai_product_pipeline_service.py does `from ai.voice_catalog...`.
# Add the project root too, so that import resolves no matter which
# directory uvicorn was launched from.
_PROJECT_ROOT = _BACKEND_DIR.parent  # .../CraftMitra
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.database import engine

from app.routers import auth
from app.routers import users
from app.routers import artisans
from app.routers import buyers
from app.routers import products
from app.routers import product_images
from app.routers import price_predictions
from app.routers import orders
from app.routers import ai


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)


# -----------------------------------------
# CORS CONFIGURATION
# -----------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------
# CORE / HEALTH ENDPOINTS
# -----------------------------------------

@app.get("/")
def root():
    return {
        "message": "CraftMitra Backend is Running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/db-health")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "database": "connected",
        "status": "healthy"
    }


# -----------------------------------------
# API ROUTERS
# -----------------------------------------

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(artisans.router)
app.include_router(buyers.router)
app.include_router(products.router)
app.include_router(product_images.router)
app.include_router(price_predictions.router)
app.include_router(orders.router)
app.include_router(ai.router)