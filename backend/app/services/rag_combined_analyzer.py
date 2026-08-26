# ============================================================
# NexRay AI - RAG Combined Analyzer (Ollama + Knowledge Base)
# ============================================================
# This module implements the RAG pipeline for combined analysis
# (X-ray image + symptoms) using Ollama and the custom West
# African medical knowledge base.
#
# Handles three analysis modes:
# 1. X-Ray image only — vision model analyses the image
# 2. Symptoms only — RAG retrieval + text generation
# 3. Combined — image + symptoms cross-referenced together
#
# NOTE: This module requires Ollama with a vision-capable model:
#   ollama serve
#   ollama pull llama3.2  (supports vision)
#
# In the current deployment, combined_analyzer.py uses the
# Claude Vision API because:
# 1. Ollama vision inference is slow on CPU (60+ seconds)
# 2. Railway/Render hosting has no GPU resources
# 3. Claude Vision provides superior medical imaging analysis
#
# This module is included to demonstrate the complete local
# inference pipeline for GPU-enabled environments.
# ============================================================

import json
import base64
import requests
from app.services.medical_knowledge import MEDICAL_DOCUMENTS, SYMPTOM_KEYWORD_MAP

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


def retrieve_relevant_documents(symptoms: str = None) -> str:
    """
    RAG Retrieval Step — retrieves relevant documents from the
    West African medical knowledge base.

    For X-ray only analysis, returns chest-focused documents.
    For symptom-based analysis, uses keyword matching.

    Args:
        symptoms: Optional symptom description for keyword matching

    Returns:
        context: Relevant medical knowledge as a string
    """
    if not symptoms:
        # X-ray only — return chest/thoracic condition documents
        relevant_docs = [
            doc for doc in MEDICAL_DOCUMENTS
            if doc["id"] in [
                "pneumonia_1", "tuberculosis_1", "pleural_effusion_1",
                "heart_failure_1", "sickle_cell_1"
            ]
        ]
        return "\n\n---\n\n".join([doc["content"] for doc in relevant_docs])

    # Symptom-based retrieval using keyword matching
    symptoms_lower = symptoms.lower()
    relevant_ids = set()
    for keyword, doc_ids in SYMPTOM_KEYWORD_MAP.items():
        if keyword in symptoms_lower:
            relevant_ids.update(doc_ids)

    if not relevant_ids:
        relevant_docs = MEDICAL_DOCUMENTS[:3]
    else:
        relevant_docs = [
            doc for doc in MEDICAL_DOCUMENTS
            if doc["id"] in relevant_ids
        ][:3]

    return "\n\n---\n\n".join([doc["content"] for doc in relevant_docs])


def analyze_combined_rag(image_bytes: bytes = None,
                         image_type: str = "image/jpeg",
                         symptoms: str = None) -> dict:
    """
    RAG-powered combined analyzer using Ollama vision model.

    For combined analysis, the model receives:
    - The X-ray image (base64 encoded)
    - Retrieved medical knowledge context
    - Patient symptom description
    And cross-references all three for a more accurate assessment.

    Args:
        image_bytes: Raw bytes of the X-ray image (optional)
        image_type: MIME type of the image
        symptoms: Plain English symptom description (optional)

    Returns:
        dict: Structured analysis matching the NexRay API format
    """
    medical_context = retrieve_relevant_documents(symptoms)

    # Build request payload based on available inputs
    if image_bytes and symptoms:
        # Combined: image + symptoms
        image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")
        prompt = f"""You are a medical decision-support assistant for NexRay AI, used by doctors in Ghana and West Africa.

Use the following medical knowledge base:

{medical_context}

Analyse this X-ray image together with the patient symptoms.
Cross-reference the imaging findings with the clinical presentation for a more accurate combined assessment.

Patient symptoms: {symptoms}

You MUST respond with ONLY valid JSON:
{{
    "analysis_basis": "Combined X-Ray and Symptoms",
    "body_region": "detected body region",
    "possible_conditions": [
        {{"condition": "most likely", "confidence": 85, "description": "based on X-ray and symptoms"}},
        {{"condition": "second", "confidence": 60, "description": "why possible"}},
        {{"condition": "third", "confidence": 40, "description": "why possible"}}
    ],
    "recommended_tests": ["test 1", "test 2"],
    "suggested_treatment": ["treatment 1", "treatment 2"],
    "next_steps": ["step 1", "step 2"],
    "urgency": "Urgent",
    "summary": "overall assessment",
    "disclaimer": "AI-generated. Clinical judgment required."
}}
JSON only. EXACTLY 3 conditions. urgency: Emergency/Urgent/Routine."""

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 2000}
        }
        timeout = 300

    elif image_bytes:
        # X-ray only
        image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")
        prompt = f"""You are an AI radiology assistant for NexRay AI, used by doctors in Ghana and West Africa.

Use this medical knowledge:

{medical_context}

Analyse this chest X-ray. Identify the body region and 3 most likely conditions.

You MUST respond with ONLY valid JSON:
{{
    "analysis_basis": "X-Ray only",
    "body_region": "detected region (e.g. Chest, Skull, Knee)",
    "possible_conditions": [
        {{"condition": "most likely", "confidence": 85, "description": "what you see"}},
        {{"condition": "second", "confidence": 60, "description": "why possible"}},
        {{"condition": "third", "confidence": 40, "description": "why possible"}}
    ],
    "recommended_tests": ["test 1", "test 2"],
    "suggested_treatment": ["treatment 1", "treatment 2"],
    "next_steps": ["step 1", "step 2"],
    "urgency": "Routine",
    "overall_impression": "radiological summary",
    "disclaimer": "AI-generated. Clinical judgment required."
}}
JSON only. EXACTLY 3 conditions."""

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 2000}
        }
        timeout = 300

    elif symptoms:
        # Symptoms only
        prompt = f"""You are a medical decision-support assistant for NexRay AI, used by doctors in Ghana and West Africa.

Use the following medical knowledge base:

{medical_context}

Analyse the patient symptoms and identify the 3 most likely conditions.

Patient symptoms: {symptoms}

You MUST respond with ONLY valid JSON:
{{
    "analysis_basis": "Symptoms only",
    "body_region": null,
    "possible_conditions": [
        {{"condition": "most likely", "confidence": 85, "description": "why matches symptoms"}},
        {{"condition": "second", "confidence": 60, "description": "why possible"}},
        {{"condition": "third", "confidence": 40, "description": "why possible"}}
    ],
    "recommended_tests": ["test 1", "test 2"],
    "suggested_treatment": ["treatment 1", "treatment 2"],
    "next_steps": ["step 1", "step 2"],
    "urgency": "Routine",
    "summary": "overall assessment",
    "disclaimer": "AI-generated. Clinical judgment required."
}}
JSON only. EXACTLY 3 conditions."""

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 2000}
        }
        timeout = 180

    else:
        return {"error": "No image or symptoms provided"}

    # Send to Ollama
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        response.raise_for_status()
        response_text = response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise Exception("Ollama is not running. Start with: ollama serve")
    except requests.exceptions.ReadTimeout:
        raise Exception("Ollama timed out. Try a smaller model: llama3.2:1b")

    # Parse JSON response
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]

    response_text = response_text.strip()
    start = response_text.find("{")
    end   = response_text.rfind("}") + 1
    if start != -1 and end != 0:
        response_text = response_text[start:end]

    import re
    response_text = re.sub(r',\s*}', '}', response_text)
    response_text = re.sub(r',\s*]', ']', response_text)

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON from Ollama: {e}")