"""
Data preprocessing utilities for football player detection training.
"""

import os
import cv2
import json
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any
import random


class FootballDataPreprocessor:
    """Handles data preprocessing for YOLO training."""

    def __init__(self, dataset_path: str, output_path: str):
        self.dataset_path = Path(dataset_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

    def resize_image(self, image: np.ndarray, target_size: Tuple[int, int] = (640, 640)) -> np.ndarray:
        """Resize image while maintaining aspect ratio."""
        h, w = image.shape[:2]
        scale = min(target_size[0] / w, target_size[1] / h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(image, (new_w, new_h))

        # Pad to target size
        pad_w = target_size[0] - new_w
        pad_h = target_size[1] - new_h

        top = pad_h // 2
        bottom = pad_h - top
        left = pad_w // 2
        right = pad_w - left

        padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(0, 0, 0))

        return padded, scale, (left, top)

    def augment_image(self, image: np.ndarray, annotations: List[Dict]) -> Tuple[np.ndarray, List[Dict]]:
        """Apply data augmentation to image and adjust annotations."""
        h, w = image.shape[:2]

        # Random brightness/contrast
        if random.random() > 0.5:
            alpha = random.uniform(0.8, 1.2)  # Contrast
            beta = random.randint(-20, 20)    # Brightness
            image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

        # Random horizontal flip
        if random.random() > 0.5:
            image = cv2.flip(image, 1)
            for ann in annotations:
                ann['x'] = w - ann['x'] - ann['width']

        # Random rotation (small angles)
        if random.random() > 0.7:
            angle = random.uniform(-5, 5)
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            image = cv2.warpAffine(image, matrix, (w, h))

            # Note: For simplicity, we keep original annotations for small rotations
            # In production, you'd want to transform the bounding boxes too

        return image, annotations

    def convert_to_yolo_format(self, annotations: List[Dict], image_width: int, image_height: int) -> List[str]:
        """Convert annotations to YOLO format."""
        yolo_annotations = []

        for ann in annotations:
            # Normalize coordinates
            x_center = (ann['x'] + ann['width'] / 2) / image_width
            y_center = (ann['y'] + ann['height'] / 2) / image_height
            width = ann['width'] / image_width
            height = ann['height'] / image_height

            # Class ID (0 for player)
            class_id = 0

            yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
            yolo_annotations.append(yolo_line)

        return yolo_annotations

    def process_dataset(self, train_split: float = 0.8, augment: bool = True):
        """Process the entire dataset for YOLO training."""
        # Create output directories
        train_dir = self.output_path / "train"
        val_dir = self.output_path / "val"

        for split_dir in [train_dir, val_dir]:
            (split_dir / "images").mkdir(parents=True, exist_ok=True)
            (split_dir / "labels").mkdir(parents=True, exist_ok=True)

        # Process all images
        image_files = list(self.dataset_path.glob("*.jpg")) + list(self.dataset_path.glob("*.png"))
        random.shuffle(image_files)

        train_count = int(len(image_files) * train_split)

        for i, image_path in enumerate(image_files):
            # Determine split
            is_train = i < train_count
            split_dir = train_dir if is_train else val_dir

            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                continue

            # Load annotations (assuming they exist)
            annotation_path = image_path.with_suffix('.json')
            if not annotation_path.exists():
                continue

            with open(annotation_path, 'r') as f:
                annotations = json.load(f)

            # Apply augmentation for training set
            if is_train and augment:
                image, annotations = self.augment_image(image, annotations)

            # Resize image
            processed_image, scale, offset = self.resize_image(image)

            # Adjust annotations for resize
            for ann in annotations:
                ann['x'] = int(ann['x'] * scale) + offset[0]
                ann['y'] = int(ann['y'] * scale) + offset[1]
                ann['width'] = int(ann['width'] * scale)
                ann['height'] = int(ann['height'] * scale)

            # Convert to YOLO format
            h, w = processed_image.shape[:2]
            yolo_annotations = self.convert_to_yolo_format(annotations, w, h)

            # Save processed files
            base_name = image_path.stem

            # Save image
            cv2.imwrite(str(split_dir / "images" / f"{base_name}.jpg"), processed_image)

            # Save annotations
            with open(split_dir / "labels" / f"{base_name}.txt", 'w') as f:
                f.write('\n'.join(yolo_annotations))

        print(f"Dataset processing complete!")
        print(f"Train images: {len(list((train_dir / 'images').glob('*.jpg')))}")
        print(f"Val images: {len(list((val_dir / 'images').glob('*.jpg')))}")


def create_dataset_yaml(output_path: str, dataset_name: str = "football_players"):
    """Create YOLO dataset configuration file."""
    yaml_content = f"""# Football player detection dataset
path: {output_path}
train: train/images
val: val/images

# Classes
nc: 1  # number of classes
names: ['player']  # class names
"""

    with open(Path(output_path) / "dataset.yaml", 'w') as f:
        f.write(yaml_content)

    print(f"Dataset YAML created at {output_path}/dataset.yaml")


if __name__ == "__main__":
    # Example usage
    preprocessor = FootballDataPreprocessor(
        dataset_path="raw_data",
        output_path="processed_dataset"
    )

    preprocessor.process_dataset(train_split=0.8, augment=True)
    create_dataset_yaml("processed_dataset")