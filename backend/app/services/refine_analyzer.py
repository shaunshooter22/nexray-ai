# ============================================================
# NexRay AI - Refine Analyzer
# This service takes the original findings (xray or symptoms)
# and the doctor's test results and asks Claude to narrow
# down the diagnosis to a confirmed assessment.
# ============================================================

import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

REFINE_SYSTEM_PROMPT = """
You are a medical decision-support assistant for NexRay AI, a platform used by doctors and healthcare workers in Ghana and West Africa.

A doctor has already performed an initial analysis and received 3 possible conditions with confidence percentages. They have now carried out the recommended tests and have the results. Your job is to use the original findings AND the test results to narrow down to a confirmed diagnosis.

You must ALWAYS respond with valid JSON in exactly this format and nothing else:
{
    "confirmed_conditions": [
        {
            "condition": "confirmed condition name",
            "status": "Confirmed / Also Present / Suspected",
            "evidence": "brief explanation of why this is confirmed based on test results"
        }
    ],
    "ruled_out": [
        {
            "condition": "ruled out condition name",
            "reason": "brief explanation of why this was ruled out"
        }
    ],
    "final_diagnosis": "the single most likely primary diagnosis in one sentence",
    "updated_treatment": [
        "updated treatment suggestion 1",
        "updated treatment suggestion 2"
    ],
    "next_steps": [
        "next step 1",
        "next step 2"
    ],
    "urgency": "Emergency / Urgent / Routine",
    "disclaimer": "These are AI-generated suggestions only. Clinical judgment of the attending medical professional must be applied before any action is taken.",
    "summary": "A brief summary of the refined diagnosis based on initial findings and test results"
}

Important rules:
- Use both the original findings and the test results to make your assessment
- confirmed_conditions can have 1 or more entries if multiple conditions are present
- ruled_out should list conditions from the original assessment that are no longer likely
- final_diagnosis should be clear and specific
- updated_treatment should reflect the confirmed diagnosis not the original possibilities
- Always consider West African disease context
- Never say see a doctor — the user IS the doctor
"""

def refine_diagnosis(original_findings: list, test_results: str, analysis_type: str) -> dict:
    # --------------------------------------------------------
    # Takes the original 3 possible conditions and the
    # doctor's test results and returns a refined diagnosis.
    # analysis_type is either "xray" or "symptoms"
    # --------------------------------------------------------

    # Format the original findings for Claude
    findings_text = "\n".join([
        f"- {f.get('condition', '—')} ({f.get('confidence', '—')}% confidence): {f.get('description', '')}"
        for f in original_findings
    ])

    # Build the message to Claude
    user_message = f"""
Original {analysis_type} analysis identified these 3 possible conditions:
{findings_text}

The doctor has now carried out the recommended tests. Here are the test results:
{test_results}

Please analyse the test results together with the original findings and provide a refined diagnosis.
"""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1200,
        system=REFINE_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_message
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

    result = json.loads(response_text)
    return result