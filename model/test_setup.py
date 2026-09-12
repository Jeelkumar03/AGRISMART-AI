from pathlib import Path
import sys

print("=== AgriSmart AI - ML Setup Test ===")

# Python
print(f"Python version: {sys.version}")

# PyTorch
try:
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("GPU: Not available - CPU will be used locally")

except Exception as e:
    print(f"PyTorch error: {e}")


# Dataset paths
train_dir = Path("data/train")
val_dir = Path("data/val")

print(f"\nTrain folder exists: {train_dir.exists()}")
print(f"Validation folder exists: {val_dir.exists()}")

if train_dir.exists() and val_dir.exists():

    train_classes = sorted(
        folder.name for folder in train_dir.iterdir()
        if folder.is_dir()
    )

    val_classes = sorted(
        folder.name for folder in val_dir.iterdir()
        if folder.is_dir()
    )

    print(f"Train classes: {len(train_classes)}")
    print(f"Validation classes: {len(val_classes)}")

    if train_classes == val_classes:
        print("Class check: PASS")
    else:
        print("Class check: FAIL")

else:
    print("Dataset folders are missing.")

print("\n=== Setup test complete ===")