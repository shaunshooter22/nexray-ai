# ============================================================
# NexRay AI - Report Routes
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.database import get_db
from app.models import PatientSession, Report, Doctor
from app.services.report_generator import generate_report
from app.routes.auth import get_current_doctor
from app.services.auth import verify_token
import os
import json

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

class ReportRequest(BaseModel):
    session_id: int

@router.post("/generate")
async def generate_session_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    session = db.query(PatientSession).filter(PatientSession.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found")

    xray_findings = None
    if session.xray_findings:
        try:
            xray_findings = json.loads(session.xray_findings)
        except:
            try:
                xray_findings = {
                    "body_region": session.xray_region,
                    "findings": eval(session.xray_findings),
                    "overall_impression": f"X-ray analysis completed for {session.xray_region} region"
                }
            except:
                xray_findings = None

    symptom_findings = None
    if session.symptom_findings:
        try:
            symptom_findings = json.loads(session.symptom_findings)
        except:
            try:
                symptom_findings = eval(session.symptom_findings)
            except:
                symptom_findings = None

    refined_diagnosis = None
    if session.refined_findings:
        try:
            refined_diagnosis = json.loads(session.refined_findings)
        except:
            refined_diagnosis = None

    report_path = generate_report(
        session_id=request.session_id,
        patient_name=session.patient_name,
        xray_findings=xray_findings,
        symptom_findings=symptom_findings,
        refined_diagnosis=refined_diagnosis
    )

    report = Report(
        session_id=request.session_id,
        report_path=report_path
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "session_id": request.session_id,
        "report_path": report_path,
        "message": "Report generated successfully. Use the download endpoint to get the PDF."
    }

@router.get("/list")
async def list_reports(
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    result = []
    for r in reports:
        session = db.query(PatientSession).filter(PatientSession.id == r.session_id).first()
        if session:
            if session.xray_findings and session.symptom_findings:
                analysis_type = "Combined Case"
            elif session.xray_findings:
                analysis_type = "X-Ray Analysis"
            elif session.symptom_findings:
                analysis_type = "Symptom Check"
            else:
                analysis_type = "Analysis"
            patient_name = session.patient_name
        else:
            analysis_type = "Analysis"
            patient_name = None

        result.append({
            "id": r.id,
            "session_id": r.session_id,
            "patient_name": patient_name,
            "analysis_type": analysis_type,
            "report_path": r.report_path,
            "created_at": r.created_at,
        })
    return result

@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    xray_count = db.query(PatientSession).filter(
        PatientSession.xray_findings != None,
        PatientSession.created_at >= week_ago
    ).count()

    symptom_count = db.query(PatientSession).filter(
        PatientSession.symptom_findings != None,
        PatientSession.created_at >= week_ago
    ).count()

    report_count = db.query(Report).count()

    activity = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0)
        day_end = day.replace(hour=23, minute=59, second=59)
        day_xray = db.query(PatientSession).filter(
            PatientSession.xray_findings != None,
            PatientSession.created_at >= day_start,
            PatientSession.created_at <= day_end
        ).count()
        day_symptom = db.query(PatientSession).filter(
            PatientSession.symptom_findings != None,
            PatientSession.created_at >= day_start,
            PatientSession.created_at <= day_end
        ).count()
        activity.append({
            "day": day.strftime("%a"),
            "analyses": day_xray,
            "symptoms": day_symptom,
        })

    return {
        "xray_count": xray_count,
        "symptom_count": symptom_count,
        "report_count": report_count,
        "activity": activity,
    }

@router.get("/download/{report_id}")
async def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    token: str = Query(None),
):
    # Verify token from query parameter
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    if not os.path.exists(report.report_path):
        raise HTTPException(status_code=404, detail="Report file not found on server")

    session = db.query(PatientSession).filter(PatientSession.id == report.session_id).first()
    patient = session.patient_name if session and session.patient_name else f"session_{report.session_id}"
    clean_name = patient.replace(" ", "_").lower()
    formatted_date = report.created_at.strftime("%d%b%Y") if report.created_at else ""

    return FileResponse(
        path=report.report_path,
        media_type="application/pdf",
        filename=f"nexray_{clean_name}_{formatted_date}.pdf"
    )