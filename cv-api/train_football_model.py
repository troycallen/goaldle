import os
from ultralytics import YOLO

def train_football_model():
    """Train YOLOv8 model on football dataset using downloaded data"""
    
    dataset_path = "football_dataset"
    dataset_config = os.path.join(dataset_path, 'data.yaml')
    
    if not os.path.exists(dataset_config):
        print(f"Could not find data.yaml in {dataset_path}")
        print("Make sure the football dataset is downloaded and extracted")
        return None
    
    print(f"Using dataset config: {dataset_config}")
    
    # Load a pretrained YOLOv8 model (detection model - dataset has bounding boxes only)
    model = YOLO('yolov8m.pt')  # Use detection model for bounding box dataset
    
    # Train the model
    print("Starting training...")
    results = model.train(
        data=dataset_config,
        epochs=20,  # Reduced for CPU training
        imgsz=640,
        batch=4,    # Smaller batch for CPU training
        device='cpu',   # Use CPU since CUDA not available
        patience=10,
        save_period=5,
        name='football_players_detect',
        exist_ok=True  # Allow overwriting existing runs
    )
    
    return model

def main():
    print("Training football player detection model...")
    
    model = train_football_model()
    
    if model:
        print("Training completed!")
        print("New model saved in: runs/detect/football_players_detect/weights/best.pt")
        print("\nTo use your trained model, update main.py:")
        print("self.model = YOLO('runs/detect/football_players_detect/weights/best.pt')")
    else:
        print("Training failed. Check that football_dataset folder exists.")

if __name__ == "__main__":
    main()