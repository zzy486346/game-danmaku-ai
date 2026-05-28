"""Transparent overlay window for danmaku display."""

import time

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QScreen, QGuiApplication
from loguru import logger


class OverlayWindow(QWidget):
    """Transparent, always-on-top window for rendering danmaku."""

    def __init__(self, danmaku_manager, config):
        super().__init__()
        self.danmaku_manager = danmaku_manager
        self.config = config
        self.visible = True
        self.paused = False
        self._frame_count = 0
        self._fps_actual = 0.0
        self._fps_started_at = time.perf_counter()

        self._setup_window()
        self._setup_timer()

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        screen = QGuiApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            self.setGeometry(geometry)

    def _setup_timer(self):
        """Setup update timer."""
        self.update_timer = QTimer(self)
        self.update_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.update_timer.timeout.connect(self._update)
        self.apply_timer_config()

    def apply_timer_config(self):
        """Apply render FPS config to the update timer."""
        fps = max(1, self.config.get('danmaku.animation.fps', 60))
        interval = max(1, round(1000 / fps))
        self.update_timer.setInterval(interval)
        if not self.update_timer.isActive():
            self.update_timer.start()

    def _update(self):
        """Update animation and trigger repaint."""
        if self.paused:
            return

        width = self.width()
        height = self.height()

        position = self.config.get('danmaku.display.position', 'top')
        height_ratio = self.config.get('danmaku.display.height_ratio', 0.3)

        if position == 'top':
            offset_y = 10
        elif position == 'center':
            offset_y = int(height * 0.3)
        else:
            offset_y = int(height * 0.6)

        self.danmaku_manager.update(width, height, offset_y)
        self.update()

    def paintEvent(self, event):
        """Paint danmaku on the overlay."""
        if not self.visible:
            return

        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.danmaku_manager.render(painter, self.width(), self.height())
            self._record_frame()
        finally:
            painter.end()

    def toggle_visibility(self):
        """Toggle danmaku visibility."""
        self.visible = not self.visible
        if self.visible:
            self.show()
        else:
            self.hide()
        logger.info(f"Overlay visibility: {self.visible}")

    def toggle_pause(self):
        """Toggle pause state."""
        self.paused = not self.paused
        logger.info(f"Overlay paused: {self.paused}")

    def clear_danmaku(self):
        """Clear all danmaku."""
        self.danmaku_manager.clear()

    def set_geometry(self, x: int, y: int, width: int, height: int):
        """Set overlay geometry."""
        self.setGeometry(x, y, width, height)

    def fit_to_screen(self):
        """Fit overlay to primary screen."""
        screen = QGuiApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            self.setGeometry(geometry)

    def get_fps_actual(self) -> float:
        """Get measured overlay paint FPS."""
        return self._fps_actual

    def _record_frame(self):
        """Update lightweight render FPS measurement."""
        self._frame_count += 1
        now = time.perf_counter()
        elapsed = now - self._fps_started_at
        if elapsed >= 1.0:
            self._fps_actual = self._frame_count / elapsed
            self._frame_count = 0
            self._fps_started_at = now
