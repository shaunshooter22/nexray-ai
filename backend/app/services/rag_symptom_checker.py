# ============================================================
# NexRay AI - RAG Symptom Checker (Ollama + Custom Knowledge Base)
# ============================================================
# This module implements a Retrieval Augmented Generation (RAG)
# pipeline for symptom-based diagnosis using:
#
# 1. A custom West African medical knowledge base (medical_knowledge.py)
# 2. A local Ollama language model (llama3.2)
#
# How RAG works:
# - Instead of relying on the model's general training data alone,
#   we first RETRIEVE relevant disease information from our custom
#   knowledge base based on the patient's symptoms
# - We then AUGMENT the model's prompt with this retrieved context
# - The model GENERATES a diagnosis grounded in our specific data
#
# This approach means the model uses OUR medical knowledge base
# rather than generic internet data, making it more accurate for
# the West African clinical context.
#
# NOTE: This module requires Ollama to be running locally:
#   ollama serve
#   ollama pull llama3.2
#
# In the current deployment, symptom_checker.py uses the Claude API
# because Ollama requires local GPU/CPU resources that are not
# available on the Render/Railway hosting environment. This module
# demonstrates the full RAG pipeline for local/GPU deployment.
# ============================================================

import json
import requests
from app.services.medical_knowledge import MEDICAL_DOCUMENTS, SYMPTOM_KEYWORD_MAP

# Ollama configuration
OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


def retrieve_relevant_documents(symptoms: str) -> str:
    """
    RAG Retrieval Step — searches the custom medical knowledge base
    for documents relevant to the given symptoms.

    Uses keyword matching against the SYMPTOM_KEYWORD_MAP to find
    the most relevant disease documents. This is a lightweight
    retrieval approach that avoids the need for vector embeddings
    while still providing accurate context retrieval for the
    structured medical knowledge base.

    In a production system with a larger knowledge base, this would
    be replaced with semantic similarity search using embeddings
    (e.g. ChromaDB + sentence-transformers).

    Args:
        symptoms: Plain English symptom description from the doctor

    Returns:
        context: Concatenated relevant disease documents as a string
    """
    symptoms_lower = symptoms.lower()

    # Find relevant document IDs based on symptom keywords
    relevant_ids = set()
    for keyword, doc_ids in SYMPTOM_KEYWORD_MAP.items():
        if keyword in symptoms_lower:
            relevant_ids.update(doc_ids)

    # Retrieve matched documents (limit to 3 to keep prompt concise)
    if not relevant_ids:
        # Fallback: return most common West African conditions
        relevant_docs = MEDICAL_DOCUMENTS[:3]
    else:
        relevant_docs = [
            doc for doc in MEDICAL_DOCUMENTS
            if doc["id"] in relevant_ids
        ][:3]

    # Concatenate documents into context string
    context = "\n\n---\n\n".join([doc["content"] for doc in relevant_docs])

    print(f"[RAG] Retrieved {len(relevant_docs)} documents for symptoms")
    print(f"[RAG] Matched documents: {[doc['id'] for doc in relevant_docs]}")

    return context


def check_symptoms_rag(symptoms: str) -> dict:
    """
    RAG-powered symptom checker using Ollama + custom knowledge base.

    Pipeline:
    1. RETRIEVE: Search custom West African medical knowledge base
    2. AUGMENT: Build prompt with retrieved medical context
    3. GENERATE: Send augmented prompt to local Ollama model
    4. PARSE: Extract structured JSON from model response

    Args:
        symptoms: Plain English symptom description

    Returns:
        dict: Structured diagnosis with 3 conditions and confidence scores
    """

    # Step 1: Retrieve relevant medical knowledge (RAG)
    print(f"[RAG] Processing symptoms: {symptoms[:100]}...")
    medical_context = retrieve_relevant_documents(symptoms)

    # Step 2: Build augmented prompt with retrieved context
    prompt = f"""You are a medical decision-support assistant for NexRay AI, used by doctors in Ghana and West Africa.

Use ONLY the following medical knowledge base to inform your diagnosis:

{medical_context}

Based on this knowledge, analyse the following patient symptoms and identify the 3 most likely conditions.

Patient symptoms: {symptoms}

You MUST respond with ONLY valid JSON in exactly this format, nothing else:
{{
    "possible_conditions": [
        {{
            "condition": "most likely condition name",
            "confidence": 85,
            "description": "why this condition matches the symptoms based on the knowledge base"
        }},
        {{
            "condition": "second possible condition",
            "confidence": 60,
            "description": "why this condition is possible"
        }},
        {{
            "condition": "third possible condition",
            "confidence": 40,
            "description": "why this condition is possible"
        }}
    ],
    "recommended_tests": ["test 1", "test 2", "test 3"],
    "suggested_treatment": ["treatment 1", "treatment 2"],
    "next_steps": ["step 1", "step 2"],
    "urgency": "Urgent",
    "summary": "brief overall assessment",
    "disclaimer": "AI-generated suggestions only. Clinical judgment required."
}}

Rules:
- Return EXACTLY 3 conditions ordered most likely to least likely
- confidence is 0-100, each condition is scored independently
- urgency must be exactly: Emergency, Urgent, or Routine
- Base your response on the provided knowledge base only
- Respond with JSON only, no other text"""

    # Step 3: Send augmented prompt to Ollama
    print(f"[RAG] Sending request to Ollama ({OLLAMA_MODEL})...")
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,   # Low temperature for consistent output
                    "num_predict": 2000,  # Max tokens to generate
                }
            },
            timeout=300  # 5 minute timeout for CPU inference
        )
        response.raise_for_status()
        result = response.json()
        response_text = result.get("response", "").strip()
        print(f"[RAG] Received response ({len(response_text)} chars)")

    except requests.exceptions.ConnectionError:
        raise Exception(
            "Ollama is not running. Start it with: ollama serve\n"
            "Then pull the model: ollama pull llama3.2"
        )
    except requests.exceptions.ReadTimeout:
        raise Exception(
            "Ollama timed out. The model is taking too long to respond. "
            "Try a smaller model: ollama pull llama3.2:1b"
        )
    except Exception as e:
        raise Exception(f"Ollama request failed: {str(e)}")

    # Step 4: Parse and clean JSON response
    # Small models sometimes wrap JSON in markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]

    response_text = response_text.strip()

    # Extract JSON object boundaries
    start = response_text.find("{")
    end   = response_text.rfind("}") + 1
    if start != -1 and end != 0:
        response_text = response_text[start:end]

    # Fix common JSON formatting errors from small models
    import re
    response_text = re.sub(r',\s*}', '}', response_text)   # trailing commas
    response_text = re.sub(r',\s*]', ']', response_text)   # trailing commas in arrays

    try:
        result = json.loads(response_text)
        print("[RAG] Successfully parsed JSON response")
        return result
    except json.JSONDecodeError as e:
        print(f"[RAG] JSON parse error: {e}")
        print(f"[RAG] Raw response: {response_text[:500]}")
        raise Exception(
            "The Ollama model returned an invalid JSON response. "
            "Try again or use a larger model for better reliability."
        )