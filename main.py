import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import achievements, missions, mission_users, users

app = FastAPI()

allowed_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8100").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(achievements.router)
app.include_router(missions.router)
app.include_router(users.router)
app.include_router(mission_users.router)
