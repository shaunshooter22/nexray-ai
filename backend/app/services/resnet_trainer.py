# ============================================================
# NexRay AI - ResNet X-Ray Classifier Training Module
# ============================================================
# This module contains the full pipeline for fine-tuning a
# pretrained ResNet-50 model on chest X-ray data for the
# West African clinical context.
#
# NOTE: This training pipeline requires GPU resources (minimum
# 8GB VRAM recommended). In the current deployment, the system
# uses the Claude Vision API for X-ray analysis due to GPU
# resource constraints. This module demonstrates the complete
# ML training pipeline that would replace the API call in a
# GPU-enabled production environment.
#
# Dataset: NIH Chest X-Ray14
# https://www.kaggle.com/datasets/nih-chest-xrays/data
# 112,120 frontal chest X-ray images with 14 disease labels
#
# Model: ResNet-50 (pretrained on ImageNet)
# Fine-tuned for 5 conditions most relevant to West Africa:
# - Normal
# - Pneumonia
# - Tuberculosis (TB)
# - Pleural Effusion
# - Cardiomegaly
# ============================================================

import os
import json
import numpy as np
from pathlib import Path

# ── Deep Learning Imports ──
# These would be installed in a GPU-enabled environment:
# pip install torch torchvision transformers scikit-learn pillow

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    from torchvision import transforms, models
    from PIL import Image
    from sklearn.metrics import classification_report, confusion_matrix
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("PyTorch not available. Install with: pip install torch torchvision")

# ============================================================
# CONFIGURATION
# ============================================================

# Target conditions relevant to West African clinical context
CONDITION_LABELS = [
    "Normal",
    "Pneumonia",
    "Tuberculosis",
    "Pleural Effusion",
    "Cardiomegaly"
]

# Map NIH dataset labels to our 5 conditions
NIH_LABEL_MAPPING = {
    "No Finding": "Normal",
    "Pneumonia": "Pneumonia",
    "Infiltration": "Pneumonia",    # Consolidation patterns
    "Effusion": "Pleural Effusion",
    "Pleural_Thickening": "Pleural Effusion",
    "Cardiomegaly": "Cardiomegaly",
    "Fibrosis": "Tuberculosis",     # TB often presents with fibrosis
    "Nodule": "Tuberculosis",       # TB nodules
    "Mass": "Tuberculosis",
}

# Training configuration
TRAINING_CONFIG = {
    "image_size": 224,          # ResNet-50 input size
    "batch_size": 32,           # Batch size per GPU
    "learning_rate": 0.001,     # Initial learning rate
    "num_epochs": 20,           # Training epochs
    "patience": 5,              # Early stopping patience
    "train_split": 0.7,         # 70% training data
    "val_split": 0.15,          # 15% validation data
    "test_split": 0.15,         # 15% test data
    "num_workers": 4,           # DataLoader workers
    "weight_decay": 1e-4,       # L2 regularisation
    "dropout_rate": 0.5,        # Dropout for regularisation
}

MODEL_SAVE_PATH = "app/models/resnet_xray_classifier.pth"
LABEL_MAP_PATH = "app/models/label_map.json"


# ============================================================
# DATASET CLASS
# ============================================================

class ChestXRayDataset(Dataset):
    """
    Custom PyTorch Dataset for NIH Chest X-Ray14.

    Loads X-ray images and their labels from the NIH dataset
    directory structure and applies the specified transforms.

    Args:
        image_paths: List of paths to X-ray images
        labels: List of integer class labels
        transform: torchvision transforms to apply
    """

    def __init__(self, image_paths: list, labels: list, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        # Load image in grayscale (X-rays are greyscale)
        image = Image.open(self.image_paths[idx]).convert("RGB")

        if self.transform:
            image = self.transform(image)

        label = torch.tensor(self.labels[idx], dtype=torch.long)
        return image, label


# ============================================================
# DATA TRANSFORMS
# ============================================================

def get_transforms():
    """
    Returns training and validation transforms.

    Training transforms include augmentation to improve
    generalisation — flipping, rotation, and brightness
    adjustments simulate variations in X-ray acquisition.

    Validation/test transforms only normalise without augmentation
    to ensure consistent evaluation.
    """
    # ImageNet normalisation values (ResNet was trained on these)
    mean = [0.485, 0.456, 0.406]
    std  = [0.229, 0.224, 0.225]

    train_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])

    return train_transform, val_transform


# ============================================================
# MODEL DEFINITION
# ============================================================

