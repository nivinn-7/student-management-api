from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, EmailStr
from .models import CollegeType

class CollegeBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    district: Optional[str] = None
    remarks: Optional[str] = None

class CollegeCreate(CollegeBase):
    pass

class CollegeRead(CollegeBase):
    id: int
    college_type: CollegeType

    model_config = ConfigDict(from_attributes=True)


class CourseBase(BaseModel):
    name: str
    duration: int

class CourseCreate(CourseBase):
    pass

class CourseRead(CourseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    register_number: str
    college_id: int
    course_id: int

class StudentCreate(StudentBase):
    password: str = Field(..., min_length=6)

class StudentRead(StudentBase):
    id: int
    id_card_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class StudentLogin(BaseModel):
    email: EmailStr
    password: str

class StudentMe(BaseModel):
    id: int
    name: str
    email: EmailStr
    register_number: str
    college: CollegeRead
    course: CourseRead

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None


class AttendanceRead(BaseModel):
    id: int
    date: date
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AttendanceLocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
