"""Object detection engine using YOLOv8."""

import numpy as np
from loguru import logger


class ObjectDetector:
    """Object detection using YOLOv8."""

    def __init__(self, model_path='yolov8n.pt', confidence=0.5, classes=None):
        self.model_path = model_path
        self.confidence = confidence
        self.classes = classes
        self.model = None
        self._initialize()

    def _initialize(self):
        """Initialize YOLO model."""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            logger.info(f"YOLO model loaded: {self.model_path}")
        except ImportError:
            logger.warning("ultralytics not available, object detection disabled")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None

    def detect(self, image):
        """Detect objects in image.

        Args:
            image: numpy array (BGR or BGRA format)

        Returns:
            list of dicts with 'class', 'confidence', 'bbox' keys
        """
        if self.model is None:
            return []

        try:
            if image.shape[2] == 4:
                image = image[:, :, :3]
            results = self.model(image, conf=self.confidence, verbose=False)
            return self._parse_results(results)
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []

    def _parse_results(self, results):
        """Parse YOLO results into standardized format."""
        parsed = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for i in range(len(boxes)):
                box = boxes[i]
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = box.conf[0].item()
                class_id = int(box.cls[0].item())
                class_name = result.names[class_id]

                if self.classes and class_name not in self.classes:
                    continue

                parsed.append({
                    'class': class_name,
                    'class_id': class_id,
                    'confidence': confidence,
                    'bbox': [x1, y1, x2, y2]
                })

        return parsed

    def detect_region(self, image, region):
        """Detect objects in a specific region.

        Args:
            image: full image
            region: [x, y, width, height]

        Returns:
            list of detected objects with adjusted coordinates
        """
        x, y, w, h = region
        cropped = image[y:y+h, x:x+w]
        results = self.detect(cropped)

        for item in results:
            item['bbox'][0] += x
            item['bbox'][1] += y
            item['bbox'][2] += x
            item['bbox'][3] += y

        return results

    def get_object_counts(self, image):
        """Get count of each object class in image."""
        results = self.detect(image)
        counts = {}
        for item in results:
            class_name = item['class']
            counts[class_name] = counts.get(class_name, 0) + 1
        return counts

    def set_confidence(self, confidence):
        """Set minimum confidence threshold."""
        self.confidence = confidence
        logger.info(f"Detection confidence threshold set to: {confidence}")

    def set_classes(self, classes):
        """Set filter for specific classes."""
        self.classes = classes
        logger.info(f"Detection classes filter set to: {classes}")
