"""AI Engine - Unified manager for all AI recognition tasks."""

import time
import numpy as np
from queue import Queue
from threading import Thread, Event, Lock
from loguru import logger

from ai.ocr_engine import OCREngine
from ai.object_detector import ObjectDetector
from ai.event_classifier import EventClassifier, GameEvent
from ai.cloud_vision import create_provider, PROVIDER_CONFIGS


ANALYSIS_PROMPT = """你是B站游戏直播间的老观众，正在看直播发弹幕。根据画面内容，发1-2条弹幕。

风格参考：
- "666" "卧槽" "草" "笑死" "绝了" "上啊！"
- "？？？" "这波啊" "节目效果拉满" "太秀了"
- "寄" "gg" "操作拉胯" "可以可以" "nb"
- 简短、口语化、有梗，像真人在直播间随手打的

不要：
- 不要写完整句子，不要书面语
- 不要说"画面中"、"截图显示"等描述性语言
- 不要提代码、终端、配置等技术内容
- 不要每次都用"666"，要有变化

只返回JSON：
{"comments": ["弹幕1", "弹幕2"]}"""


class AIEngine:
    """Manages multiple AI recognition engines."""

    def __init__(self, config):
        self.config = config
        self.running = Event()
        self.result_queue = Queue(maxsize=100)
        self.process_thread = None
        self.lock = Lock()

        self.ocr_engine = None
        self.object_detector = None
        self.event_classifier = None
        self.cloud_provider = None

        self._initialize_engines()

    def _initialize_engines(self):
        """Initialize all AI engines based on config."""
        ocr_config = self.config.get('ai.ocr', {})
        if ocr_config.get('enabled', True):
            self.ocr_engine = OCREngine(
                language=ocr_config.get('language', 'ch'),
                confidence=ocr_config.get('confidence', 0.6)
            )

        od_config = self.config.get('ai.object_detection', {})
        if od_config.get('enabled', True):
            self.object_detector = ObjectDetector(
                model_path=od_config.get('model', 'yolov8n.pt'),
                confidence=od_config.get('confidence', 0.5),
                classes=od_config.get('classes', None)
            )

        ec_config = self.config.get('ai.event_classification', {})
        if ec_config.get('enabled', True):
            self.event_classifier = EventClassifier(
                model_path=ec_config.get('model', None)
            )

        self._init_cloud_provider()

        logger.info("AI engines initialized")

    def _init_cloud_provider(self):
        """Initialize cloud vision provider."""
        cloud_config = self.config.get('ai.cloud', {})
        if not cloud_config.get('enabled', False):
            self.cloud_provider = None
            return

        provider_type = cloud_config.get('provider', 'openai')
        api_key = self.config.get('ai.cloud.api_key', '')
        base_url = cloud_config.get('base_url', None)
        model = cloud_config.get('model', None)

        if api_key:
            self.cloud_provider = create_provider(provider_type, api_key, base_url, model)
            if self.cloud_provider:
                logger.info(f"Cloud vision provider initialized: {provider_type}")
        else:
            logger.warning("Cloud vision enabled but no API key configured")

    def update_cloud_config(self, provider_type: str, api_key: str, base_url: str = None, model: str = None):
        """Update cloud provider configuration."""
        self.config.set('ai.cloud.provider', provider_type)
        self.config.set('ai.cloud.api_key', api_key)
        if base_url:
            self.config.set('ai.cloud.base_url', base_url)
        if model:
            self.config.set('ai.cloud.model', model)

        self.cloud_provider = create_provider(provider_type, api_key, base_url, model)
        logger.info(f"Cloud provider updated: {provider_type}")

    def process_frame(self, frame, use_cloud: bool = False):
        """Process a single frame through all AI engines.

        Args:
            frame: numpy array (BGR or BGRA format)
            use_cloud: whether to use cloud vision API

        Returns:
            dict with recognition results
        """
        if frame.shape[2] == 4:
            frame = frame[:, :, :3]

        results = {
            'timestamp': time.time(),
            'ocr': [],
            'objects': [],
            'events': [],
            'cloud_analysis': None
        }

        if use_cloud and self.cloud_provider:
            cloud_result = self._analyze_with_cloud(frame)
            if cloud_result:
                results['cloud_analysis'] = cloud_result
                results['events'].extend(cloud_result.get('events', []))
                results['ocr'].extend([{'text': t, 'confidence': 1.0} for t in cloud_result.get('texts', [])])
                results['objects'].extend([{'class': o, 'confidence': 1.0} for o in cloud_result.get('objects', [])])
        else:
            with self.lock:
                if self.ocr_engine:
                    results['ocr'] = self.ocr_engine.recognize(frame)

                if self.object_detector:
                    results['objects'] = self.object_detector.detect(frame)

                if self.event_classifier:
                    events = self.event_classifier.classify(
                        frame,
                        ocr_results=results['ocr'],
                        detections=results['objects']
                    )
                    results['events'] = events

        return results

    def _analyze_with_cloud(self, frame):
        """Analyze frame using cloud vision API."""
        try:
            import json
            image_base64 = self.cloud_provider._encode_image(frame)
            response = self.cloud_provider.analyze_image(image_base64, ANALYSIS_PROMPT)

            if response:
                try:
                    json_str = response
                    if '```json' in json_str:
                        json_str = json_str.split('```json')[1].split('```')[0]
                    elif '```' in json_str:
                        json_str = json_str.split('```')[1].split('```')[0]

                    result = json.loads(json_str.strip())
                    logger.debug(f"Cloud analysis result: {result}")
                    return result
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse cloud response as JSON: {response}")
                    return {"comment": response[:100]}
        except Exception as e:
            logger.error(f"Cloud analysis error: {e}")
        return None

    def start_async(self, frame_source):
        """Start async processing of frames.

        Args:
            frame_source: callable that returns frames
        """
        if self.running.is_set():
            logger.warning("AI engine already running")
            return

        self.running.set()
        self.process_thread = Thread(
            target=self._process_loop,
            args=(frame_source,),
            daemon=True
        )
        self.process_thread.start()
        logger.info("AI engine started in async mode")

    def stop(self):
        """Stop async processing."""
        self.running.clear()
        if self.process_thread:
            self.process_thread.join(timeout=5)
        logger.info("AI engine stopped")

    def _process_loop(self, frame_source):
        """Main processing loop."""
        interval = self.config.get('performance.ai_interval', 0.5)

        while self.running.is_set():
            try:
                frame = frame_source()
                if frame is not None:
                    results = self.process_frame(frame)
                    if self._has_significant_results(results):
                        self.result_queue.put(results)
            except Exception as e:
                logger.error(f"AI processing error: {e}")

            time.sleep(interval)

    def _has_significant_results(self, results):
        """Check if results contain anything worth showing."""
        if results['events']:
            return True
        if results['ocr']:
            return True
        if results['objects']:
            for obj in results['objects']:
                if obj['confidence'] > 0.7:
                    return True
        return False

    def get_results(self, timeout=1.0):
        """Get processed results."""
        try:
            return self.result_queue.get(timeout=timeout)
        except:
            return None

    def get_latest_results(self):
        """Get most recent results without waiting."""
        results = None
        while not self.result_queue.empty():
            try:
                results = self.result_queue.get_nowait()
            except:
                break
        return results

    def generate_danmaku_text(self, results):
        """Generate danmaku text from AI results.

        Args:
            results: AI recognition results

        Returns:
            list of danmaku text strings
        """
        danmaku_texts = []

        cloud_analysis = results.get('cloud_analysis')
        if cloud_analysis:
            if 'comments' in cloud_analysis:
                danmaku_texts.extend(cloud_analysis['comments'])
            elif 'comment' in cloud_analysis:
                danmaku_texts.append(cloud_analysis['comment'])

        for event in results.get('events', []):
            if isinstance(event, GameEvent):
                if self.event_classifier:
                    message = self.event_classifier.get_event_message(event)
                    danmaku_texts.append(message)
            elif isinstance(event, str):
                danmaku_texts.append(f"🎮 {event}")

        for ocr_item in results.get('ocr', []):
            text = ocr_item['text']
            if len(text) > 2 and len(text) < 50:
                danmaku_texts.append(text)

        for obj in results.get('objects', []):
            if obj.get('confidence', 0) > 0.8:
                class_name = obj['class']
                danmaku_texts.append(f"👀 发现 {class_name}")

        return danmaku_texts

    def get_provider_info(self):
        """Get current cloud provider info."""
        if not self.cloud_provider:
            return None
        return {
            'type': type(self.cloud_provider).__name__,
            'model': self.cloud_provider.model
        }
