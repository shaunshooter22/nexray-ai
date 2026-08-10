# ============================================================
# NexRay AI - Body Region Classifier
# This service takes an xray image and detects which body
# region it belongs to: chest, bone or spine.
# We are using a pretrained ResNet-50 model from HuggingFace.
# ============================================================

from transformers import AutoImageProcessor, AutoModelForImageClassification  # Correct HuggingFace tools for image models
from PIL import Image  # For opening and processing the uploaded image
import torch  # PyTorch runs the model inference
import io  # For handling image bytes

# The pretrained model we are using from HuggingFace
MODEL_NAME = "microsoft/resnet-50"

# Load the image processor - this prepares the image before feeding it to the model
# It resizes, normalizes and converts the image into the format the model expects
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

# Load the pretrained model itself
# This downloads the model weights from HuggingFace the first time it runs
# After that it uses the cached version
model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)

# Put the model in evaluation mode - this disables training features we dont need
model.eval()

# Keywords we use to match the model output to our three body regions
REGION_KEYWORDS = {
    "chest": ["chest", "lung", "thorax", "pulmonary", "cardiac", "heart", "rib"],
    "bone": ["bone", "fracture", "wrist", "hand", "finger", "elbow", "shoulder", "knee", "ankle", "foot"],
    "spine": ["spine", "vertebra", "lumbar", "cervical", "thoracic", "scoliosis", "disc"]
}

def classify_region(image_bytes: bytes) -> str:
    # --------------------------------------------------------
    # Takes raw image bytes from the upload, runs it through
    # the classifier and returns the detected body region
    # as a string: "chest", "bone" or "spine"
    # --------------------------------------------------------

    # Open the image from the uploaded bytes
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Prepare the image for the model
    inputs = processor(images=image, return_tensors="pt")

    # Run the image through the model without calculating gradients
    with torch.no_grad():
        outputs = model(**inputs)

    # Get the predicted class index
    predicted_index = outputs.logits.argmax(-1).item()

    # Convert the index to a human readable label
    predicted_label = model.config.id2label[predicted_index].lower()

    # Match the predicted label to one of our three body regions
    for region, keywords in REGION_KEYWORDS.items():
        if any(keyword in predicted_label for keyword in keywords):
            return region

    # If no match found default to chest
    return "chest"