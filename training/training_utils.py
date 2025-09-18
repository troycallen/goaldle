"""
Training utilities and helper functions for football player detection.
"""

import os
import yaml
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from ultralytics import YOLO
import torch
import wandb


class TrainingConfig:
    """Configuration class for training parameters."""

    def __init__(self):
        self.epochs = 100
        self.batch_size = 16
        self.img_size = 640
        self.learning_rate = 0.01
        self.patience = 10
        self.save_period = 10
        self.workers = 8
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.project_name = 'football_detection'
        self.experiment_name = 'yolov8_players'

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'epochs': self.epochs,
            'batch': self.batch_size,
            'imgsz': self.img_size,
            'lr0': self.learning_rate,
            'patience': self.patience,
            'save_period': self.save_period,
            'workers': self.workers,
            'device': self.device,
            'project': self.project_name,
            'name': self.experiment_name
        }


class TrainingLogger:
    """Custom logging for training process."""

    def __init__(self, log_dir: str = "training_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / 'training.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def log_training_start(self, config: TrainingConfig, dataset_info: Dict[str, Any]):
        """Log training start information."""
        self.logger.info("=" * 50)
        self.logger.info("TRAINING STARTED")
        self.logger.info("=" * 50)
        self.logger.info(f"Device: {config.device}")
        self.logger.info(f"Epochs: {config.epochs}")
        self.logger.info(f"Batch size: {config.batch_size}")
        self.logger.info(f"Image size: {config.img_size}")
        self.logger.info(f"Learning rate: {config.learning_rate}")
        self.logger.info(f"Dataset: {dataset_info}")

    def log_epoch(self, epoch: int, metrics: Dict[str, float]):
        """Log epoch metrics."""
        metric_str = " | ".join([f"{k}: {v:.4f}" for k, v in metrics.items()])
        self.logger.info(f"Epoch {epoch}: {metric_str}")

    def log_training_complete(self, best_metrics: Dict[str, float], model_path: str):
        """Log training completion."""
        self.logger.info("=" * 50)
        self.logger.info("TRAINING COMPLETED")
        self.logger.info("=" * 50)
        self.logger.info(f"Best model saved to: {model_path}")
        self.logger.info("Best metrics:")
        for metric, value in best_metrics.items():
            self.logger.info(f"  {metric}: {value:.4f}")


class ModelTrainer:
    """Main training class for football player detection models."""

    def __init__(self, config: TrainingConfig, use_wandb: bool = False):
        self.config = config
        self.logger = TrainingLogger()
        self.use_wandb = use_wandb

        if self.use_wandb:
            wandb.init(
                project=config.project_name,
                name=config.experiment_name,
                config=config.to_dict()
            )

    def prepare_model(self, pretrained_model: str = "yolov8n.pt") -> YOLO:
        """Load and prepare YOLO model for training."""
        self.logger.logger.info(f"Loading pretrained model: {pretrained_model}")

        # Download pretrained model if it doesn't exist
        model = YOLO(pretrained_model)

        self.logger.logger.info(f"Model loaded successfully")
        self.logger.logger.info(f"Model parameters: {sum(p.numel() for p in model.model.parameters()):,}")

        return model

    def train(self, model: YOLO, dataset_yaml: str, output_dir: str = "runs/train") -> str:
        """Train the model."""
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Log dataset info
        with open(dataset_yaml, 'r') as f:
            dataset_config = yaml.safe_load(f)

        self.logger.log_training_start(self.config, dataset_config)

        # Start training
        try:
            results = model.train(
                data=dataset_yaml,
                **self.config.to_dict()
            )

            # Get best model path
            best_model_path = results.save_dir / "weights" / "best.pt"

            # Log completion
            if hasattr(results, 'results_dict'):
                best_metrics = results.results_dict
            else:
                best_metrics = {"training": "completed"}

            self.logger.log_training_complete(best_metrics, str(best_model_path))

            return str(best_model_path)

        except Exception as e:
            self.logger.logger.error(f"Training failed: {str(e)}")
            raise

        finally:
            if self.use_wandb:
                wandb.finish()

    def resume_training(self, checkpoint_path: str, dataset_yaml: str) -> str:
        """Resume training from checkpoint."""
        self.logger.logger.info(f"Resuming training from: {checkpoint_path}")

        model = YOLO(checkpoint_path)
        return self.train(model, dataset_yaml)

    def validate_model(self, model_path: str, dataset_yaml: str) -> Dict[str, float]:
        """Validate trained model."""
        self.logger.logger.info("Starting model validation...")

        model = YOLO(model_path)
        results = model.val(data=dataset_yaml)

        # Extract validation metrics
        metrics = {}
        if hasattr(results, 'results_dict'):
            metrics = results.results_dict

        self.logger.logger.info("Validation completed")
        for metric, value in metrics.items():
            self.logger.logger.info(f"  {metric}: {value:.4f}")

        return metrics


class DatasetManager:
    """Manages dataset organization and validation."""

    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)

    def validate_dataset_structure(self) -> bool:
        """Validate YOLO dataset structure."""
        required_dirs = ['train/images', 'train/labels', 'val/images', 'val/labels']
        required_files = ['dataset.yaml']

        for dir_name in required_dirs:
            dir_path = self.dataset_path / dir_name
            if not dir_path.exists():
                print(f"Missing directory: {dir_path}")
                return False

        for file_name in required_files:
            file_path = self.dataset_path / file_name
            if not file_path.exists():
                print(f"Missing file: {file_path}")
                return False

        print("Dataset structure validation passed")
        return True

    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        stats = {}

        for split in ['train', 'val']:
            images_dir = self.dataset_path / split / 'images'
            labels_dir = self.dataset_path / split / 'labels'

            if images_dir.exists() and labels_dir.exists():
                num_images = len(list(images_dir.glob('*.jpg'))) + len(list(images_dir.glob('*.png')))
                num_labels = len(list(labels_dir.glob('*.txt')))

                stats[split] = {
                    'images': num_images,
                    'labels': num_labels,
                    'missing_labels': num_images - num_labels
                }

        return stats


