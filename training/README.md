# Football Player Detection Training

This directory contains training scripts and utilities for developing YOLOv8 models to detect football players in video footage.

## Files Overview

- `train_football_model.py` - Main training script (moved from cv-api)
- `data_preprocessing.py` - Data preprocessing and augmentation utilities
- `model_evaluation.py` - Model evaluation and performance metrics
- `training_utils.py` - Training configuration and helper functions
- `requirements.txt` - Python dependencies for training

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare your dataset:**
   ```python
   from data_preprocessing import FootballDataPreprocessor

   preprocessor = FootballDataPreprocessor("raw_data", "processed_dataset")
   preprocessor.process_dataset(train_split=0.8, augment=True)
   ```

3. **Train a model:**
   ```python
   from training_utils import TrainingConfig, ModelTrainer

   config = TrainingConfig()
   trainer = ModelTrainer(config)
   model = trainer.prepare_model("yolov8n.pt")
   best_model = trainer.train(model, "processed_dataset/dataset.yaml")
   ```

4. **Evaluate performance:**
   ```python
   from model_evaluation import ModelEvaluator

   evaluator = ModelEvaluator("best_model.pt", "test_images")
   report = evaluator.generate_evaluation_report()
   ```

## Training Configuration

The `TrainingConfig` class allows you to customize training parameters:

```python
config = TrainingConfig()
config.epochs = 100          # Number of training epochs
config.batch_size = 16       # Batch size
config.img_size = 640        # Input image size
config.learning_rate = 0.01  # Learning rate
config.patience = 10         # Early stopping patience
```

## Dataset Structure

Expected YOLO dataset structure:
```
processed_dataset/
├── dataset.yaml
├── train/
│   ├── images/
│   └── labels/
└── val/
    ├── images/
    └── labels/
```

## Model Evaluation

The evaluation system provides comprehensive metrics:
- Precision, Recall, F1-score
- IoU-based matching
- Confidence threshold analysis
- Visual prediction outputs

## GPU Training

For faster training with CUDA:
```bash
# Check if CUDA is available
python -c "import torch; print(torch.cuda.is_available())"

# Training will automatically use GPU if available
```
