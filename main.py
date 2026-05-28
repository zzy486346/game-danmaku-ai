"""Game Danmaku AI - Main Entry Point."""

import sys
import signal
from pathlib import Path
from threading import Thread

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication
from loguru import logger

from utils.config_manager import ConfigManager
from utils.performance import PerformanceMonitor
from core.screen_capture import ScreenCapture
from core.ai_engine import AIEngine
from core.danmaku_manager import DanmakuManager
from core.game_detector import GameDetector
from ui.overlay_window import OverlayWindow
from ui.tray_icon import TrayIcon
from ui.settings_dialog import SettingsDialog


class GameDanmakuApp:
    """Main application class."""

    def __init__(self):
        self.config = ConfigManager("config.yaml")
        self.perf_monitor = PerformanceMonitor()

        self.screen_capture = None
        self.ai_engine = None
        self.danmaku_manager = None
        self.game_detector = None

        self.overlay = None
        self.tray_icon = None

        self._initialize_components()

    def _initialize_components(self):
        """Initialize all application components."""
        logger.info("Initializing Game Danmaku AI...")

        self.danmaku_manager = DanmakuManager(self.config)
        self.ai_engine = AIEngine(self.config)
        self.screen_capture = ScreenCapture(
            monitor=self.config.get('capture.monitor', 0),
            fps=self.config.get('capture.fps', 30)
        )
        self.game_detector = GameDetector()

        self.overlay = OverlayWindow(self.danmaku_manager, self.config)
        self.tray_icon = TrayIcon()

        self._connect_signals()
        logger.info("Components initialized")

    def _connect_signals(self):
        """Connect signals between components."""
        self.tray_icon.show_settings_signal.connect(self._show_settings)
        self.tray_icon.toggle_pause_signal.connect(self._toggle_pause)
        self.tray_icon.toggle_visibility_signal.connect(self._toggle_visibility)
        self.tray_icon.quit_signal.connect(self.quit)

        self.ai_timer = QTimer()
        self.ai_timer.timeout.connect(self._process_ai_frame)
        ai_interval = self.config.get('performance.ai_interval', 3)
        self.ai_timer.start(ai_interval * 1000)

        self.cloud_timer = QTimer()
        self.cloud_timer.timeout.connect(self._process_cloud_frame)
        cloud_interval = self.config.get('ai.cloud.interval', 5)
        self.cloud_timer.start(cloud_interval * 1000)

        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self._update_performance)
        self.perf_timer.start(1000)

    def start(self):
        """Start the application."""
        logger.info("Starting Game Danmaku AI...")

        self.screen_capture.start()
        self.danmaku_manager.start()
        self.game_detector.start()

        self.overlay.show()
        self.tray_icon.show()

        self.tray_icon.show_notification(
            "Game Danmaku AI",
            "应用已启动，按 F9 暂停，F10 隐藏，F11 设置"
        )

        logger.info("Application started")

    def stop(self):
        """Stop all components."""
        logger.info("Stopping Game Danmaku AI...")

        self.screen_capture.stop()
        self.ai_engine.stop()
        self.danmaku_manager.stop()
        self.game_detector.stop()

        self.overlay.close()
        self.tray_icon.hide()

        logger.info("Application stopped")

    def quit(self):
        """Quit the application."""
        self.stop()
        QApplication.quit()

    def _process_ai_frame(self):
        """Process a frame through local AI engine."""
        if not self.config.get('ai.ocr.enabled', True) and \
           not self.config.get('ai.object_detection.enabled', True):
            return

        frame = self.screen_capture.get_latest_frame()
        if frame is not None:
            results = self.ai_engine.process_frame(frame, use_cloud=False)
            danmaku_texts = self.ai_engine.generate_danmaku_text(results)
            for text in danmaku_texts:
                self.danmaku_manager.add_text(text)

    def _process_cloud_frame(self):
        """Process a frame through cloud AI in background thread."""
        if not self.config.get('ai.cloud.enabled', False):
            return

        frame = self.screen_capture.get_latest_frame()
        if frame is not None:
            Thread(target=self._cloud_analyze, args=(frame,), daemon=True).start()

    def _cloud_analyze(self, frame):
        """Analyze frame with cloud API in background."""
        try:
            from danmaku.styles import get_random_style, PRESET_STYLES, DanmakuStyle
            results = self.ai_engine.process_frame(frame, use_cloud=True)
            danmaku_texts = self.ai_engine.generate_danmaku_text(results)
            use_random = self.config.get('danmaku.style.random_color', True)

            for text in danmaku_texts:
                if use_random:
                    style = get_random_style()
                    style_name = f"random_{id(style)}"
                    PRESET_STYLES[style_name] = style
                else:
                    color = self.config.get('danmaku.style.color', '#FFFFFF')
                    style = DanmakuStyle(color=color)
                    style_name = "custom"
                    PRESET_STYLES[style_name] = style
                self.danmaku_manager.add_text(text, style_name)
        except Exception as e:
            logger.error(f"Cloud analysis error: {e}")

    def _update_performance(self):
        """Update performance metrics."""
        stats = self.perf_monitor.get_stats()
        active_count = self.danmaku_manager.get_active_count()
        self.tray_icon.update_status(stats['fps'], active_count)

    def _show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.config, self.ai_engine)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            logger.info("Settings saved")
            self._update_timers()

    def _update_timers(self):
        """Update timer intervals based on current config."""
        ai_interval = self.config.get('performance.ai_interval', 3)
        self.ai_timer.setInterval(ai_interval * 1000)

        cloud_interval = self.config.get('ai.cloud.interval', 5)
        self.cloud_timer.setInterval(cloud_interval * 1000)

        logger.info(f"Timers updated: local={ai_interval}s, cloud={cloud_interval}s")

    def _toggle_pause(self):
        """Toggle pause state."""
        self.overlay.toggle_pause()

    def _toggle_visibility(self):
        """Toggle visibility state."""
        self.overlay.toggle_visibility()


def main():
    """Main entry point."""
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    game_danmaku = GameDanmakuApp()

    signal.signal(signal.SIGINT, lambda *_: game_danmaku.quit())

    game_danmaku.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
