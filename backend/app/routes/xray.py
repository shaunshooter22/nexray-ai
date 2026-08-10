# ============================================================
# NexRay AI - X-Ray Routes
# This file contains the API route for X-ray analysis.
# It receives the uploaded image and sends it to Claude Vision
# which identifies the body region and detects conditions.
# ============================================================

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import PatientSession, Doctor
from app.services.xray_analyzer import analyze_xray
from app.routes.auth import get_current_doctor
import os
import json

router = APIRouter(
    prefix="/xray",
    tags=["X-Ray Analysis"]
)

UPLOAD_FOLDER = "uploads"

@router.post("/analyze")
async def analyze_xray_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    # --------------------------------------------------------
    # Receives an x-ray image, sends it to Claude Vision
    # for analysis, saves the session and returns findings.
    # --------------------------------------------------------

    # Check that the uploaded file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    # Read the image bytes
    image_bytes = await file.read()

    # Save the uploaded image to the uploads folder
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(image_bytes)

    # Send to Claude Vision for analysis
    findings = analyze_xray(image_bytes, image_type=file.content_type)

    # Save session to database — store full Claude Vision response as JSON
    session = PatientSession(
        xray_path=file_path,
        xray_region=findings.get("body_region", "Unknown"),
        xray_findings=json.dumps(findings)  # Store full response so report has all data
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Return results
    return {
        "session_id": session.id,
        "detected_region": findings.get("body_region"),
        "analysis": findings
    }