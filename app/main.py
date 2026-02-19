import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth as auth_router, attendance as attendance_router, college as college_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Auth Backend", version="1.0.0")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(attendance_router.router)
app.include_router(college_router.router)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}

