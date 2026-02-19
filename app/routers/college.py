from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db

router = APIRouter(prefix="/colleges", tags=["colleges"])

@router.get("/", response_model=list[schemas.CollegeRead])
def get_colleges(db: Session = Depends(get_db)):
    colleges = db.query(models.College).order_by(models.College.name).all()
    return colleges

@router.get("/{college_id}/courses", response_model=list[schemas.CourseRead])
def get_courses_by_college(college_id: int, db: Session = Depends(get_db)):
    courses = db.query(models.Course).filter(models.Course.college_id == college_id).order_by(models.Course.name).all()
    return courses