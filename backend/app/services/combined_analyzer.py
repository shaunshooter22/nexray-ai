# ============================================================
# NexRay AI - Combined Analyzer
# This service handles analysis when both an X-ray image
# and symptoms are provided together. Claude analyses both
# and gives a combined assessment that is more accurate
# than either alone.
# ============================================================

import anthropic
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

COMBINED_SYSTEM_PROMPT = """
You are a medical decision-support assistant for NexRay AI, a platform used by doctors and healthcare workers in Ghana and West Africa.

You will receive either:
- An X-ray image only
- Symptoms only (as text)
- Both an X-ray image and symptoms together

Your job is to analyse whatever is provided and give the 3 most likely diagnoses with confidence percentages.

When both image and symptoms are provided, cross-reference them for a more accurate assessment. For example if the X-ray shows lung opacity AND the patient has fever and cough, pneumonia should rank higher confidence.

You must ALWAYS respond with valid JSON in exactly this format and nothing else:
{
    "analysis_basis": "X-Ray only / Symptoms only / Combined X-Ray and Symptoms",
    "body_region": "the body part shown in the x-ray if image was provided, otherwise null",
    "possible_conditions": [
        {
            "condition": "most likely condition",
            "confidence": 87,
            "description": "brief description of why this condition is likely based on the evidence provided"
        },
        {
            "condition": "second possible condition",
            "confidence": 65,
            "description": "brief description of why this condition is possible"
        },
        {
            "condition": "third possible condition",
            "confidence": 42,
            "description": "brief description of why this condition is possible"
        }
    ],
    "recommended_tests": [
        "recommended test 1",
        "recommended test 2"
    ],
    "suggested_treatment": [
        "treatment suggestion 1",
        "treatment suggestion 2"
    ],
    "next_steps": [
        "next step 1",
        "next step 2"
    ],
    "urgency": "Emergency / Urgent / Routine",
    "disclaimer": "These are AI-generated suggestions only. Clinical judgment of the attending medical professional must be applied before any action is taken.",
    "summary": "A brief summary of the overall assessment"
}

Important rules:
- Always return EXACTLY 3 possible conditions ordered from most likely to least likely
- confidence is a number between 0 and 100 — each is independent and does not need to add up to 100
- When both X-ray and symptoms are provided cross-reference them — a condition supported by both should have higher confidence
- Always prioritise conditions common in West Africa such as malaria, typhoid, TB, pneumonia
- recommended_tests should help confirm or rule out the 3 possible conditions
- Never say see a doctor — the user IS the doctor
- Urgency is Emergency if life threatening, Urgent if needs same day attention, Routine otherwise
"""

def analyze_combined(image_bytes: bytes = None, image_type: str = "image/jpeg",
                     symptoms: str = None) -> dict:
    # --------------------------------------------------------
    # Flexible analysis — accepts image only, symptoms only,
    # or both together. Claude analyses whatever is provided
    # and returns 3 possible conditions with confidence %.
    # --------------------------------------------------------

    # Build the message content based on what was provided
    content = []

    # Add image if provided
    if image_bytes:
        image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": image_type,
                "data": image_base64,
            }
        })

    # Build the text prompt based on what was provided
    if image_bytes and symptoms:
        text = f"Please analyse this X-ray image together with the following patient symptoms and provide your assessment with exactly 3 possible conditions.\n\nPatient symptoms: {symptoms}"
    elif image_bytes:
        text = "Please analyse this X-ray image and provide your radiological assessment with exactly 3 possible conditions."
    elif symptoms:
        text = f"Please analyse the following patient symptoms and provide your assessment with exactly 3 possible conditions.\n\nPatient symptoms: {symptoms}"
    else:
        return {"error": "No image or symptoms provided"}

    content.append({"type": "text", "text": text})

    # Send to Claude
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1200,
        system=COMBINED_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}]
    )

    # Extract and clean response
    response_text = message.content[0].text.strip()

    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    response_text = response_text.strip()

    start = response_text.find("{")
    end = response_text.rfind("}") + 1
    if start != -1 and end != 0:
        response_text = response_text[start:end]

    result = json.loads(response_text)
    return result