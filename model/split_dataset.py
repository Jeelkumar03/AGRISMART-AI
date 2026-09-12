import argparse
import random
import shutil
from pathlib import Path


def split_dataset(source, destination, val_ratio=0.2, seed=42):
    source = Path(source)
    destination = Path(destination)

    random.seed(seed)

    if not source.exists():
        raise FileNotFoundError(f"Dataset folder not found: {source}")

    classes = sorted(
        folder for folder in source.iterdir()
        if folder.is_dir()
    )

    if not classes:
        raise RuntimeError("No class folders found in dataset.")

    train_dir = destination / "train"
    val_dir = destination / "val"

    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)

    for class_dir in classes:
        images = [
            f for f in class_dir.iterdir()
            if f.is_file()
        ]

        random.shuffle(images)

        val_count = int(len(images) * val_ratio)

        val_images = images[:val_count]
        train_images = images[val_count:]

        (train_dir / class_dir.name).mkdir(parents=True, exist_ok=True)
        (val_dir / class_dir.name).mkdir(parents=True, exist_ok=True)

        for image in train_images:
            shutil.copy2(
                image,
                train_dir / class_dir.name / image.name
            )

        for image in val_images:
            shutil.copy2(
                image,
                val_dir / class_dir.name / image.name
            )

        print(
            f"{class_dir.name}: "
            f"{len(train_images)} train, "
            f"{len(val_images)} val"
        )

    print("\nDataset split complete!")
    print(f"Train: {train_dir}")
    print(f"Validation: {val_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source",
        default=r"D:\SIH\Agrismart-AI\archive\plantvillage dataset\color"
    )

    parser.add_argument(
        "--destination",
        default="data"
    )

    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.2
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42
    )

    args = parser.parse_args()

    split_dataset(
        args.source,
        args.destination,
        args.val_ratio,
        args.seed
    )