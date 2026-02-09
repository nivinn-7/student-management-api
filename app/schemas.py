from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


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
    register_number: str
    college_id: int
    course_id: int


class StudentCreate(StudentBase):
    password: str


class StudentRead(StudentBase):
    id: int
    id_card_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None


class StudentMe(BaseModel):
    id: int
    name: str
    register_number: str
    college: CollegeRead
    course: CourseRead

    model_config = ConfigDict(from_attributes=True)


class AttendanceBase(BaseModel):
    date: date
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    check_in_lat: Optional[float] = None
    check_in_lon: Optional[float] = None
    check_out_lat: Optional[float] = None
    check_out_lon: Optional[float] = None


class AttendanceRead(AttendanceBase):
    id: int
    student_id: int

    model_config = ConfigDict(from_attributes=True)


class AttendanceCheckInRequest(BaseModel):
    latitude: float
    longitude: float


class AttendanceCheckOutRequest(BaseModel):
    latitude: float
    longitude: float


class AttendanceList(BaseModel):
    items: List[AttendanceRead]

from pydantic import BaseModel, EmailStr
from datetime import date, datetime

class CollegeResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class StudentCreate(BaseModel):
    name: str
    register_number: str
    college_id: int
    course_id: int
    password: str

class StudentLogin(BaseModel):
    register_number: str
    password: str

class AttendanceResponse(BaseModel):
    date: date
    check_in_time: datetime | None
    check_out_time: datetime | None

    class Config:
        from_attributes = True
