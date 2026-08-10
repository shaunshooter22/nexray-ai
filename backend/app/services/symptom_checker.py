# ============================================================
# NexRay AI - Symptom Checker Service
# This service takes a list of symptoms from the doctor,
# sends them to the Claude API which acts as a medical
# triage assistant, and returns 3 possible conditions
# with confidence percentages and recommendations.
# ============================================================

import os
import anthropic
import json
from dotenv import load_dotenv

load_dotenv()

# Get the Claude API key from the .env file
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Create the Anthropic client using our API key
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# ============================================================
# System prompt — sets Claude up as a medical triage
# assistant that returns 3 possible conditions with
# confidence percentages
# ============================================================
SYSTEM_PROMPT = """
You are a medical decision-support assistant for NexRay AI, a platform used by doctors and medical staff in Ghana and West Africa.

Your job is to:
1. Analyse the symptoms provided
2. Identify the 3 most likely medical conditions based on those symptoms
3. Prioritise conditions common in West Africa such as malaria, typhoid, dengue fever and others
4. Return a structured JSON response with your findings

You must ALWAYS respond with valid JSON in exactly this format and nothing else:
{
    "possible_conditions": [
        {
            "condition": "most likely condition",
            "confidence": 87,
            "description": "brief description of why this condition matches the symptoms"
        },
        {
            "condition": "second possible condition",
            "confidence": 65,
            "description": "brief description of why this condition matches the symptoms"
        },
        {
            "condition": "third possible condition",
            "confidence": 42,
            "description": "brief description of why this condition matches the symptoms"
        }
    ],
    "recommended_tests": [
        "test 1",
        "test 2"
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
    "summary": "A brief overall summary of the assessment"
}

Important rules:
- Always return EXACTLY 3 possible conditions ordered from most likely to least likely
- confidence is a number between 0 and 100 representing how certain you are about that specific condition independently
- Each confidence is independent — they do not need to add up to 100
- Always include at least 2 recommended tests
- Always include at least 2 treatment suggestions — these are suggestions for the doctor, not prescriptions
- Consider malaria first when fever is present in a West African context
- Urgency is Emergency if life threatening, Urgent if needs same day attention, Routine otherwise
- Never say see a doctor — the user IS the doctor or medical staff
"""

def check_symptoms(symptoms: str) -> dict:
    # --------------------------------------------------------
    # Takes a string of symptoms from the doctor,
    # sends them to Claude API and returns a structured
    # dictionary with 3 possible conditions and recommendations
    # --------------------------------------------------------

    # Send the symptoms to Claude API
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Please analyse these symptoms and provide your assessment with exactly 3 possible conditions: {symptoms}"
            }
        ]
    )

    # Extract the text response from Claude
    response_text = message.content[0].text

    # Clean the response
    response_text = response_text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    response_text = response_text.strip()

    # Extract just the JSON object
    start = response_text.find("{")
    end = response_text.rfind("}") + 1
    if start != -1 and end != 0:
        response_text = response_text[start:end]

    # Parse the JSON response from Claude
    result = json.loads(response_text)

    return result