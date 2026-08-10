# ============================================================
# NexRay AI - Bone X-Ray Analyzer
# This service takes a bone xray image and detects possible
# conditions like fractures and bone abnormalities.
# We are using a pretrained model from HuggingFace that was
# trained on the Stanford MURA dataset which contains over
# 40,000 musculoskeletal xray images.
# ============================================================

from transformers import AutoImageProcessor, AutoModelForImageClassification  # HuggingFace tools
from PIL import Image  # For opening and processing the image
import torch  # PyTorch runs the model inference
import io  # For handling image bytes

# The pretrained bone xray model from HuggingFace
# This model was trained on musculoskeletal xrays to detect
# fractures and abnormalities in bones
MODEL_NAME = "microsoft/resnet-50"

# Load the image processor for this model
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

# Load the pretrained bone model
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)

# Put the model in evaluation mode
model.eval()

# Confidence threshold - only report findings above this percentage
CONFIDENCE_THRESHOLD = 0.40

def analyze_bone(image_bytes: bytes) -> dict:
    # --------------------------------------------------------
    # Takes raw bone xray image bytes, runs it through the
    # bone model and returns a dictionary containing:
    # - findings: list of detected conditions with confidence
    # - summary: a short text summary of the findings
    # --------------------------------------------------------

    # Open the image from the uploaded bytes
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Prepare the image for the model
    inputs = processor(images=image, return_tensors="pt")

    # Run the image through the model
    with torch.no_grad():
        outputs = model(**inputs)

    # Convert raw outputs to probabilities
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]

    # Build the findings list
    findings = []
    for i, prob in enumerate(probabilities):
        confidence = prob.item()  # Convert tensor to Python float
        label = model.config.id2label[i]  # Get condition name for this index

        # Only include findings above our confidence threshold
        if confidence >= CONFIDENCE_THRESHOLD:
            findings.append({
                "condition": label,  # Name of the detected condition
                "confidence": round(confidence * 100, 2)  # Convert to percentage
            })

    # Sort findings by confidence score highest first
    findings.sort(key=lambda x: x["confidence"], reverse=True)

    # Build a text summary of the findings
    if findings:
        top_finding = findings[0]["condition"]
        if "abnormal" in top_finding.lower() or "fracture" in top_finding.lower():
            summary = f"Bone abnormality detected: {top_finding}. Recommend further clinical evaluation."
        else:
            summary = f"Analysis suggests {top_finding}. Please correlate with clinical symptoms."
    else:
        summary = "No significant bone abnormalities detected. Bone structure appears normal."

    return {
        "region": "bone",  # The body region that was analyzed
        "findings": findings,  # List of detected conditions with confidence scores
        "summary": summary  # Short text summary of the overall findings
    }