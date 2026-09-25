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


# Allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://bbdians.onrender.com",
],

    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Public confession routes
app.include_router(router)

# Private admin routes
app.include_router(admin_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to BBDIANS",
        "status": "Backend is working!"
    }