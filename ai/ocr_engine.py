"""OCR text recognition engine."""

import numpy as np
from loguru import logger


class OCREngine:
    """OCR engine using PaddleOCR for text recognition."""

    def __init__(self, language='ch', confidence=0.6):
        self.language = language
        self.confidence = confidence
        self.ocr = None
        self._initialize()

    def _initialize(self):
        """Initialize OCR model."""
        try:
            import os
            os.environ['GLOG_minloglevel'] = '3'
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang=self.language
            )
            logger.info(f"PaddleOCR initialized with language: {self.language}")
        except ImportError:
            logger.warning("PaddleOCR not available, using fallback")
            self.ocr = None
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            self.ocr = None

    def recognize(self, image):
        """Recognize text in image.

        Args:
            image: numpy array (BGR or BGRA format)

        Returns:
            list of dicts with 'text', 'confidence', 'bbox' keys
        """
        if self.ocr is None:
            return []

        try:
            if image.shape[2] == 4:
                image = image[:, :, :3]
            results = self.ocr.ocr(image, cls=True)
            return self._parse_results(results)
        except Exception as e:
            logger.error(f"OCR recognition error: {e}")
            return []

    def _parse_results(self, results):
        """Parse OCR results into standardized format."""
        parsed = []
        if results is None:
            return parsed

        for line in results:
            if line is None:
                continue
            for item in line:
                bbox, (text, confidence) = item
                if confidence >= self.confidence:
                    parsed.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': bbox
                    })
        return parsed

    def recognize_region(self, image, region):
        """Recognize text in a specific region of the image.

        Args:
            image: full image
            region: [x, y, width, height]

        Returns:
            list of recognized text items
        """
        x, y, w, h = region
        cropped = image[y:y+h, x:x+w]
        results = self.recognize(cropped)

        for item in results:
            for point in item['bbox']:
                point[0] += x
                point[1] += y

        return results

    def get_full_text(self, image):
        """Get all text concatenated from image."""
        results = self.recognize(image)
        texts = [item['text'] for item in results]
        return ' '.join(texts)

    def set_confidence(self, confidence):
        """Set minimum confidence threshold."""
        self.confidence = confidence
        logger.info(f"OCR confidence threshold set to: {confidence}")
