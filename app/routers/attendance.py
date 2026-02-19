import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from math import radians, cos, sin, sqrt, atan2

from .. import models, schemas
from ..dependencies import get_db, get_current_student

router = APIRouter(prefix="/attendance", tags=["attendance"])

ALLOWED_DISTANCE_METERS = int(os.getenv("ALLOWED_DISTANCE_METERS", "200"))

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def validate_location(latitude: float, longitude: float, college: models.College):
    distance = calculate_distance(
        latitude,
        longitude,
        college.latitude,
        college.longitude
    )

    if distance > ALLOWED_DISTANCE_METERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are outside the allowed campus radius",
        )

@router.post("/check-in", response_model=schemas.AttendanceRead)
def check_in(
    payload: schemas.AttendanceLocationRequest,
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(get_current_student),
):
    now = datetime.now(timezone.utc)
    
    college = db.get(models.College, current_student.college_id)
    if not college:
        raise HTTPException(
        status_code=404,
        detail="College not found",
        )
    validate_location(payload.latitude, payload.longitude, college)

    attendance = models.Attendance(
        student_id=current_student.id,
        date=now.date(),
        check_in_time=now,
        check_in_lat=payload.latitude,
        check_in_lon=payload.longitude
    )

    try:
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked in today",
        )
    return attendance

@router.post("/check-out", response_model=schemas.AttendanceRead)
def check_out(
    payload: schemas.AttendanceLocationRequest,
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(get_current_student),
):
    now = datetime.now(timezone.utc)

    attendance = db.query(models.Attendance).filter_by(
        student_id = current_student.id,
        date = now.date(),
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not checked in today",
        )

    if attendance.check_out_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked out",
        )
    
    college = db.get(models.College, current_student.college_id)
    if not college:
        raise HTTPException(
        status_code=404,
        detail="College not found",
        )
    validate_location(payload.latitude, payload.longitude, college)

    attendance.check_out_time = now
    attendance.check_out_lat = payload.latitude
    attendance.check_out_lon = payload.longitude

    try:
        db.commit()
        db.refresh(attendance)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to check out",
        )
    
    return attendance

@router.get("/my", response_model=list[schemas.AttendanceRead])
def get_my_attendance(
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(get_current_student),
):
    records = (
        db.query(models.Attendance)
        .filter(models.Attendance.student_id == current_student.id)
        .order_by(models.Attendance.date.desc())
        .all()
    )
    return records

@router.get("/today")
def get_today_status(
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(get_current_student),
):
    today = datetime.now(timezone.utc).date()

    attendance = (
        db.query(models.Attendance)
        .filter(
            models.Attendance.student_id == current_student.id,
            models.Attendance.date == today,
        )
        .first()
    )

    if not attendance:
        return {"checked_in": False, "checked_out": False}

    return {
        "checked_in": attendance.check_in_time is not None,
        "checked_out": attendance.check_out_time is not None,
    }