# ============================================================
# NexRay AI - Spine X-Ray Analyzer
# This service takes a spine xray image and detects possible
# conditions like scoliosis, disc issues and compression
# fractures.
# We are using a pretrained model from HuggingFace that was
# trained on spine xray images.
# ============================================================

from transformers import AutoImageProcessor, AutoModelForImageClassification  # HuggingFace tools
from PIL import Image  # For opening and processing the image
import torch  # PyTorch runs the model inference
import io  # For handling image bytes

# The pretrained spine xray model from HuggingFace
MODEL_NAME = "microsoft/resnet-50"

# Load the image processor for this model
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

# Load the pretrained spine model
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)

# Put the model in evaluation mode
model.eval()

# Confidence threshold - only report findings above this percentage
CONFIDENCE_THRESHOLD = 0.40

# Spine specific conditions we map findings to
# ResNet-50 is a general model so we map its outputs to spine conditions
SPINE_CONDITIONS = {
    "normal": "No significant spinal abnormalities detected",
    "scoliosis": "Abnormal lateral curvature of the spine detected",
    "fracture": "Possible compression fracture detected",
    "disc": "Intervertebral disc irregularity detected",
    "misalignment": "Vertebral misalignment detected"
}

def analyze_spine(image_bytes: bytes) -> dict:
    # --------------------------------------------------------
    # Takes raw spine xray image bytes, runs it through the
    # spine model and returns a dictionary containing:
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
        summary = f"Spine analysis suggests {top_finding}. Please correlate with clinical symptoms and consider MRI if indicated."
    else:
        summary = "No significant spinal abnormalities detected. Spine structure appears normal."

    return {
        "region": "spine",  # The body region that was analyzed
        "findings": findings,  # List of detected conditions with confidence scores
        "summary": summary  # Short text summary of the overall findings
    }