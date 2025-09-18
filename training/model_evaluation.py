"""
Model evaluation utilities for football player detection.
"""

import cv2
import torch
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any
import matplotlib.pyplot as plt
from ultralytics import YOLO
import json


class ModelEvaluator:
    """Evaluates YOLO model performance on football player detection."""

    def __init__(self, model_path: str, test_data_path: str):
        self.model = YOLO(model_path)
        self.test_data_path = Path(test_data_path)
        self.results = {}

    def calculate_iou(self, box1: List[float], box2: List[float]) -> float:
        """Calculate Intersection over Union (IoU) between two bounding boxes."""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2

        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)

        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0

        intersection = (x2_i - x1_i) * (y2_i - y1_i)

        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0.0

    def evaluate_single_image(self, image_path: str, ground_truth_path: str, confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """Evaluate model performance on a single image."""
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {"error": "Could not load image"}

        # Get predictions
        results = self.model(image, conf=confidence_threshold)
        predictions = []

        if len(results) > 0 and len(results[0].boxes) > 0:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()

            for box, conf in zip(boxes, confidences):
                predictions.append({
                    "bbox": box.tolist(),
                    "confidence": float(conf)
                })

        # Load ground truth
        try:
            with open(ground_truth_path, 'r') as f:
                ground_truth = json.load(f)
        except:
            return {"error": "Could not load ground truth"}

        # Calculate metrics
        gt_boxes = []
        for gt in ground_truth:
            x1 = gt['x']
            y1 = gt['y']
            x2 = x1 + gt['width']
            y2 = y1 + gt['height']
            gt_boxes.append([x1, y1, x2, y2])

        pred_boxes = [pred["bbox"] for pred in predictions]

        # Match predictions to ground truth using IoU
        iou_threshold = 0.5
        matched_predictions = set()
        matched_ground_truth = set()

        for i, gt_box in enumerate(gt_boxes):
            best_iou = 0
            best_pred = -1

            for j, pred_box in enumerate(pred_boxes):
                if j in matched_predictions:
                    continue

                iou = self.calculate_iou(gt_box, pred_box)
                if iou > best_iou and iou >= iou_threshold:
                    best_iou = iou
                    best_pred = j

            if best_pred != -1:
                matched_predictions.add(best_pred)
                matched_ground_truth.add(i)

        true_positives = len(matched_predictions)
        false_positives = len(pred_boxes) - true_positives
        false_negatives = len(gt_boxes) - len(matched_ground_truth)

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return {
            "predictions": len(predictions),
            "ground_truth": len(ground_truth),
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score
        }

    def evaluate_dataset(self, confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """Evaluate model on entire test dataset."""
        image_files = list(self.test_data_path.glob("*.jpg")) + list(self.test_data_path.glob("*.png"))

        total_tp = 0
        total_fp = 0
        total_fn = 0
        total_predictions = 0
        total_ground_truth = 0

        results_per_image = []

        for image_path in image_files:
            gt_path = image_path.with_suffix('.json')
            if not gt_path.exists():
                continue

            result = self.evaluate_single_image(str(image_path), str(gt_path), confidence_threshold)

            if "error" not in result:
                total_tp += result["true_positives"]
                total_fp += result["false_positives"]
                total_fn += result["false_negatives"]
                total_predictions += result["predictions"]
                total_ground_truth += result["ground_truth"]
                results_per_image.append(result)

        # Calculate overall metrics
        overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        overall_f1 = 2 * (overall_precision * overall_recall) / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0

        return {
            "total_images": len(results_per_image),
            "total_predictions": total_predictions,
            "total_ground_truth": total_ground_truth,
            "overall_precision": overall_precision,
            "overall_recall": overall_recall,
            "overall_f1_score": overall_f1,
            "per_image_results": results_per_image
        }

    def visualize_predictions(self, image_path: str, output_path: str = None, confidence_threshold: float = 0.5):
        """Visualize model predictions on an image."""
        image = cv2.imread(image_path)
        if image is None:
            print("Could not load image")
            return

        # Get predictions
        results = self.model(image, conf=confidence_threshold)

        # Draw bounding boxes
        if len(results) > 0 and len(results[0].boxes) > 0:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()

            for box, conf in zip(boxes, confidences):
                x1, y1, x2, y2 = map(int, box)

                # Draw rectangle
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Draw confidence score
                label = f"Player: {conf:.2f}"
                cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Save or display
        if output_path:
            cv2.imwrite(output_path, image)
            print(f"Visualization saved to {output_path}")
        else:
            cv2.imshow("Predictions", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def generate_evaluation_report(self, output_file: str = "evaluation_report.json"):
        """Generate comprehensive evaluation report."""
        print("Evaluating model performance...")

        # Test different confidence thresholds
        thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        threshold_results = {}

        for threshold in thresholds:
            print(f"Testing confidence threshold: {threshold}")
            result = self.evaluate_dataset(confidence_threshold=threshold)
            threshold_results[threshold] = result

        # Find best threshold
        best_threshold = max(threshold_results.keys(),
                           key=lambda t: threshold_results[t]["overall_f1_score"])

        report = {
            "best_threshold": best_threshold,
            "best_performance": threshold_results[best_threshold],
            "threshold_analysis": threshold_results,
            "model_path": str(self.model.model_name if hasattr(self.model, 'model_name') else 'unknown'),
            "test_dataset": str(self.test_data_path)
        }

        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Evaluation report saved to {output_file}")
        print(f"Best F1 score: {threshold_results[best_threshold]['overall_f1_score']:.3f} at threshold {best_threshold}")

        return report


if __name__ == "__main__":
    # Example usage
    evaluator = ModelEvaluator(
        model_path="best_model.pt",
        test_data_path="test_images"
    )

    # Generate evaluation report
    report = evaluator.generate_evaluation_report()

    # Visualize some predictions
    test_images = list(Path("test_images").glob("*.jpg"))
    if test_images:
        evaluator.visualize_predictions(
            str(test_images[0]),
            "prediction_example.jpg"
        )