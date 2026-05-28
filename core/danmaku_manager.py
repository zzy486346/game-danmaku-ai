"""Danmaku manager - connects AI engine with danmaku rendering."""

import time
import random
from queue import Queue, Empty
from threading import Thread, Event, Lock
from difflib import SequenceMatcher
from loguru import logger

from danmaku.animation import AnimationEngine, DanmakuItem
from danmaku.renderer import DanmakuRenderer
from danmaku.styles import DanmakuStyle, PRESET_STYLES, get_random_style, get_style_for_event


class DanmakuManager:
    """Manages danmaku lifecycle, connecting AI results to rendering."""

    def __init__(self, config):
        self.config = config
        self.animation = AnimationEngine(
            max_count=config.get('danmaku.animation.max_count', 50)
        )
        self.renderer = DanmakuRenderer()
        self.text_queue = Queue(maxsize=200)
        self.running = Event()
        self.process_thread = None
        self.recent_texts = []
        self.max_recent = 100
        self.recent_ttl = 180
        self.recent_lock = Lock()
        self.apply_config()

    def start(self):
        """Start danmaku processing."""
        if self.running.is_set():
            return

        self.running.set()
        self.process_thread = Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()
        logger.info("Danmaku manager started")

    def stop(self):
        """Stop danmaku processing."""
        self.running.clear()
        if self.process_thread:
            self.process_thread.join(timeout=2)
        logger.info("Danmaku manager stopped")

    def add_text(self, text: str, style_name: str = "default") -> bool:
        """Add text to danmaku queue with deduplication."""
        if self._is_duplicate_text(text):
            return False

        self._remember_text(text)

        try:
            self.text_queue.put_nowait((text, style_name))
            return True
        except:
            return False

    def add_danmaku_from_ai(self, ai_results: dict):
        """Process AI results and generate danmaku."""
        from core.ai_engine import AIEngine
        texts = []

        for event in ai_results.get('events', []):
            style_name = get_style_for_event(event.value).color
            texts.append((f"🎮 {event.value}", "highlight"))

        for ocr_item in ai_results.get('ocr', []):
            text = ocr_item['text']
            if 2 < len(text) < 50:
                texts.append((text, "info"))

        for obj in ai_results.get('objects', []):
            if obj['confidence'] > 0.7:
                texts.append((f"👀 发现 {obj['class']}", "info"))

        for text, style in texts:
            self.add_text(text, style)

    def _process_loop(self):
        """Process queued text into danmaku items with staggered output."""
        last_add_time = 0
        add_interval = 0.8

        while self.running.is_set():
            current_time = time.time()

            if current_time - last_add_time >= add_interval:
                try:
                    if not self.text_queue.empty():
                        text, style_name = self.text_queue.get_nowait()
                        style_name = self._prepare_style(style_name)
                        speed_level = self.config.get('danmaku.animation.speed', 8)
                        speed = 150 + speed_level * 25
                        speed += random.uniform(-15, 15)
                        screen_width = 1920
                        try:
                            from PySide6.QtGui import QGuiApplication
                            screen = QGuiApplication.primaryScreen()
                            if screen:
                                screen_width = screen.availableGeometry().width()
                        except:
                            pass
                        self.animation.add_danmaku(text, style_name, speed, screen_width)
                        last_add_time = current_time
                except Empty:
                    pass

            time.sleep(0.02)

    def update(self, screen_width: int, screen_height: int, offset_y: int = 0):
        """Update animation state."""
        self.animation.update(screen_width, screen_height, offset_y)

    def render(self, painter, screen_width: int, screen_height: int):
        """Render all active danmaku."""
        danmaku_list = self.animation.get_active_danmaku()
        self.renderer.render(painter, danmaku_list, screen_width, screen_height)

    def clear(self):
        """Clear all danmaku."""
        self.animation.clear()
        while not self.text_queue.empty():
            try:
                self.text_queue.get_nowait()
            except:
                break

    def get_active_count(self) -> int:
        """Get number of active danmaku."""
        return len(self.animation.get_active_danmaku())

    def set_speed(self, speed: float):
        """Set base animation speed."""
        self.config.set('danmaku.animation.speed', speed)

    def set_max_count(self, count: int):
        """Set maximum danmaku count."""
        self.animation.set_max_count(count)

    def apply_config(self):
        """Apply live danmaku settings to animation and default style."""
        self.animation.set_max_count(self.config.get('danmaku.animation.max_count', 50))
        PRESET_STYLES["default"] = DanmakuStyle(
            color=self.config.get('danmaku.style.color', '#FFFFFF'),
            **self._style_kwargs()
        )
        self.renderer.clear_cache()

    def _style_kwargs(self):
        """Build style keyword arguments from config."""
        return {
            "font_family": self.config.get('danmaku.style.font', 'Microsoft YaHei'),
            "font_size": self.config.get('danmaku.style.size', 16),
            "outline_color": self.config.get('danmaku.style.outline_color', '#000000'),
            "outline_width": self.config.get('danmaku.style.outline_width', 2),
            "opacity": self.config.get('danmaku.animation.opacity', 0.8),
        }

    def _prepare_style(self, style_name: str) -> str:
        """Resolve runtime style for queued danmaku."""
        if style_name != "default" or not self.config.get('danmaku.style.random_color', False):
            return style_name

        style = get_random_style(**self._style_kwargs())
        style_name = f"random_{id(style)}"
        PRESET_STYLES[style_name] = style
        return style_name

    def _is_duplicate_text(self, text: str) -> bool:
        """Check exact and near-duplicate text in a recent time window."""
        normalized = self._normalize_text(text)
        if not normalized:
            return True

        now = time.time()
        with self.recent_lock:
            self._cleanup_recent(now)
            for item in self.recent_texts:
                if normalized == item["normalized"]:
                    return True
                if self._is_similar(normalized, item["normalized"]):
                    return True
        return False

    def _remember_text(self, text: str):
        """Remember accepted text for future deduplication."""
        now = time.time()
        with self.recent_lock:
            self._cleanup_recent(now)
            self.recent_texts.append({
                "text": text,
                "normalized": self._normalize_text(text),
                "timestamp": now,
            })
            if len(self.recent_texts) > self.max_recent:
                self.recent_texts = self.recent_texts[-self.max_recent:]

    def _cleanup_recent(self, now: float):
        """Remove old recent texts."""
        cutoff = now - self.recent_ttl
        self.recent_texts = [
            item for item in self.recent_texts
            if item["timestamp"] >= cutoff
        ]

    def _normalize_text(self, text: str) -> str:
        """Normalize text for duplicate detection."""
        return "".join(ch for ch in text.lower().strip() if ch.isalnum())

    def _is_similar(self, left: str, right: str) -> bool:
        """Detect near-duplicate short comments."""
        if not left or not right:
            return False

        if left in right or right in left:
            return min(len(left), len(right)) >= 6

        return SequenceMatcher(None, left, right).ratio() >= 0.86
