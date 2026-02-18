import enum
from sqlalchemy import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base

class CollegeType(enum.Enum):
    ENGINEERING = "Engineering"
    DEGREE = "Degree"
    OTHERS = "Others"

class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    district = Column(String(255), nullable=True)
    college_type = Column(Enum(CollegeType, name = "collegetype"), nullable=False)
    department_count = Column(Integer, nullable=True)
    remarks = Column(String(512), nullable=True)

    students = relationship("Student", back_populates="college")
    courses = relationship("Course", back_populates="college")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    duration = Column(Integer, nullable=False)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False, index=True)

    students = relationship("Student", back_populates="course")
    college = relationship("College", back_populates="courses")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    register_number = Column(String(100), unique=True, index=True, nullable=False)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    id_card_path = Column(String(1024), nullable=True)
    hashed_password = Column(String(255), nullable=False)

    college = relationship("College", back_populates="students")
    course = relationship("Course", back_populates="students")
    attendance_records = relationship(
        "Attendance", back_populates="student", cascade="all, delete-orphan"
    )


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("student_id", "date", name="uq_attendance_student_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    check_in_time = Column(DateTime(timezone=True), nullable=True)
    check_out_time = Column(DateTime(timezone=True), nullable=True)
    check_in_lat = Column(Float, nullable=True)
    check_in_lon = Column(Float, nullable=True)
    check_out_lat = Column(Float, nullable=True)
    check_out_lon = Column(Float, nullable=True)

    student = relationship("Student", back_populates="attendance_records")