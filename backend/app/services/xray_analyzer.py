# ============================================================
# NexRay AI - X-Ray Analyzer (Claude Vision)
# This service takes any x-ray image and sends it to Claude
# API which analyses it like a radiologist — identifying the
# body region, detecting conditions, and suggesting findings.
# No separate classifier or specialist models needed.
# ============================================================

import anthropic
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

# System prompt for X-ray analysis
XRAY_SYSTEM_PROMPT = """
You are an AI radiology assistant for NexRay AI, a medical platform used by doctors and healthcare workers in Ghana and West Africa.

Your job is to analyse X-ray images and provide structured findings.

You must ALWAYS respond with valid JSON in exactly this format and nothing else:
{
    "body_region": "the body part shown in the x-ray (e.g. Chest, Left Hand, Lumbar Spine, Knee, Pelvis etc.)",
    "findings": [
        {
            "condition": "most likely condition",
            "confidence": 87,
            "description": "brief description of why you think this"
        },
        {
            "condition": "second possible condition",
            "confidence": 65,
            "description": "brief description of why you think this"
        },
        {
            "condition": "third possible condition",
            "confidence": 42,
            "description": "brief description of why you think this"
        }
    ],
    "overall_impression": "overall radiological impression in one or two sentences",
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
    "disclaimer": "These are AI-generated radiological suggestions only. A qualified radiologist or clinician must review and confirm findings before any clinical action is taken."
}

Important rules:
- Identify the body region accurately from the image
- Always return EXACTLY 3 findings ordered from most likely to least likely
- confidence is a number between 0 and 100 representing how certain you are about that specific condition independently
- Each confidence is independent — they do not need to add up to 100
- Always include a description for each finding explaining what you see
- recommended_tests should include any tests or investigations needed to confirm the diagnosis
- suggested_treatment should be practical treatment options for the detected conditions
- next_steps should be what the doctor should do next clinically
- Never say you cannot analyse X-rays — always provide your best radiological assessment
- Urgency is Emergency if life threatening findings, Urgent if needs prompt attention, Routine otherwise
"""

def analyze_xray(image_bytes: bytes, image_type: str = "image/jpeg") -> dict:
    # --------------------------------------------------------
    # Takes raw x-ray image bytes, sends it to Claude Vision
    # and returns a structured dictionary 

    # Convert image bytes to base64 for Claude API
    image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    # Send to Claude Vision
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1200,
        system=XRAY_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_type,
                            "data": image_base64,
                        }
                    },
                    {
                        "type": "text",
                        "text": "Please analyse this X-ray image and provide your radiological assessment with exactly 3 possible conditions."
                    }
                ]
            }
        ]
    )

    # Extract response text
    response_text = message.content[0].text.strip()

    # Clean markdown if present
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    response_text = response_text.strip()

    # Extract JSON
    start = response_text.find("{")
    end = response_text.rfind("}") + 1
    if start != -1 and end != 0:
        response_text = response_text[start:end]

    # Parse and return
    result = json.loads(response_text)
    return result