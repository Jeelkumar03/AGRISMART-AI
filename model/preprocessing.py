"""Shared data loading and preprocessing utilities.

Expected folder structure:
    data/train/<class_name>/*.jpg
    data/val/<class_name>/*.jpg
"""
from pathlib import Path

from torch.utils.data import DataLoader
from torchvision import datasets, transforms

IMG_SIZE = 224
BATCH_SIZE = 32

# Training gets augmentation (helps the model generalize to messy field photos).
# GaussianBlur + RandomErasing simulate phone-camera noise and partial occlusion.
TRAIN_TRANSFORMS = transforms.Compose([
    transforms.RandomResizedCrop(IMG_SIZE, scale=(0.75, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.02),
    transforms.RandomApply([transforms.GaussianBlur(kernel_size=3)], p=0.15),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    transforms.RandomErasing(p=0.15, scale=(0.02, 0.1)),
])

# Validation/prediction use fixed, non-random transforms so results are reproducible.
EVAL_TRANSFORMS = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def get_dataloaders(data_dir="data", batch_size=BATCH_SIZE):
    train_dir = Path(data_dir) / "train"
    val_dir = Path(data_dir) / "val"
    if not train_dir.exists():
        raise FileNotFoundError(
            f"{train_dir} not found. Expected data/train/<class_name>/*.jpg"
        )
    if not val_dir.exists():
        raise FileNotFoundError(
            f"{val_dir} not found. Expected data/val/<class_name>/*.jpg"
        )

    train_ds = datasets.ImageFolder(train_dir, transform=TRAIN_TRANSFORMS)
    val_ds = datasets.ImageFolder(val_dir, transform=EVAL_TRANSFORMS)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=2)

    return train_loader, val_loader, train_ds.classes


def inspect_dataset(data_dir="data"):
    """Print image count per class for train and val splits. Run directly for a quick dataset report."""
    for split in ["train", "val"]:
        split_dir = Path(data_dir) / split
        if not split_dir.exists():
            print(f"{split_dir} not found, skipping.")
            continue
        print(f"\n{split.upper()} SET")
        print("-" * 40)
        total = 0
        for class_dir in sorted(p for p in split_dir.iterdir() if p.is_dir()):
            count = len(list(class_dir.glob("*.*")))
            print(f"{class_dir.name:30s} {count:>6d}")
            total += count
        print("-" * 40)
        print(f"{'TOTAL':30s} {total:>6d}")


if __name__ == "__main__":
    inspect_dataset()
