# ============================================================
# NexRay AI - Symptom Routes
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import PatientSession, Doctor
from app.services.symptom_checker import check_symptoms
from app.routes.auth import get_current_doctor
import json

router = APIRouter(
    prefix="/symptoms",
    tags=["Symptom Checker"]
)

class SymptomRequest(BaseModel):
    symptoms: str
    patient_name: Optional[str] = None  # Patient name

@router.post("/analyze")
async def analyze_symptoms(
    request: SymptomRequest,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    if not request.symptoms.strip():
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty")

    findings = check_symptoms(request.symptoms)

    session = PatientSession(
        patient_name=request.patient_name,
        symptoms=request.symptoms,
        symptom_findings=json.dumps(findings)
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "patient_name": request.patient_name,
        "symptoms": request.symptoms,
        "analysis": findings
    }