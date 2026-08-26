# ============================================================
# NexRay AI - ResNet X-Ray Classifier Training Module
# ============================================================
# This module contains the full pipeline for fine-tuning a
# pretrained ResNet-50 model on multiple X-ray datasets for
# the West African clinical context.
#
# Datasets used:
# 1. NIH Chest X-Ray14 — 112,120 chest X-rays (14 conditions)
#    https://www.kaggle.com/datasets/nih-chest-xrays/data
#
# 2. CheXpert (Stanford) — 224,316 chest X-rays (14 conditions)
#    https://stanfordmlgroup.github.io/competitions/chexpert
#
# 3. MURA (Stanford) — 40,895 musculoskeletal X-rays
#    Covers: wrist, elbow, shoulder, hand, humerus, finger, forearm
#    https://stanfordmlgroup.github.io/competitions/mura
#
# 4. VinDr-CXR — 18,000 chest X-rays from Vietnam
#    https://www.kaggle.com/datasets/vinbigdata/vinbigdata-chest-xray-abnormalities-detection
#
# Model: ResNet-50 (microsoft/resnet-50 pretrained on ImageNet)
# Fine-tuned for conditions most relevant to West Africa across
# all body regions.
#
# NOTE: This training pipeline requires GPU resources (minimum
# 8GB VRAM recommended). In the current deployment, the system
# uses the Claude Vision API for X-ray analysis due to GPU
# resource constraints on the hosting environment.
# ============================================================

import os
import json
import csv
import numpy as np
from pathlib import Path

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader, ConcatDataset
    from torchvision import transforms, models
    from PIL import Image
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.model_selection import train_test_split
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("PyTorch not available. Install with: pip install torch torchvision scikit-learn pillow")


# ============================================================
# CONDITION LABELS
# ============================================================
# Unified label set covering chest diseases and musculoskeletal
# conditions relevant to the West African clinical context.

CONDITION_LABELS = [
    # Chest conditions
    "Normal",
    "Pneumonia",
    "Tuberculosis",
    "Pleural Effusion",
    "Cardiomegaly",
    # Musculoskeletal conditions (from MURA dataset)
    "Fracture",
    "Abnormal Musculoskeletal",
]

# Training configuration
TRAINING_CONFIG = {
    "image_size":    224,
    "batch_size":    32,
    "learning_rate": 0.001,
    "num_epochs":    20,
    "patience":      5,
    "train_split":   0.7,
    "val_split":     0.15,
    "test_split":    0.15,
    "num_workers":   4,
    "weight_decay":  1e-4,
    "dropout_rate":  0.5,
}

MODEL_SAVE_PATH = "app/models/resnet_xray_classifier.pth"
LABEL_MAP_PATH  = "app/models/label_map.json"


# ============================================================
# DATASET CLASS
# ============================================================