def build_model(num_classes: int = 5, dropout_rate: float = 0.5):
    """
    Builds a fine-tuned ResNet-50 model for chest X-ray classification.

    Architecture:
    - Base: ResNet-50 pretrained on ImageNet (transfer learning)
    - All layers are unfrozen for fine-tuning
    - Final FC layer replaced with custom classifier head:
      ResNet FC (2048) -> Dropout -> Linear (512) -> ReLU -> Linear (num_classes)

    Transfer learning rationale:
    ResNet-50 pretrained on ImageNet has learned low-level features
    (edges, textures) that transfer well to medical imaging tasks.
    Fine-tuning all layers allows the model to adapt these features
    to X-ray specific patterns.

    Args:
        num_classes: Number of output classes (default 5)
        dropout_rate: Dropout probability for regularisation

    Returns:
        model: PyTorch model ready for training
    """
    # Load pretrained ResNet-50
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

    # Unfreeze all layers for fine-tuning
    for param in model.parameters():
        param.requires_grad = True

    # Replace the final fully connected layer
    # ResNet-50 default FC: Linear(2048, 1000) for ImageNet
    # We replace with a custom head for our 5 classes
    in_features = model.fc.in_features  # 2048
    model.fc = nn.Sequential(
        nn.Dropout(p=dropout_rate),
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(p=dropout_rate / 2),
        nn.Linear(512, num_classes)
    )

    return model


# ============================================================
# DATA LOADING
# ============================================================

def load_nih_dataset(data_dir: str):
    """
    Loads and preprocesses the NIH Chest X-Ray14 dataset.

    The NIH dataset contains:
    - 112,120 chest X-ray images
    - Data_Entry_2017.csv with labels per image
    - Multiple labels per image (multi-label classification)

    We simplify to single-label by taking the primary condition
    and mapping to our 5 West African relevant conditions.

    Args:
        data_dir: Path to NIH dataset directory

    Returns:
        image_paths: List of image file paths
        labels: List of integer class labels
        label_to_idx: Dictionary mapping label names to indices
    """
    import csv

    label_to_idx = {label: idx for idx, label in enumerate(CONDITION_LABELS)}
    image_paths = []
    labels = []
    skipped = 0

    csv_path = os.path.join(data_dir, "Data_Entry_2017.csv")

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            image_name = row["Image Index"]
            finding_labels = row["Finding Labels"].split("|")

            # Map to our conditions - take first matching label
            assigned_label = None
            for finding in finding_labels:
                finding = finding.strip()
                if finding in NIH_LABEL_MAPPING:
                    mapped = NIH_LABEL_MAPPING[finding]
                    if mapped in label_to_idx:
                        assigned_label = mapped
                        break

            if assigned_label is None:
                skipped += 1
                continue

            # Find image file in dataset subdirectories
            image_path = None
            for subdir in ["images_001", "images_002", "images_003",
                           "images_004", "images_005", "images_006",
                           "images_007", "images_008", "images_009",
                           "images_010", "images_011", "images_012"]:
                candidate = os.path.join(data_dir, subdir, "images", image_name)
                if os.path.exists(candidate):
                    image_path = candidate
                    break

            if image_path:
                image_paths.append(image_path)
                labels.append(label_to_idx[assigned_label])

    print(f"Loaded {len(image_paths)} images ({skipped} skipped - no matching label)")
    return image_paths, labels, label_to_idx


def create_data_loaders(image_paths: list, labels: list):
    """
    Splits dataset and creates PyTorch DataLoaders.

    Performs stratified split to maintain class balance across
    training, validation and test sets.

    Args:
        image_paths: List of image file paths
        labels: List of integer labels

    Returns:
        train_loader, val_loader, test_loader: PyTorch DataLoaders
    """
    from sklearn.model_selection import train_test_split

    train_transform, val_transform = get_transforms()

    # Stratified split to maintain class distribution
    X_train, X_temp, y_train, y_temp = train_test_split(
        image_paths, labels,
        test_size=(1 - TRAINING_CONFIG["train_split"]),
        stratify=labels,
        random_state=42
    )

    val_ratio = TRAINING_CONFIG["val_split"] / (
        TRAINING_CONFIG["val_split"] + TRAINING_CONFIG["test_split"]
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=(1 - val_ratio),
        stratify=y_temp,
        random_state=42
    )

    print(f"Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")

    train_dataset = ChestXRayDataset(X_train, y_train, transform=train_transform)
    val_dataset   = ChestXRayDataset(X_val,   y_val,   transform=val_transform)
    test_dataset  = ChestXRayDataset(X_test,  y_test,  transform=val_transform)

    train_loader = DataLoader(
        train_dataset,
        batch_size=TRAINING_CONFIG["batch_size"],
        shuffle=True,
        num_workers=TRAINING_CONFIG["num_workers"],
        pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=TRAINING_CONFIG["batch_size"],
        shuffle=False,
        num_workers=TRAINING_CONFIG["num_workers"],
        pin_memory=True
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=TRAINING_CONFIG["batch_size"],
        shuffle=False,
        num_workers=TRAINING_CONFIG["num_workers"],
        pin_memory=True
    )

    return train_loader, val_loader, test_loader


