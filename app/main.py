from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth as auth_router, attendance as attendance_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Auth Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(attendance_router.router)

@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok"}

