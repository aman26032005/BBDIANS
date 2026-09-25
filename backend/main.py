from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .models import Confession
from .routes import router
from .admin_routes import router as admin_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="BBDIANS",
    description="Anonymous Confession App",
    version="1.0.0"
)


# Allowed frontend origins
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://bbdians.onrender.com",
]


app.add_middleware(
    CORSMiddleware,

    allow_origins=ALLOWED_ORIGINS,

    allow_credentials=False,

    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS",
    ],

    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)


app.include_router(router)
app.include_router(admin_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to BBDIANS",
        "status": "Backend is working!"
    }