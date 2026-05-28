"""Danmaku renderer for drawing on transparent overlay."""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import (
    QPainter, QColor, QFont, QFontMetrics,
    QPen, QBrush, QPainterPath, QStaticText, QTransform
)
from loguru import logger

from danmaku.styles import DanmakuStyle, PRESET_STYLES
from danmaku.animation import DanmakuItem


class DanmakuRenderer:
    """Renders danmaku items on a QPainter surface."""

    def __init__(self):
        self.font_cache = {}
        self.metrics_cache = {}
        self.static_text_cache = {}

    def render(self, painter: QPainter, danmaku_list: list, screen_width: int, screen_height: int):
        """Render all danmaku items."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        for danmaku in danmaku_list:
            if danmaku.alive:
                self.render_single(painter, danmaku, screen_width, screen_height)

    def render_single(self, painter: QPainter, danmaku: DanmakuItem, screen_width: int, screen_height: int):
        """Render a single danmaku item."""
        style = PRESET_STYLES.get(danmaku.style_name, PRESET_STYLES["default"])
        font = self._get_font(style)
        metrics = self._get_metrics(font, danmaku.text)

        if danmaku.width == 0:
            danmaku.width = metrics.horizontalAdvance(danmaku.text)
            danmaku.height = metrics.height()

        x = int(danmaku.x)
        y = int(danmaku.y)

        painter.setFont(font)

        if style.outline_width > 0:
            self._draw_outline(painter, x, y, danmaku.text, font, style)

        color = QColor(style.color)
        color.setAlphaF(style.opacity * danmaku.opacity)
        painter.setPen(QPen(color))
        painter.drawStaticText(x, y, self._get_static_text(font, danmaku.text))

    def _draw_outline(self, painter: QPainter, x: int, y: int, text: str, font: QFont, style: DanmakuStyle):
        """Draw text outline for better visibility using shadow effect."""
        outline_color = QColor(style.outline_color)
        outline_color.setAlphaF(style.opacity * 0.6)
        static_text = self._get_static_text(font, text)

        painter.setPen(QPen(outline_color))
        offset = max(1, style.outline_width)
        for dx, dy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset)]:
            painter.drawStaticText(x + dx, y + dy, static_text)

    def _get_font(self, style: DanmakuStyle) -> QFont:
        """Get or create font from cache."""
        cache_key = (style.font_family, style.font_size, style.bold, style.italic)
        if cache_key not in self.font_cache:
            font = QFont(style.font_family, style.font_size)
            font.setBold(style.bold)
            font.setItalic(style.italic)
            self.font_cache[cache_key] = font
        return self.font_cache[cache_key]

    def _get_metrics(self, font: QFont, text: str) -> QFontMetrics:
        """Get or create font metrics from cache."""
        cache_key = (font.family(), font.pointSize(), font.bold(), font.italic(), text)
        if cache_key not in self.metrics_cache:
            self.metrics_cache[cache_key] = QFontMetrics(font)
            if len(self.metrics_cache) > 1000:
                self.metrics_cache.clear()
        return self.metrics_cache[cache_key]

    def _get_static_text(self, font: QFont, text: str) -> QStaticText:
        """Get or create cached static text layout."""
        cache_key = (font.family(), font.pointSize(), font.bold(), font.italic(), text)
        if cache_key not in self.static_text_cache:
            static_text = QStaticText(text)
            static_text.setPerformanceHint(QStaticText.PerformanceHint.AggressiveCaching)
            static_text.prepare(QTransform(), font)
            self.static_text_cache[cache_key] = static_text
            if len(self.static_text_cache) > 1000:
                self.static_text_cache.clear()
        return self.static_text_cache[cache_key]

    def calculate_text_width(self, text: str, style: DanmakuStyle) -> int:
        """Calculate the width of text with given style."""
        font = self._get_font(style)
        metrics = self._get_metrics(font, text)
        return metrics.horizontalAdvance(text)

    def clear_cache(self):
        """Clear font and metrics cache."""
        self.font_cache.clear()
        self.metrics_cache.clear()
        self.static_text_cache.clear()