class XRayDataset(Dataset):
    """
    Universal PyTorch Dataset for X-ray images.
    Works with all four datasets — NIH, CheXpert, MURA, VinDr.

    Args:
        image_paths: List of paths to X-ray images
        labels: List of integer class labels
        transform: torchvision transforms to apply
    """

    def __init__(self, image_paths: list, labels: list, transform=None):
        self.image_paths = image_paths
        self.labels      = labels
        self.transform   = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
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
    Returns training and validation/test transforms.

    Training augmentation improves generalisation by simulating
    variations in X-ray acquisition across different hospitals
    and equipment — common in the West African setting where
    equipment quality varies widely.
    """
    mean = [0.485, 0.456, 0.406]  # ImageNet normalisation
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

def build_model(num_classes: int = 7, dropout_rate: float = 0.5):
    """
    Builds a fine-tuned ResNet-50 for multi-body-region X-ray classification.

    Base model: microsoft/resnet-50 pretrained on ImageNet
    (ResNet50_Weights.IMAGENET1K_V2 from torchvision)

    Custom classifier head:
    ResNet FC (2048) -> Dropout(0.5) -> Linear(512) -> ReLU
                     -> Dropout(0.25) -> Linear(num_classes)

    Args:
        num_classes: Number of output classes (default 7)
        dropout_rate: Dropout probability for regularisation

    Returns:
        model: PyTorch model ready for training
    """
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

    # Unfreeze all layers for full fine-tuning
    for param in model.parameters():
        param.requires_grad = True

    # Replace final FC layer with custom head
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
# DATASET LOADERS
# ============================================================

def load_nih_dataset(data_dir: str, label_to_idx: dict) -> tuple:
    """
    Loads the NIH Chest X-Ray14 dataset.
    112,120 frontal chest X-ray images with 14 disease labels.
    Source: National Institutes of Health, USA.

    Label mapping to our unified condition set:
    - No Finding        -> Normal
    - Pneumonia         -> Pneumonia
    - Infiltration      -> Pneumonia (consolidation pattern)
    - Effusion          -> Pleural Effusion
    - Pleural_Thickening-> Pleural Effusion
    - Cardiomegaly      -> Cardiomegaly
    - Fibrosis          -> Tuberculosis
    - Nodule            -> Tuberculosis
    - Mass              -> Tuberculosis
    """
    NIH_LABEL_MAPPING = {
        "No Finding":         "Normal",
        "Pneumonia":          "Pneumonia",
        "Infiltration":       "Pneumonia",
        "Effusion":           "Pleural Effusion",
        "Pleural_Thickening": "Pleural Effusion",
        "Cardiomegaly":       "Cardiomegaly",
        "Fibrosis":           "Tuberculosis",
        "Nodule":             "Tuberculosis",
        "Mass":               "Tuberculosis",
    }

    image_paths = []
    labels      = []
    skipped     = 0

    csv_path = os.path.join(data_dir, "Data_Entry_2017.csv")
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            image_name     = row["Image Index"]
            finding_labels = row["Finding Labels"].split("|")

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

            # Search across all NIH image subdirectories
            image_path = None
            for subdir in [f"images_{str(i).zfill(3)}" for i in range(1, 13)]:
                candidate = os.path.join(data_dir, subdir, "images", image_name)
                if os.path.exists(candidate):
                    image_path = candidate
                    break

            if image_path:
                image_paths.append(image_path)
                labels.append(label_to_idx[assigned_label])

    print(f"NIH: Loaded {len(image_paths)} images ({skipped} skipped)")
    return image_paths, labels


def load_chexpert_dataset(data_dir: str, label_to_idx: dict) -> tuple:
    """
    Loads the CheXpert dataset (Stanford University).
    224,316 chest X-rays with uncertainty labels.
    Source: Stanford ML Group.

    CheXpert uses uncertainty labels (-1 = uncertain).
    We treat uncertain labels as positive for training
    (U-Ones policy) which is a common approach.

    Label mapping:
    - No Finding        -> Normal
    - Pneumonia         -> Pneumonia
    - Lung Opacity      -> Pneumonia
    - Pleural Effusion  -> Pleural Effusion
    - Cardiomegaly      -> Cardiomegaly
    """
    CHEXPERT_LABEL_MAPPING = {
        "No Finding":       "Normal",
        "Pneumonia":        "Pneumonia",
        "Lung Opacity":     "Pneumonia",
        "Pleural Effusion": "Pleural Effusion",
        "Cardiomegaly":     "Cardiomegaly",
    }

    image_paths = []
    labels      = []

    for split in ["train.csv", "valid.csv"]:
        csv_path = os.path.join(data_dir, split)
        if not os.path.exists(csv_path):
            continue

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                image_path = os.path.join(data_dir, row["Path"])
                if not os.path.exists(image_path):
                    continue

                # Find primary condition (first positive or uncertain label)
                assigned_label = None
                for chexpert_label, our_label in CHEXPERT_LABEL_MAPPING.items():
                    if chexpert_label in row:
                        val = row[chexpert_label].strip()
                        if val in ["1", "-1"]:  # positive or uncertain
                            if our_label in label_to_idx:
                                assigned_label = our_label
                                break

                if assigned_label:
                    image_paths.append(image_path)
                    labels.append(label_to_idx[assigned_label])

    print(f"CheXpert: Loaded {len(image_paths)} images")
    return image_paths, labels


def load_mura_dataset(data_dir: str, label_to_idx: dict) -> tuple:
    """
    Loads the MURA dataset (Stanford University).
    40,895 musculoskeletal X-rays across 7 body parts:
    wrist, elbow, shoulder, hand, humerus, finger, forearm.
    Source: Stanford ML Group.

    MURA is a binary classification dataset:
    - positive (abnormal) -> Fracture / Abnormal Musculoskeletal
    - negative (normal)   -> Normal

    We use the folder structure to determine labels:
    MURA-v1.1/train/XR_WRIST/patient00001/study1_positive/
    """
    image_paths = []
    labels      = []

    for split in ["train", "valid"]:
        split_dir = os.path.join(data_dir, "MURA-v1.1", split)
        if not os.path.exists(split_dir):
            continue

        for body_part in os.listdir(split_dir):
            body_part_dir = os.path.join(split_dir, body_part)
            if not os.path.isdir(body_part_dir):
                continue

            for patient in os.listdir(body_part_dir):
                patient_dir = os.path.join(body_part_dir, patient)
                if not os.path.isdir(patient_dir):
                    continue

                for study in os.listdir(patient_dir):
                    study_dir = os.path.join(patient_dir, study)
                    if not os.path.isdir(study_dir):
                        continue

                    # Label from folder name: positive or negative
                    is_positive = "positive" in study.lower()
                    label_name  = "Fracture" if is_positive else "Normal"

                    if label_name not in label_to_idx:
                        continue

                    for image_file in os.listdir(study_dir):
                        if image_file.lower().endswith((".png", ".jpg", ".jpeg")):
                            image_paths.append(os.path.join(study_dir, image_file))
                            labels.append(label_to_idx[label_name])

    print(f"MURA: Loaded {len(image_paths)} images")
    return image_paths, labels


def load_vindr_dataset(data_dir: str, label_to_idx: dict) -> tuple:
    """
    Loads the VinDr-CXR dataset.
    18,000 chest X-rays annotated by radiologists in Vietnam.
    Source: VinBigData, Vietnam.

    This dataset is particularly relevant for NexRay AI because
    it comes from a Southeast Asian clinical context similar to
    West Africa in terms of disease burden and equipment quality.

    Label mapping:
    - No finding        -> Normal
    - Pneumonia         -> Pneumonia
    - Pleural effusion  -> Pleural Effusion
    - Cardiomegaly      -> Cardiomegaly
    - Tuberculosis      -> Tuberculosis (explicitly labelled)
    """
    VINDR_LABEL_MAPPING = {
        "No finding":      "Normal",
        "Pneumonia":       "Pneumonia",
        "Pleural effusion":"Pleural Effusion",
        "Cardiomegaly":    "Cardiomegaly",
        "Tuberculosis":    "Tuberculosis",
    }

    image_paths = []
    labels      = []

    csv_path = os.path.join(data_dir, "train.csv")
    if not os.path.exists(csv_path):
        print(f"VinDr: train.csv not found at {csv_path}")
        return image_paths, labels

    seen_images = {}  # image_id -> label (take first matching label)

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            image_id    = row.get("image_id", "")
            class_name  = row.get("class_name", "").strip()

            if class_name not in VINDR_LABEL_MAPPING:
                continue

            our_label = VINDR_LABEL_MAPPING[class_name]
            if our_label not in label_to_idx:
                continue

            if image_id not in seen_images:
                seen_images[image_id] = our_label

    # Find image files
    images_dir = os.path.join(data_dir, "train")
    for image_id, label_name in seen_images.items():
        for ext in [".png", ".jpg", ".jpeg", ".dicom"]:
            candidate = os.path.join(images_dir, image_id + ext)
            if os.path.exists(candidate):
                image_paths.append(candidate)
                labels.append(label_to_idx[label_name])
                break

    print(f"VinDr: Loaded {len(image_paths)} images")
    return image_paths, labels


# ============================================================
# COMBINED DATASET LOADER
# ============================================================

def load_all_datasets(
    nih_dir:     str = None,
    chexpert_dir:str = None,
    mura_dir:    str = None,
    vindr_dir:   str = None,
) -> tuple:
    """
    Loads and combines all available datasets into a single
    unified training set.

    Any dataset directory that is None or doesn't exist is
    skipped gracefully — you can train with any combination
    of the four datasets depending on what you have downloaded.

    Args:
        nih_dir:      Path to NIH Chest X-Ray14 directory
        chexpert_dir: Path to CheXpert directory
        mura_dir:     Path to MURA directory
        vindr_dir:    Path to VinDr-CXR directory

    Returns:
        all_image_paths: Combined list of image paths
        all_labels:      Combined list of integer labels
        label_to_idx:    Label name to integer mapping
    """
    label_to_idx = {label: idx for idx, label in enumerate(CONDITION_LABELS)}
    all_image_paths = []
    all_labels      = []

    # Load NIH dataset
    if nih_dir and os.path.exists(nih_dir):
        print("Loading NIH Chest X-Ray14 dataset...")
        paths, labels = load_nih_dataset(nih_dir, label_to_idx)
        all_image_paths.extend(paths)
        all_labels.extend(labels)
    else:
        print("NIH dataset not found — skipping")

    # Load CheXpert dataset
    if chexpert_dir and os.path.exists(chexpert_dir):
        print("Loading CheXpert dataset...")
        paths, labels = load_chexpert_dataset(chexpert_dir, label_to_idx)
        all_image_paths.extend(paths)
        all_labels.extend(labels)
    else:
        print("CheXpert dataset not found — skipping")

    # Load MURA dataset
    if mura_dir and os.path.exists(mura_dir):
        print("Loading MURA musculoskeletal dataset...")
        paths, labels = load_mura_dataset(mura_dir, label_to_idx)
        all_image_paths.extend(paths)
        all_labels.extend(labels)
    else:
        print("MURA dataset not found — skipping")

    # Load VinDr dataset
    if vindr_dir and os.path.exists(vindr_dir):
        print("Loading VinDr-CXR dataset...")
        paths, labels = load_vindr_dataset(vindr_dir, label_to_idx)
        all_image_paths.extend(paths)
        all_labels.extend(labels)
    else:
        print("VinDr dataset not found — skipping")

    total = len(all_image_paths)
    print(f"\nTotal combined dataset: {total} images")

    if total == 0:
        raise ValueError(
            "No datasets loaded. Please provide at least one dataset directory."
        )

    # Print class distribution
    class_counts = np.bincount(all_labels, minlength=len(CONDITION_LABELS))
    print("\nClass distribution:")
    for i, label in enumerate(CONDITION_LABELS):
        print(f"  {label}: {class_counts[i]} images")

    return all_image_paths, all_labels, label_to_idx


# ============================================================
# DATA LOADERS
# ============================================================

def create_data_loaders(image_paths: list, labels: list) -> tuple:
    """
    Splits combined dataset and creates PyTorch DataLoaders.
    Uses stratified split to maintain class balance.
    """
    train_transform, val_transform = get_transforms()

    # Stratified 70/15/15 split
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

    print(f"\nSplit — Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")

    train_loader = DataLoader(
        XRayDataset(X_train, y_train, transform=train_transform),
        batch_size=TRAINING_CONFIG["batch_size"],
        shuffle=True,
        num_workers=TRAINING_CONFIG["num_workers"],
        pin_memory=True
    )
    val_loader = DataLoader(
        XRayDataset(X_val, y_val, transform=val_transform),
        batch_size=TRAINING_CONFIG["batch_size"],
        shuffle=False,
        num_workers=TRAINING_CONFIG["num_workers"],
        pin_memory=True
    )
    test_loader = DataLoader(
        XRayDataset(X_test, y_test, transform=val_transform),
        batch_size=TRAINING_CONFIG["batch_size"],
        shuffle=False,
        num_workers=TRAINING_CONFIG["num_workers"],
        pin_memory=True
    )

    return train_loader, val_loader, test_loader


# ============================================================
# TRAINING LOOP
# ============================================================

def train_model(
    nih_dir:      str = None,
    chexpert_dir: str = None,
    mura_dir:     str = None,
    vindr_dir:    str = None,
):
    """
    Full training pipeline for the NexRay AI X-ray classifier.

    Trains ResNet-50 on a combination of NIH, CheXpert, MURA,
    and VinDr datasets for multi-body-region X-ray classification.

    Training procedure:
    1. Load and combine all available datasets
    2. Stratified 70/15/15 train/val/test split
    3. Build ResNet-50 with custom classifier head
    4. Train with Adam optimiser + ReduceLROnPlateau scheduler
    5. Early stopping on validation loss (patience=5)
    6. Save best model checkpoint
    7. Evaluate on held-out test set

    Args:
        nih_dir:      Path to NIH Chest X-Ray14 directory
        chexpert_dir: Path to CheXpert directory
        mura_dir:     Path to MURA directory
        vindr_dir:    Path to VinDr-CXR directory
    """
    if not TORCH_AVAILABLE:
        print("PyTorch required. Install with: pip install torch torchvision scikit-learn")
        return

    device = torch.device(
        "cuda" if torch.cuda.is_available() else
        "mps"  if torch.backends.mps.is_available() else
        "cpu"
    )
    print(f"Training device: {device}")
    if device.type == "cpu":
        print("WARNING: Training on CPU is very slow. Use Google Colab (free T4 GPU).")

    # Load all datasets
    print("\n" + "=" * 60)
    print("Loading datasets...")
    image_paths, labels, label_to_idx = load_all_datasets(
        nih_dir=nih_dir,
        chexpert_dir=chexpert_dir,
        mura_dir=mura_dir,
        vindr_dir=vindr_dir,
    )

    # Create data loaders
    train_loader, val_loader, test_loader = create_data_loaders(image_paths, labels)

    # Build model
    print("\nBuilding ResNet-50 model...")
    model = build_model(
        num_classes=len(CONDITION_LABELS),
        dropout_rate=TRAINING_CONFIG["dropout_rate"]
    )
    model = model.to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}")

    # Class-weighted loss to handle imbalanced dataset
    class_counts = np.bincount(labels, minlength=len(CONDITION_LABELS))
    class_weights = torch.FloatTensor(
        1.0 / (class_counts / class_counts.sum() + 1e-6)
    ).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # Adam optimiser with weight decay (L2 regularisation)
    optimizer = optim.Adam(
        model.parameters(),
        lr=TRAINING_CONFIG["learning_rate"],
        weight_decay=TRAINING_CONFIG["weight_decay"]
    )

    # Reduce learning rate when validation loss plateaus
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=3, verbose=True
    )

    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

    best_val_loss   = float("inf")
    patience_counter = 0
    history = {"train_loss": [], "val_loss": [], "val_accuracy": []}

    print("\nStarting training...")
    print("=" * 60)

    for epoch in range(TRAINING_CONFIG["num_epochs"]):

        # ── Training phase ──
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total   = 0

        for batch_idx, (images, targets) in enumerate(train_loader):
            images  = images.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss    = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            train_loss    += loss.item()
            _, predicted   = outputs.max(1)
            train_total   += targets.size(0)
            train_correct += predicted.eq(targets).sum().item()

            if (batch_idx + 1) % 100 == 0:
                print(f"  Epoch {epoch+1} | Batch {batch_idx+1}/{len(train_loader)} "
                      f"| Loss: {loss.item():.4f}")

        avg_train_loss = train_loss / len(train_loader)
        train_accuracy = 100.0 * train_correct / train_total

        # ── Validation phase ──
        model.eval()
        val_loss    = 0.0
        val_correct = 0
        val_total   = 0

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

        scheduler.step(avg_val_loss)

        history["train_loss"].append(avg_train_loss)
        history["val_loss"].append(avg_val_loss)
        history["val_accuracy"].append(val_accuracy)

        print(f"\nEpoch {epoch+1}/{TRAINING_CONFIG['num_epochs']}")
        print(f"  Train — Loss: {avg_train_loss:.4f} | Acc: {train_accuracy:.2f}%")
        print(f"  Val   — Loss: {avg_val_loss:.4f} | Acc: {val_accuracy:.2f}%")

        # Checkpoint and early stopping
        if avg_val_loss < best_val_loss:
            best_val_loss    = avg_val_loss
            patience_counter = 0
            torch.save({
                "epoch":                epoch + 1,
                "model_state_dict":     model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_loss":             best_val_loss,
                "val_accuracy":         val_accuracy,
                "label_to_idx":         label_to_idx,
                "condition_labels":     CONDITION_LABELS,
            }, MODEL_SAVE_PATH)
            print(f"  Checkpoint saved (val_loss: {best_val_loss:.4f})")
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

    all_preds   = []
    all_targets = []

    with torch.no_grad():
        for images, targets in test_loader:
            images  = images.to(device)
            outputs = model(images)
            _, predicted = outputs.max(1)
            all_preds.extend(predicted.cpu().numpy())
            all_targets.extend(targets.numpy())

    print("\nClassification Report:")
    print(classification_report(all_targets, all_preds, target_names=CONDITION_LABELS))

    print("Confusion Matrix:")
    print(confusion_matrix(all_targets, all_preds))

    # Save label map
    with open(LABEL_MAP_PATH, "w") as f:
        json.dump({
            "label_to_idx":     label_to_idx,
            "idx_to_label":     {str(v): k for k, v in label_to_idx.items()},
            "condition_labels": CONDITION_LABELS,
            "datasets_used":    {
                "NIH Chest X-Ray14": nih_dir is not None,
                "CheXpert":          chexpert_dir is not None,
                "MURA":              mura_dir is not None,
                "VinDr-CXR":         vindr_dir is not None,
            }
        }, f, indent=2)

    print(f"\nTraining complete.")
    print(f"Model saved: {MODEL_SAVE_PATH}")
    print(f"Label map saved: {LABEL_MAP_PATH}")
    return history


# ============================================================
# INFERENCE FUNCTION
# ============================================================

def predict_xray(image_bytes: bytes, image_type: str = "image/jpeg") -> dict:
    """
    Runs inference on an X-ray image using the trained ResNet-50.

    This function would replace the Claude Vision API call in
    xray_analyzer.py in a GPU-enabled production environment.

    In the current deployment, xray_analyzer.py uses Claude Vision API
    because:
    1. The ResNet model requires GPU resources for training
    2. The Railway/Render hosting environment has no GPU
    3. Claude Vision provides superior medical imaging analysis
       for X-ray types not covered by the training datasets

    Args:
        image_bytes: Raw image bytes from the uploaded X-ray
        image_type:  MIME type of the image

    Returns:
        dict: Structured findings matching the NexRay AI API format
    """
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch not available for inference.")

    if not os.path.exists(MODEL_SAVE_PATH):
        raise RuntimeError(
            f"Trained model not found at {MODEL_SAVE_PATH}. "
            "Run train_model() first with at least one dataset."
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    checkpoint = torch.load(MODEL_SAVE_PATH, map_location=device)
    model = build_model(num_classes=len(CONDITION_LABELS))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    model.to(device)

    _, val_transform = get_transforms()
    import io
    image        = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_tensor = val_transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs       = model(image_tensor)
        probabilities = torch.softmax(outputs, dim=1).squeeze()

    condition_scores = [
        {
            "condition":   CONDITION_LABELS[i],
            "confidence":  round(probabilities[i].item() * 100, 1),
            "description": _get_condition_description(CONDITION_LABELS[i])
        }
        for i in range(len(CONDITION_LABELS))
    ]

    condition_scores.sort(key=lambda x: x["confidence"], reverse=True)
    top_3   = condition_scores[:3]
    urgency = _get_urgency(top_3[0]["condition"], top_3[0]["confidence"])

    return {
        "body_region": _detect_body_region(top_3[0]["condition"]),
        "findings":    top_3,
        "overall_impression": (
            f"ResNet-50 classifier trained on NIH, CheXpert, MURA and VinDr datasets "
            f"identifies {top_3[0]['condition']} as the most likely finding "
            f"({top_3[0]['confidence']}% confidence). Clinical correlation recommended."
        ),
        "recommended_tests":  _get_recommended_tests(top_3[0]["condition"]),
        "suggested_treatment":_get_suggested_treatment(top_3[0]["condition"]),
        "next_steps": [
            "Correlate findings with clinical presentation",
            "Consult radiologist for formal report",
            "Consider additional imaging if indicated"
        ],
        "urgency": urgency,
        "model":   "ResNet-50 fine-tuned on NIH + CheXpert + MURA + VinDr",
        "disclaimer": (
            "These findings are generated by a fine-tuned ResNet-50 model and must "
            "be verified by a qualified radiologist before any clinical action."
        )
    }


def _detect_body_region(condition: str) -> str:
    if condition in ["Fracture", "Abnormal Musculoskeletal"]:
        return "Musculoskeletal"
    return "Chest (Thorax)"


def _get_condition_description(condition: str) -> str:
    descriptions = {
        "Normal":                  "No significant radiological abnormality detected.",
        "Pneumonia":               "Increased opacity consistent with alveolar consolidation.",
        "Tuberculosis":            "Infiltrates or nodular opacities consistent with pulmonary TB.",
        "Pleural Effusion":        "Blunting of costophrenic angle suggesting pleural fluid.",
        "Cardiomegaly":            "Increased cardiothoracic ratio suggesting cardiac enlargement.",
        "Fracture":                "Cortical disruption or fracture line detected.",
        "Abnormal Musculoskeletal":"Musculoskeletal abnormality detected — further assessment needed.",
    }
    return descriptions.get(condition, "Radiological finding detected.")


def _get_urgency(condition: str, confidence: float) -> str:
    if condition == "Tuberculosis":
        return "Urgent"
    if condition in ["Pleural Effusion", "Cardiomegaly"] and confidence > 70:
        return "Urgent"
    if condition == "Pneumonia" and confidence > 80:
        return "Urgent"
    if condition == "Fracture" and confidence > 70:
        return "Urgent"
    return "Routine"


def _get_recommended_tests(condition: str) -> list:
    tests = {
        "Normal":                  ["Follow up if symptoms persist", "Repeat CXR if clinically indicated"],
        "Pneumonia":               ["Sputum culture", "CBC with differential", "Blood culture", "CRP/ESR"],
        "Tuberculosis":            ["Sputum AFB smear x3", "GeneXpert MTB/RIF", "Mantoux test", "HIV test"],
        "Pleural Effusion":        ["Chest ultrasound", "Thoracocentesis for fluid analysis", "LDH, protein, glucose"],
        "Cardiomegaly":            ["ECG", "Echocardiogram", "BNP/NT-proBNP", "Renal function"],
        "Fracture":                ["Repeat X-ray (AP and lateral)", "CT scan if complex fracture", "Neurovascular assessment"],
        "Abnormal Musculoskeletal":["Orthopaedic referral", "MRI if soft tissue injury suspected", "CT scan"],
    }
    return tests.get(condition, ["Clinical assessment", "Further imaging as indicated"])


def _get_suggested_treatment(condition: str) -> list:
    treatments = {
        "Normal":                  ["No specific treatment required", "Symptomatic management"],
        "Pneumonia":               ["Amoxicillin-clavulanate or ceftriaxone", "Oxygen therapy if SpO2 <94%"],
        "Tuberculosis":            ["HRZE regimen after confirmation", "Patient isolation", "Contact tracing"],
        "Pleural Effusion":        ["Treat underlying cause", "Thoracocentesis if large or symptomatic"],
        "Cardiomegaly":            ["Furosemide", "ACE inhibitors/ARBs", "Treat underlying cause"],
        "Fracture":                ["Immobilisation (cast or splint)", "Analgesia", "Orthopaedic referral"],
        "Abnormal Musculoskeletal":["Orthopaedic referral", "Analgesia", "Rest and immobilisation"],
    }
    return treatments.get(condition, ["Specialist referral", "Symptomatic management"])


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # --------------------------------------------------------
    # To train the model download the datasets from:
    # NIH:      https://www.kaggle.com/datasets/nih-chest-xrays/data
    # CheXpert: https://stanfordmlgroup.github.io/competitions/chexpert
    # MURA:     https://stanfordmlgroup.github.io/competitions/mura
    # VinDr:    https://www.kaggle.com/datasets/vinbigdata/vinbigdata-chest-xray-abnormalities-detection
    #
    # Set the directory paths below and run:
    # python -m app.services.resnet_trainer
    #
    # Recommended: Google Colab with free T4 GPU
    # Expected training time: 4-8 hours on T4 GPU
    # Expected accuracy: 75-85% on 7-class classification
    # --------------------------------------------------------

    history = train_model(
        nih_dir=      os.environ.get("NIH_DATA_DIR"),
        chexpert_dir= os.environ.get("CHEXPERT_DATA_DIR"),
        mura_dir=     os.environ.get("MURA_DATA_DIR"),
        vindr_dir=    os.environ.get("VINDR_DATA_DIR"),
    )