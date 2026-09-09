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
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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