def create_training_script(dataset_path: str, output_path: str = "train_model.py"):
    """Generate a training script with current configuration."""
    script_content = f'''#!/usr/bin/env python3
"""
Auto-generated training script for football player detection.
"""

from training_utils import TrainingConfig, ModelTrainer, DatasetManager

def main():
    # Configuration
    config = TrainingConfig()
    config.epochs = 100
    config.batch_size = 16
    config.img_size = 640
    config.learning_rate = 0.01

    # Dataset path
    dataset_path = "{dataset_path}"
    dataset_yaml = f"{{dataset_path}}/dataset.yaml"

    # Validate dataset
    dataset_manager = DatasetManager(dataset_path)
    if not dataset_manager.validate_dataset_structure():
        print("Dataset validation failed!")
        return

    # Print dataset stats
    stats = dataset_manager.get_dataset_stats()
    print("Dataset Statistics:")
    for split, data in stats.items():
        print(f"  {{split}}: {{data['images']}} images, {{data['labels']}} labels")

    # Initialize trainer
    trainer = ModelTrainer(config, use_wandb=False)

    # Prepare model
    model = trainer.prepare_model("yolov8n.pt")

    # Train model
    best_model_path = trainer.train(model, dataset_yaml)

    # Validate final model
    validation_metrics = trainer.validate_model(best_model_path, dataset_yaml)

    print(f"Training completed! Best model saved to: {{best_model_path}}")

if __name__ == "__main__":
    main()
'''

    with open(output_path, 'w') as f:
        f.write(script_content)

    print(f"Training script created: {output_path}")


if __name__ == "__main__":
    # Example usage
    config = TrainingConfig()
    trainer = ModelTrainer(config)

    # Create a sample training script
    create_training_script("processed_dataset")