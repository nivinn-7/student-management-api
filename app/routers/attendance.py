from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db, get_current_student

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("/check-in", response_model=schemas.AttendanceRead)
def check_in(
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(get_current_student),
):
    today = date.today()

    existing = db.query(models.Attendance).filter(
        models.Attendance.student_id == current_student.id,
        models.Attendance.date == today,
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked in today",
        )

    attendance = models.Attendance(
        student_id=current_student.id,
        date=today,
        check_in_time=datetime.today(),
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return attendance

@router.post("/check-out", response_model=schemas.AttendanceRead)
def check_out(
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(get_current_student),
):
    today = date.today()

    attendance = db.query(models.Attendance).filter(
        models.Attendance.student_id == current_student.id,
        models.Attendance.date == today,
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

    attendance.check_out_time = datetime.today()

    db.commit()
    db.refresh(attendance)

    return attendance

