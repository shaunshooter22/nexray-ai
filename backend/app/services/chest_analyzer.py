# ============================================================
# NexRay AI - Chest X-Ray Analyzer
# This service takes a chest xray image and detects possible
# conditions like pneumonia, pleural effusion, cardiomegaly etc.
# We are using a pretrained model from HuggingFace that was
# trained on the NIH ChestX-ray14 dataset.
# ============================================================

from transformers import AutoImageProcessor, AutoModelForImageClassification  # HuggingFace tools for loading the model
from PIL import Image  # For opening and processing the image
import torch  # PyTorch runs the model inference
import io  # For handling image bytes

# The pretrained chest xray model from HuggingFace
# This model was specifically trained on chest xray images
# to detect 14 different chest conditions
MODEL_NAME = "nickmuchi/vit-finetuned-chest-xray-pneumonia"

# Load the image processor for this model
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

# Load the pretrained chest model
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)

# Put the model in evaluation mode
model.eval()

# Confidence threshold - we only report findings above this percentage
# Anything below 40% confidence we consider too uncertain to report
CONFIDENCE_THRESHOLD = 0.40

def analyze_chest(image_bytes: bytes) -> dict:
    # --------------------------------------------------------
    # Takes raw chest xray image bytes, runs it through the
    # chest model and returns a dictionary containing:
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

    # Convert the raw model outputs to probabilities using softmax
    # Softmax turns the raw scores into percentages that add up to 100%
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]

    # Build the findings list
    findings = []
    for i, prob in enumerate(probabilities):
        confidence = prob.item()  # Convert tensor value to a Python float
        label = model.config.id2label[i]  # Get the condition name for this index

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
        summary = f"Analysis suggests possible {top_finding}. Please correlate with clinical symptoms."
    else:
        summary = "No significant findings detected above confidence threshold. Image may be normal."

    return {
        "region": "chest",  # The body region that was analyzed
        "findings": findings,  # List of detected conditions with confidence scores
        "summary": summary  # Short text summary of the overall findings
    }