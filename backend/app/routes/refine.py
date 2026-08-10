# ============================================================
# NexRay AI - Refine Routes
# The doctor types their test results in plain English.
# Claude analyses the results and narrows down the diagnosis.
# The refined diagnosis is saved to the database automatically.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import PatientSession, Doctor
from app.services.refine_analyzer import refine_diagnosis
from app.routes.auth import get_current_doctor
import json

router = APIRouter(
    prefix="/refine",
    tags=["Refine Diagnosis"]
)

class RefineRequest(BaseModel):
    session_id: int        # The original session ID
    test_results: str      # The doctor's test results in plain English — no specific format needed
    analysis_type: str     # "xray" or "symptoms"

@router.post("/diagnosis")
async def refine_session_diagnosis(
    request: RefineRequest,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    # --------------------------------------------------------
    # The doctor types their test results in plain English.
    # Claude reads them and narrows down the diagnosis.
    # The refined diagnosis is saved to the database so the
    # report generator can fetch it automatically.
    # --------------------------------------------------------

    # Validate analysis type
    if request.analysis_type not in ["xray", "symptoms"]:
        raise HTTPException(status_code=400, detail="analysis_type must be 'xray' or 'symptoms'")

    # Fetch the original session
    session = db.query(PatientSession).filter(PatientSession.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found")

    # Get the original findings
    original_findings = []

    if request.analysis_type == "xray":
        if not session.xray_findings:
            raise HTTPException(status_code=400, detail="No X-ray findings found for this session")
        try:
            xray_data = json.loads(session.xray_findings)
            original_findings = xray_data.get("findings", xray_data.get("possible_conditions", []))
        except:
            raise HTTPException(status_code=400, detail="Could not parse X-ray findings")

    elif request.analysis_type == "symptoms":
        if not session.symptom_findings:
            raise HTTPException(status_code=400, detail="No symptom findings found for this session")
        try:
            symptom_data = json.loads(session.symptom_findings)
            original_findings = symptom_data.get("possible_conditions", [])
        except:
            raise HTTPException(status_code=400, detail="Could not parse symptom findings")

    if not original_findings:
        raise HTTPException(status_code=400, detail="No original findings to refine")

    # Send to Claude for refinement
    refined = refine_diagnosis(
        original_findings=original_findings,
        test_results=request.test_results,
        analysis_type=request.analysis_type
    )

    # Save refined diagnosis to database automatically
    session.refined_findings = json.dumps(refined)
    db.commit()
    db.refresh(session)

    return {
        "session_id": request.session_id,
        "analysis_type": request.analysis_type,
        "message": "Diagnosis refined successfully. Generate a report for this session to see the full results.",
        "refined_diagnosis": refined
    }