# ============================================================
# TRAINING LOOP
# ============================================================

def train_model(data_dir: str):
    """
    Full training pipeline for the ResNet-50 chest X-ray classifier.

    Training procedure:
    1. Load and preprocess NIH Chest X-Ray14 dataset
    2. Split into train/val/test sets (70/15/15)
    3. Build ResNet-50 with custom classifier head
    4. Train with Adam optimiser and ReduceLROnPlateau scheduler
    5. Apply early stopping based on validation loss
    6. Evaluate on held-out test set
    7. Save best model weights and label map

    Args:
        data_dir: Path to NIH Chest X-Ray14 dataset directory
    """
    if not TORCH_AVAILABLE:
        print("PyTorch is required for training. Install with:")
        print("pip install torch torchvision scikit-learn")
        return

    # Detect available hardware
    device = torch.device("cuda" if torch.cuda.is_available() else
                          "mps"  if torch.backends.mps.is_available() else
                          "cpu")
    print(f"Training on: {device}")
    if device.type == "cpu":
        print("WARNING: Training on CPU will be very slow.")
        print("Use Google Colab (free T4 GPU) for training.")

    # Load dataset
    print("\nLoading NIH Chest X-Ray14 dataset...")
    image_paths, labels, label_to_idx = load_nih_dataset(data_dir)

    # Create data loaders
    print("Creating data loaders...")
    train_loader, val_loader, test_loader = create_data_loaders(image_paths, labels)

    # Build model
    print("Building ResNet-50 model...")
    model = build_model(
        num_classes=len(CONDITION_LABELS),
        dropout_rate=TRAINING_CONFIG["dropout_rate"]
    )
    model = model.to(device)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Loss function with class weights to handle imbalance
    class_counts = np.bincount(labels)
    class_weights = torch.FloatTensor(
        1.0 / (class_counts / class_counts.sum())
    ).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # Optimiser and scheduler
    optimizer = optim.Adam(
        model.parameters(),
        lr=TRAINING_CONFIG["learning_rate"],
        weight_decay=TRAINING_CONFIG["weight_decay"]
    )
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=3, verbose=True
    )

    # Create model directory
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

    # Training loop
    best_val_loss = float("inf")
    patience_counter = 0
    history = {"train_loss": [], "val_loss": [], "val_accuracy": []}

    print("\nStarting training...")
    print("=" * 60)

    for epoch in range(TRAINING_CONFIG["num_epochs"]):
        # ── Training phase ──
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_idx, (images, targets) in enumerate(train_loader):
            images  = images.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            train_loss    += loss.item()
            _, predicted   = outputs.max(1)
            train_total   += targets.size(0)
            train_correct += predicted.eq(targets).sum().item()

            if (batch_idx + 1) % 50 == 0:
                print(f"  Epoch {epoch+1} | Batch {batch_idx+1}/{len(train_loader)} "
                      f"| Loss: {loss.item():.4f}")

        avg_train_loss = train_loss / len(train_loader)
        train_accuracy = 100.0 * train_correct / train_total

        # ── Validation phase ──
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, targets in val_loader:
                images  = images.to(device)
                targets = targets.to(device)

                outputs = model(images)
                loss    = criterion(outputs, targets)

                val_loss    += loss.item()
                _, predicted = outputs.max(1)
                val_total   += targets.size(0)
                val_correct += predicted.eq(targets).sum().item()

        avg_val_loss = val_loss / len(val_loader)
        val_accuracy = 100.0 * val_correct / val_total

        # Update scheduler
        scheduler.step(avg_val_loss)

        # Log epoch results
        history["train_loss"].append(avg_train_loss)
        history["val_loss"].append(avg_val_loss)
        history["val_accuracy"].append(val_accuracy)

        print(f"\nEpoch {epoch+1}/{TRAINING_CONFIG['num_epochs']}")
        print(f"  Train Loss: {avg_train_loss:.4f} | Train Acc: {train_accuracy:.2f}%")
        print(f"  Val Loss:   {avg_val_loss:.4f} | Val Acc:   {val_accuracy:.2f}%")

        # Early stopping and model checkpoint
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            torch.save({
                "epoch": epoch + 1,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_loss": best_val_loss,
                "val_accuracy": val_accuracy,
                "label_to_idx": label_to_idx,
                "condition_labels": CONDITION_LABELS,
            }, MODEL_SAVE_PATH)
            print(f"  Best model saved (val_loss: {best_val_loss:.4f})")
        else:
            patience_counter += 1
            print(f"  No improvement ({patience_counter}/{TRAINING_CONFIG['patience']})")
            if patience_counter >= TRAINING_CONFIG["patience"]:
                print("Early stopping triggered.")
                break

    # ── Test set evaluation ──
    print("\n" + "=" * 60)
    print("Evaluating on test set...")

    checkpoint = torch.load(MODEL_SAVE_PATH, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    all_predictions = []
    all_targets     = []

    with torch.no_grad():
        for images, targets in test_loader:
            images  = images.to(device)
            outputs = model(images)
            _, predicted = outputs.max(1)
            all_predictions.extend(predicted.cpu().numpy())
            all_targets.extend(targets.numpy())

    print("\nClassification Report:")
    print(classification_report(
        all_targets, all_predictions,
        target_names=CONDITION_LABELS
    ))

    print("\nConfusion Matrix:")
    print(confusion_matrix(all_targets, all_predictions))

    # Save label map for inference
    with open(LABEL_MAP_PATH, "w") as f:
        json.dump({
            "label_to_idx": label_to_idx,
            "idx_to_label": {str(v): k for k, v in label_to_idx.items()},
            "condition_labels": CONDITION_LABELS,
        }, f, indent=2)

    print(f"\nTraining complete.")
    print(f"Best model saved to: {MODEL_SAVE_PATH}")
    print(f"Label map saved to:  {LABEL_MAP_PATH}")
    return history


# ============================================================
# INFERENCE FUNCTION
# ============================================================

def predict_xray(image_bytes: bytes, image_type: str = "image/jpeg") -> dict:
    """
    Runs inference on a chest X-ray image using the trained ResNet-50.

    This function would replace the Claude Vision API call in
    xray_analyzer.py in a GPU-enabled production environment.

    In the current deployment, xray_analyzer.py uses Claude Vision API
    because the ResNet model requires GPU resources for efficient
    training and inference at scale.

    Args:
        image_bytes: Raw image bytes from the uploaded X-ray
        image_type: MIME type of the image

    Returns:
        dict: Structured findings matching the NexRay AI API response format
    """
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch not available for inference.")

    if not os.path.exists(MODEL_SAVE_PATH):
        raise RuntimeError(
            f"Trained model not found at {MODEL_SAVE_PATH}. "
            "Run train_model() first with the NIH dataset."
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load model
    checkpoint = torch.load(MODEL_SAVE_PATH, map_location=device)
    model = build_model(num_classes=len(CONDITION_LABELS))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    model.to(device)

    # Preprocess image
    _, val_transform = get_transforms()
    import io
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_tensor = val_transform(image).unsqueeze(0).to(device)

    # Run inference
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.softmax(outputs, dim=1).squeeze()

    # Build structured response matching NexRay API format
    condition_scores = [
        {
            "condition": CONDITION_LABELS[i],
            "confidence": round(probabilities[i].item() * 100, 1),
            "description": _get_condition_description(CONDITION_LABELS[i])
        }
        for i in range(len(CONDITION_LABELS))
    ]

    # Sort by confidence descending and take top 3
    condition_scores.sort(key=lambda x: x["confidence"], reverse=True)
    top_3 = condition_scores[:3]

    # Determine urgency based on top condition
    urgency = _get_urgency(top_3[0]["condition"], top_3[0]["confidence"])

    return {
        "body_region": "Chest (Thorax)",
        "findings": top_3,
        "overall_impression": (
            f"ResNet-50 classifier identifies {top_3[0]['condition']} as the most "
            f"likely finding with {top_3[0]['confidence']}% confidence. "
            f"Clinical correlation and radiologist review recommended."
        ),
        "recommended_tests": _get_recommended_tests(top_3[0]["condition"]),
        "suggested_treatment": _get_suggested_treatment(top_3[0]["condition"]),
        "next_steps": [
            "Correlate findings with clinical presentation",
            "Consult radiologist for formal report",
            "Consider additional imaging if indicated"
        ],
        "urgency": urgency,
        "model": "ResNet-50 fine-tuned on NIH Chest X-Ray14",
        "disclaimer": (
            "These findings are generated by a fine-tuned ResNet-50 model "
            "and must be verified by a qualified radiologist before clinical action."
        )
    }


def _get_condition_description(condition: str) -> str:
    descriptions = {
        "Normal": "No significant radiological abnormality detected in the chest X-ray.",
        "Pneumonia": "Increased opacity consistent with alveolar consolidation suggesting pneumonia.",
        "Tuberculosis": "Infiltrates or nodular opacities consistent with pulmonary tuberculosis.",
        "Pleural Effusion": "Blunting of costophrenic angle suggesting fluid accumulation in pleural space.",
        "Cardiomegaly": "Increased cardiothoracic ratio suggesting cardiac enlargement.",
    }
    return descriptions.get(condition, "Radiological findings present.")


def _get_urgency(condition: str, confidence: float) -> str:
    if condition in ["Pleural Effusion", "Cardiomegaly"] and confidence > 70:
        return "Urgent"
    if condition == "Pneumonia" and confidence > 80:
        return "Urgent"
    if condition == "Tuberculosis":
        return "Urgent"
    if condition == "Normal":
        return "Routine"
    return "Routine"


def _get_recommended_tests(condition: str) -> list:
    tests = {
        "Normal": ["Follow up if symptoms persist", "Repeat CXR in 6 months if indicated"],
        "Pneumonia": ["Sputum culture and sensitivity", "CBC with differential", "Blood culture", "CRP/ESR"],
        "Tuberculosis": ["Sputum smear for AFB (x3)", "GeneXpert MTB/RIF", "Mantoux test", "HIV test"],
        "Pleural Effusion": ["Ultrasound chest", "Thoracocentesis for fluid analysis", "LDH, protein, glucose of fluid"],
        "Cardiomegaly": ["ECG", "Echocardiogram", "BNP/NT-proBNP", "Renal function tests"],
    }
    return tests.get(condition, ["Clinical assessment", "Further investigations as indicated"])


def _get_suggested_treatment(condition: str) -> list:
    treatments = {
        "Normal": ["No specific treatment required", "Symptomatic management as needed"],
        "Pneumonia": ["Empiric antibiotics (amoxicillin-clavulanate or ceftriaxone)", "Oxygen therapy if SpO2 <94%", "IV fluids if dehydrated"],
        "Tuberculosis": ["Initiate HRZE regimen after confirmation", "Isolate patient", "Contact tracing", "Notify public health authorities"],
        "Pleural Effusion": ["Treat underlying cause", "Thoracocentesis if large or symptomatic", "Chest drain if empyema"],
        "Cardiomegaly": ["Diuretics (furosemide)", "ACE inhibitors/ARBs", "Beta-blockers", "Treat underlying cause"],
    }
    return treatments.get(condition, ["Refer to specialist", "Symptomatic management"])


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # --------------------------------------------------------
    # To train the model:
    # 1. Download NIH Chest X-Ray14 from Kaggle
    # 2. Set NIH_DATA_DIR to your dataset path
    # 3. Run: python -m app.services.resnet_trainer
    #
    # Recommended: Run on Google Colab with free T4 GPU
    # Expected training time: 2-4 hours on T4 GPU
    # Expected accuracy: 75-85% on 5-class classification
    # --------------------------------------------------------

    NIH_DATA_DIR = os.environ.get("NIH_DATA_DIR", "./data/nih_chest_xray")

    if not os.path.exists(NIH_DATA_DIR):
        print(f"NIH dataset not found at: {NIH_DATA_DIR}")
        print("Download from: https://www.kaggle.com/datasets/nih-chest-xrays/data")
        print("Set NIH_DATA_DIR environment variable to your dataset path.")
    else:
        history = train_model(NIH_DATA_DIR)
        print("\nTraining history:")
        for epoch, (tl, vl, va) in enumerate(zip(
            history["train_loss"],
            history["val_loss"],
            history["val_accuracy"]
        ), 1):
            print(f"  Epoch {epoch:2d}: train_loss={tl:.4f} val_loss={vl:.4f} val_acc={va:.2f}%")