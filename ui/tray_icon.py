"""System tray icon for Game Danmaku AI."""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt, Signal
from loguru import logger


class TrayIcon(QSystemTrayIcon):
    """System tray icon with context menu."""

    show_settings_signal = Signal()
    toggle_pause_signal = Signal()
    toggle_visibility_signal = Signal()
    clear_danmaku_signal = Signal()
    quit_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paused = False
        self.visible = True

        self._create_icon()
        self._setup_menu()
        self._connect_signals()

    def _create_icon(self):
        """Create tray icon."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(50, 150, 255))
        painter.setPen(QColor(255, 255, 255))
        painter.drawRoundedRect(4, 4, 56, 56, 10, 10)

        font = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "弹")

        painter.end()

        self.setIcon(QIcon(pixmap))
        self.setToolTip("Game Danmaku AI")

    def _setup_menu(self):
        """Setup context menu."""
        self.menu = QMenu()

        self.status_action = self.menu.addAction("状态: 运行中")
        self.status_action.setEnabled(False)
        self.menu.addSeparator()

        self.pause_action = self.menu.addAction("暂停 (F9)")
        self.pause_action.triggered.connect(self._toggle_pause)

        self.visibility_action = self.menu.addAction("隐藏弹幕 (F10)")
        self.visibility_action.triggered.connect(self._toggle_visibility)

        self.clear_action = self.menu.addAction("清空弹幕")
        self.clear_action.triggered.connect(self._clear_danmaku)

        self.menu.addSeparator()

        self.settings_action = self.menu.addAction("设置 (F11)")
        self.settings_action.triggered.connect(self.show_settings_signal.emit)

        self.menu.addSeparator()

        self.quit_action = self.menu.addAction("退出")
        self.quit_action.triggered.connect(self.quit_signal.emit)

        self.setContextMenu(self.menu)

    def _connect_signals(self):
        """Connect tray icon signals."""
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_settings_signal.emit()

    def _toggle_pause(self):
        """Toggle pause state."""
        self.paused = not self.paused
        if self.paused:
            self.pause_action.setText("继续 (F9)")
            self.status_action.setText("状态: 已暂停")
        else:
            self.pause_action.setText("暂停 (F9)")
            self.status_action.setText("状态: 运行中")
        self.toggle_pause_signal.emit()

    def _toggle_visibility(self):
        """Toggle visibility state."""
        self.visible = not self.visible
        if self.visible:
            self.visibility_action.setText("隐藏弹幕 (F10)")
        else:
            self.visibility_action.setText("显示弹幕 (F10)")
        self.toggle_visibility_signal.emit()

    def _clear_danmaku(self):
        """Clear all danmaku."""
        logger.info("Clearing all danmaku")
        self.clear_danmaku_signal.emit()

    def show_notification(self, title: str, message: str):
        """Show system notification."""
        self.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)

    def update_status(self, fps: float, danmaku_count: int):
        """Update status display."""
        status = f"状态: {fps:.1f} FPS | {danmaku_count} 弹幕"
        self.status_action.setText(status)
