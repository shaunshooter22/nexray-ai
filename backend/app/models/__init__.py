# ============================================================
# NexRay AI - Database Models
# ============================================================

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class PatientSession(Base):
    __tablename__ = "patient_sessions"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, nullable=True)  # Patient name added by doctor
    xray_path = Column(String, nullable=True)
    xray_region = Column(String, nullable=True)
    xray_findings = Column(Text, nullable=True)
    symptoms = Column(Text, nullable=True)
    symptom_findings = Column(Text, nullable=True)
    refined_findings = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False)
    report_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    licence_number = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())