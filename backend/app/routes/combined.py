# ============================================================
# NexRay AI - Combined Route
# Accepts optional X-ray image, optional symptoms and optional
# patient name. Saves doctor_id to link session to doctor.
# Auto-generates a report for every session.
# ============================================================

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import PatientSession, Doctor, Report
from app.services.combined_analyzer import analyze_combined
from app.services.report_generator import generate_report
from app.routes.auth import get_current_doctor
import os
import json

router = APIRouter(
    prefix="/analyze",
    tags=["Combined Analysis"]
)

UPLOAD_FOLDER = "uploads"

@router.post("/")
async def combined_analysis(
    patient_name: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    if not file and not symptoms:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least an X-ray image or symptoms"
        )

    image_bytes = None
    image_type = "image/jpeg"
    file_path = None

    if file:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Uploaded file must be an image")
        image_bytes = await file.read()
        image_type = file.content_type
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(image_bytes)

    findings = analyze_combined(
        image_bytes=image_bytes,
        image_type=image_type,
        symptoms=symptoms
    )

    analysis_basis = findings.get("analysis_basis", "Unknown")
    body_region = findings.get("body_region")

    # Save session with doctor_id
    session = PatientSession(
        doctor_id=current_doctor.id,
        patient_name=patient_name,
        xray_path=file_path,
        xray_region=body_region,
        xray_findings=json.dumps(findings) if file else None,
        symptoms=symptoms,
        symptom_findings=json.dumps(findings) if not file else None
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Auto-generate report
    try:
        xray_findings = json.loads(session.xray_findings) if session.xray_findings else None
        symptom_findings = json.loads(session.symptom_findings) if session.symptom_findings else None

        report_path = generate_report(
            session_id=session.id,
            patient_name=patient_name,
            xray_findings=xray_findings,
            symptom_findings=symptom_findings
        )

        report = Report(
            session_id=session.id,
            report_path=report_path
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        report_id = report.id
    except Exception:
        report_id = None

    return {
        "session_id": session.id,
        "report_id": report_id,
        "patient_name": patient_name,
        "analysis_basis": analysis_basis,
        "body_region": body_region,
        "analysis": findings
    }