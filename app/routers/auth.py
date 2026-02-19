import os
from pathlib import Path

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_password_hash, verify_password, create_access_token
from ..dependencies import get_db, get_current_student

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str

UPLOAD_ROOT = os.getenv("UPLOAD_ROOT", "uploads")
ID_CARDS_DIR = Path(UPLOAD_ROOT) / "id_cards"
ID_CARDS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/signup", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED)
async def signup_student(
    name: str = Form(...),
    register_number: str = Form(...),
    college_id: int = Form(...),
    course_id: int = Form(...),
    password: str = Form(...),
    id_card: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    existing = (
        db.query(models.Student)
        .filter(models.Student.register_number == register_number)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Register number already registered",
        )
    
    college = db.query(models.College).filter(models.College.id == college_id).first()
    if not college:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="College not found",
        )
    
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course not found",
        )
    
    if course.college_id != college.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course does not belong to the specified college",
        )

    ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/jpg"]
    ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
    if id_card.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG are allowed.",
        )
    
    ext = id_card.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Only .jpg, .jpeg and .png are allowed.",
        )
    
    safe_filename = f"{register_number}_{uuid.uuid4().hex}.{ext}"
    file_path = ID_CARDS_DIR / safe_filename

    content = await id_card.read()

    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 5MB limit.",
        )

    with file_path.open("wb") as f:
        f.write(content)

    hashed_password = get_password_hash(password)

    student = models.Student(
        name=name,
        register_number=register_number,
        college_id=college_id,
        course_id=course_id,
        id_card_path=str(file_path),
        hashed_password=hashed_password,
    )
    try:
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    except Exception as e:
        db.rollback()
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    student = (
        db.query(models.Student)
        .filter(models.Student.register_number == form_data.username)
        .first()
    )
    if not student or not verify_password(form_data.password, student.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect register number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(student.id))

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.StudentMe)
def read_current_student(
    current_student: models.Student = Depends(get_current_student),
):
    return current_student

