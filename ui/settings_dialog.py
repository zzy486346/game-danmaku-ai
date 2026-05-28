"""Settings dialog for Game Danmaku AI."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QLineEdit, QPushButton,
    QColorDialog, QGroupBox, QFormLayout, QSlider,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt
import sys
from PySide6.QtGui import QColor, QIcon
from pathlib import Path
from loguru import logger

from ai.cloud_vision import PROVIDER_CONFIGS

ACCENT = "#4A6CF7"
ACCENT_HOVER = "#5B7DF8"
ACCENT_PRESS = "#3A5CE0"
BG_DARK = "#14142B"
BG_CARD = "#1E1E3A"
BG_INPUT = "#252545"
BORDER = "#2A2A50"
TEXT_PRIMARY = "#F0F0F5"
TEXT_SECONDARY = "#8B8BAA"

GLOBAL_STYLESHEET = f"""
QDialog {{
    background-color: {BG_DARK};
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}}

QTabWidget::pane {{
    border: none;
    background: {BG_DARK};
    padding: 8px;
}}

QTabWidget::tab-bar {{
    alignment: left;
}}

QTabBar::tab {{
    background: transparent;
    color: {TEXT_SECONDARY};
    padding: 8px 20px;
    margin-right: 4px;
    border-bottom: 2px solid transparent;
    font-size: 13px;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}

QTabBar::tab:hover:!selected {{
    color: {TEXT_PRIMARY};
}}

QGroupBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    margin-top: 16px;
    padding: 20px 16px 16px 16px;
    font-size: 13px;
    font-weight: bold;
    color: {TEXT_PRIMARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: {ACCENT};
}}

QLabel {{
    color: {TEXT_SECONDARY};
    font-size: 12px;
}}

QLineEdit {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    selection-background-color: {ACCENT};
}}

QLineEdit:focus {{
    border-color: {ACCENT};
}}

QComboBox {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    min-width: 150px;
}}

QComboBox:hover {{
    border-color: {ACCENT};
}}

QComboBox QAbstractItemView {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
}}

QSpinBox, QDoubleSpinBox {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {ACCENT};
}}

QSlider::groove:horizontal {{
    border: none;
    height: 6px;
    background: {BG_INPUT};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {ACCENT};
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}

QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 3px;
}}

QCheckBox {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {BORDER};
    border-radius: 4px;
    background: {BG_INPUT};
}}

QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

QPushButton {{
    background: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton:hover {{
    border-color: {ACCENT};
    color: {ACCENT};
}}

QPushButton#saveButton {{
    background: {ACCENT};
    color: white;
    border: 1px solid {ACCENT};
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton#saveButton:hover {{
    background: {ACCENT_HOVER};
    border-color: {ACCENT_HOVER};
}}

QPushButton#saveButton:pressed {{
    background: {ACCENT_PRESS};
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
"""


class SettingsDialog(QDialog):
    """Settings dialog for configuring the application."""

    def __init__(self, config, ai_engine=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.ai_engine = ai_engine
        self.setWindowTitle("Game Danmaku AI - 设置")
        self.setMinimumSize(520, 480)
        self.resize(580, 620)
        self.setMaximumSize(16777215, 16777215)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        base_path = Path(getattr(sys, '_MEIPASS', Path(__file__).parent.parent))
        icon_path = base_path / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self.setStyleSheet(GLOBAL_STYLESHEET)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget()
        self._create_capture_tab()
        self._create_ai_tab()
        self._create_cloud_tab()
        self._create_danmaku_tab()
        self._create_performance_tab()
        layout.addWidget(self.tabs, stretch=1)

        footer = QFrame()
        footer.setStyleSheet(f"QFrame {{ background: {BG_CARD}; border-top: 1px solid {BORDER}; }}")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 10, 16, 10)

        self.reset_button = QPushButton("重置默认")
        self.reset_button.clicked.connect(self._reset_defaults)
        footer_layout.addWidget(self.reset_button)
        footer_layout.addStretch()
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        footer_layout.addWidget(self.cancel_button)
        self.save_button = QPushButton("保存")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self._save_settings)
        footer_layout.addWidget(self.save_button)
        layout.addWidget(footer)

    def _wrap_scroll(self, widget):
        """Wrap widget in scroll area for resizable support."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        return scroll

    def _create_capture_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 16, 20, 16)

        group = QGroupBox("屏幕捕获")
        form = QFormLayout(group)
        form.setSpacing(10)
        self.monitor_combo = QComboBox()
        self.monitor_combo.addItem("主显示器", 0)
        self.monitor_combo.addItem("显示器 1", 1)
        self.monitor_combo.addItem("显示器 2", 2)
        form.addRow("捕获显示器:", self.monitor_combo)
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(30)
        self.fps_spin.setSuffix(" FPS")
        form.addRow("捕获帧率:", self.fps_spin)
        layout.addWidget(group)
        layout.addStretch()
        self.tabs.addTab(self._wrap_scroll(tab), "屏幕捕获")

    def _create_ai_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 16, 20, 16)

        ocr_group = QGroupBox("OCR 文字识别")
        ocr_form = QFormLayout(ocr_group)
        ocr_form.setSpacing(10)
        self.ocr_enabled = QCheckBox("启用 OCR")
        ocr_form.addRow(self.ocr_enabled)
        self.ocr_confidence = QDoubleSpinBox()
        self.ocr_confidence.setRange(0.1, 1.0)
        self.ocr_confidence.setSingleStep(0.1)
        self.ocr_confidence.setValue(0.6)
        ocr_form.addRow("置信度阈值:", self.ocr_confidence)
        layout.addWidget(ocr_group)

        od_group = QGroupBox("目标检测")
        od_form = QFormLayout(od_group)
        od_form.setSpacing(10)
        self.od_enabled = QCheckBox("启用目标检测")
        od_form.addRow(self.od_enabled)
        self.od_confidence = QDoubleSpinBox()
        self.od_confidence.setRange(0.1, 1.0)
        self.od_confidence.setSingleStep(0.1)
        self.od_confidence.setValue(0.5)
        od_form.addRow("置信度阈值:", self.od_confidence)
        layout.addWidget(od_group)
        layout.addStretch()
        self.tabs.addTab(self._wrap_scroll(tab), "本地 AI")

    def _create_cloud_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 16, 20, 16)

        cloud_group = QGroupBox("云端大模型")
        cloud_form = QFormLayout(cloud_group)
        cloud_form.setSpacing(10)

        self.cloud_enabled = QCheckBox("启用云端识别")
        self.cloud_enabled.stateChanged.connect(self._on_cloud_enabled_changed)
        cloud_form.addRow(self.cloud_enabled)

        self.provider_combo = QComboBox()
        self.provider_combo.addItem("OpenAI", "openai")
        self.provider_combo.addItem("Claude (Anthropic)", "claude")
        self.provider_combo.addItem("DeepSeek", "deepseek")
        self.provider_combo.addItem("小米 MiMo", "xiaomi")
        self.provider_combo.addItem("阿里 Qwen", "qwen")
        self.provider_combo.addItem("OpenAI 兼容 API", "openai_compatible")
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        cloud_form.addRow("API 提供商:", self.provider_combo)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("输入 API Key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        cloud_form.addRow("API Key:", self.api_key_input)

        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("留空使用默认地址")
        cloud_form.addRow("API 地址:", self.base_url_input)

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        cloud_form.addRow("模型:", self.model_combo)

        self.cloud_interval_spin = QSpinBox()
        self.cloud_interval_spin.setRange(1, 30)
        self.cloud_interval_spin.setValue(5)
        self.cloud_interval_spin.setSuffix(" 秒")
        cloud_form.addRow("识别间隔:", self.cloud_interval_spin)

        self.cloud_concurrency_spin = QSpinBox()
        self.cloud_concurrency_spin.setRange(1, 8)
        self.cloud_concurrency_spin.setValue(4)
        cloud_form.addRow("云端并发数:", self.cloud_concurrency_spin)

        layout.addWidget(cloud_group)

        test_layout = QHBoxLayout()
        self.test_button = QPushButton("验证配置")
        self.test_button.clicked.connect(self._test_cloud_connection)
        test_layout.addWidget(self.test_button)
        self.test_status = QLabel("")
        test_layout.addWidget(self.test_status)
        test_layout.addStretch()
        layout.addLayout(test_layout)
        layout.addStretch()
        self.tabs.addTab(self._wrap_scroll(tab), "云端 AI")

    def _on_cloud_enabled_changed(self, state):
        enabled = state == Qt.CheckState.Checked.value
        for w in [self.provider_combo, self.api_key_input, self.base_url_input,
                   self.model_combo, self.cloud_interval_spin, self.cloud_concurrency_spin,
                   self.test_button]:
            w.setEnabled(enabled)

    def _on_provider_changed(self, index):
        provider_type = self.provider_combo.currentData()
        if not provider_type:
            return
        config = PROVIDER_CONFIGS.get(provider_type, {})
        base_url = config.get("base_url", "")
        models = config.get("models", [])

        if provider_type != "openai_compatible":
            self.base_url_input.setText(base_url)
            self.base_url_input.setPlaceholderText(base_url if base_url else "使用默认地址")
        else:
            self.base_url_input.setText("")
            self.base_url_input.setPlaceholderText("输入 API 地址，如 https://api.example.com/v1")

        self.model_combo.clear()
        for model in models:
            self.model_combo.addItem(model)
        if models:
            self.model_combo.setCurrentIndex(0)

    def _test_cloud_connection(self):
        from ai.cloud_vision import create_provider, PROVIDER_CONFIGS
        import requests

        provider_type = self.provider_combo.currentData()
        api_key = self.api_key_input.text().strip()
        base_url = self.base_url_input.text().strip() or None
        model = self.model_combo.currentText().strip() or None

        if not api_key:
            self.test_status.setText("请输入 API Key")
            self.test_status.setStyleSheet("color: #FF4444")
            return

        self.test_status.setText("验证中...")
        self.test_status.setStyleSheet(f"color: {TEXT_SECONDARY}")
        self.test_button.setEnabled(False)

        def _finish(msg, color):
            self.test_status.setText(msg)
            self.test_status.setStyleSheet(f"color: {color}")
            self.test_button.setEnabled(True)

        try:
            cfg = PROVIDER_CONFIGS.get(provider_type, {})
            actual_base = base_url or cfg.get("base_url", "")
            actual_model = model or (cfg.get("models", [""])[0] if cfg.get("models") else "")

            if provider_type == "claude":
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": actual_model,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "hi"}]
                }
                url = f"{actual_base}/messages"
            else:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": actual_model,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "hi"}]
                }
                url = f"{actual_base}/chat/completions"

            resp = requests.post(url, headers=headers, json=payload, timeout=15)

            if resp.status_code in (200, 201):
                _finish("连接成功", "#44FF44")
            elif resp.status_code == 401:
                _finish("API Key 无效", "#FF4444")
            elif resp.status_code == 403:
                _finish("无权限访问", "#FF4444")
            elif resp.status_code == 404:
                _finish("API 地址不存在", "#FF4444")
            elif resp.status_code == 429:
                _finish("请求过于频繁", "#FFAA44")
            else:
                _finish(f"错误 ({resp.status_code})", "#FF4444")
        except Exception as e:
            err = str(e)[:60]
            if "timeout" in err.lower():
                _finish("连接超时", "#FFAA44")
            else:
                _finish(f"失败: {err}", "#FF4444")

    def _create_danmaku_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 16, 20, 16)

        style_group = QGroupBox("弹幕样式")
        style_form = QFormLayout(style_group)
        style_form.setSpacing(10)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 48)
        self.font_size_spin.setValue(16)
        style_form.addRow("字体大小:", self.font_size_spin)

        color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.setFixedSize(32, 32)
        self.color_button.setStyleSheet(f"background: #FFFFFF; border: 2px solid {BORDER}; border-radius: 16px;")
        self.color_button.clicked.connect(lambda: self._pick_color(self.color_button))
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(QLabel("弹幕颜色"))
        color_layout.addStretch()
        style_form.addRow(color_layout)
        self.random_color_check = QCheckBox("使用随机颜色")
        style_form.addRow(self.random_color_check)
        layout.addWidget(style_group)

        anim_group = QGroupBox("动画效果")
        anim_form = QFormLayout(anim_group)
        anim_form.setSpacing(10)

        self.fps_combo = QComboBox()
        self.fps_combo.addItem("30 FPS", 30)
        self.fps_combo.addItem("60 FPS", 60)
        self.fps_combo.addItem("120 FPS", 120)
        self.fps_combo.addItem("144 FPS", 144)
        anim_form.addRow("弹幕帧率:", self.fps_combo)

        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(1, 20)
        self.speed_spin.setValue(5)
        anim_form.addRow("滚动速度:", self.speed_spin)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(80)
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("80%")
        opacity_layout.addWidget(self.opacity_label)
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))
        anim_form.addRow("透明度:", opacity_layout)

        self.max_count_spin = QSpinBox()
        self.max_count_spin.setRange(10, 200)
        self.max_count_spin.setValue(50)
        anim_form.addRow("最大弹幕数:", self.max_count_spin)
        layout.addWidget(anim_group)

        display_group = QGroupBox("显示位置")
        display_form = QFormLayout(display_group)
        display_form.setSpacing(10)
        self.position_combo = QComboBox()
        self.position_combo.addItem("顶部", "top")
        self.position_combo.addItem("居中", "center")
        self.position_combo.addItem("底部", "bottom")
        display_form.addRow("弹幕区域:", self.position_combo)
        layout.addWidget(display_group)
        layout.addStretch()
        self.tabs.addTab(self._wrap_scroll(tab), "弹幕设置")

    def _create_performance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 16, 20, 16)

        group = QGroupBox("性能")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.ai_interval_spin = QSpinBox()
        self.ai_interval_spin.setRange(1, 10)
        self.ai_interval_spin.setValue(3)
        self.ai_interval_spin.setSuffix(" 秒")
        form.addRow("AI 识别间隔:", self.ai_interval_spin)
        self.gpu_checkbox = QCheckBox("使用 GPU 加速")
        form.addRow(self.gpu_checkbox)
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 16)
        self.threads_spin.setValue(4)
        form.addRow("线程数:", self.threads_spin)
        layout.addWidget(group)
        layout.addStretch()
        self.tabs.addTab(self._wrap_scroll(tab), "性能")

    def _pick_color(self, button):
        current = button.text() or "#FFFFFF"
        color = QColorDialog.getColor(QColor(current), self)
        if color.isValid():
            button.setStyleSheet(f"background: {color.name()}; border: 2px solid {BORDER}; border-radius: 16px;")
            button.setText(color.name())

    def _load_settings(self):
        monitor = self.config.get('capture.monitor', 0)
        index = self.monitor_combo.findData(monitor)
        if index >= 0:
            self.monitor_combo.setCurrentIndex(index)
        self.fps_spin.setValue(self.config.get('capture.fps', 30))
        self.ocr_enabled.setChecked(self.config.get('ai.ocr.enabled', True))
        self.ocr_confidence.setValue(self.config.get('ai.ocr.confidence', 0.6))
        self.od_enabled.setChecked(self.config.get('ai.object_detection.enabled', True))
        self.od_confidence.setValue(self.config.get('ai.object_detection.confidence', 0.5))

        cloud_config = self.config.get('ai.cloud', {})
        self.cloud_enabled.setChecked(cloud_config.get('enabled', False))
        provider = cloud_config.get('provider', 'openai')
        index = self.provider_combo.findData(provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)
        self.api_key_input.setText(self.config.get('ai.cloud.api_key', ''))
        self.base_url_input.setText(cloud_config.get('base_url', ''))
        self.cloud_interval_spin.setValue(cloud_config.get('interval', 5))
        self.cloud_concurrency_spin.setValue(cloud_config.get('max_concurrent', 4))

        model = cloud_config.get('model', '')
        if model:
            index = self.model_combo.findText(model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
            else:
                self.model_combo.setEditText(model)

        self.font_size_spin.setValue(self.config.get('danmaku.style.size', 16))
        color = self.config.get('danmaku.style.color', '#FFFFFF')
        self.color_button.setStyleSheet(f"background: {color}; border: 2px solid {BORDER}; border-radius: 16px;")
        self.color_button.setText(color)
        self.random_color_check.setChecked(self.config.get('danmaku.style.random_color', True))
        fps = self.config.get('danmaku.animation.fps', 60)
        index = self.fps_combo.findData(fps)
        if index >= 0:
            self.fps_combo.setCurrentIndex(index)
        self.speed_spin.setValue(self.config.get('danmaku.animation.speed', 5))
        self.opacity_slider.setValue(int(self.config.get('danmaku.animation.opacity', 0.8) * 100))
        self.max_count_spin.setValue(self.config.get('danmaku.animation.max_count', 50))

        position = self.config.get('danmaku.display.position', 'top')
        index = self.position_combo.findData(position)
        if index >= 0:
            self.position_combo.setCurrentIndex(index)

        self.ai_interval_spin.setValue(self.config.get('performance.ai_interval', 3))
        self.gpu_checkbox.setChecked(self.config.get('performance.use_gpu', True))
        self.threads_spin.setValue(self.config.get('performance.num_threads', 4))
        self._on_cloud_enabled_changed(Qt.CheckState.Checked.value if self.cloud_enabled.isChecked() else 0)

    def _save_settings(self):
        self.config.set('capture.monitor', self.monitor_combo.currentData())
        self.config.set('capture.fps', self.fps_spin.value())
        self.config.set('ai.ocr.enabled', self.ocr_enabled.isChecked())
        self.config.set('ai.ocr.confidence', self.ocr_confidence.value())
        self.config.set('ai.object_detection.enabled', self.od_enabled.isChecked())
        self.config.set('ai.object_detection.confidence', self.od_confidence.value())

        self.config.set('ai.cloud.enabled', self.cloud_enabled.isChecked())
        self.config.set('ai.cloud.provider', self.provider_combo.currentData())
        self.config.set('ai.cloud.api_key', self.api_key_input.text().strip())
        self.config.set('ai.cloud.base_url', self.base_url_input.text().strip())
        self.config.set('ai.cloud.model', self.model_combo.currentText().strip())
        self.config.set('ai.cloud.interval', self.cloud_interval_spin.value())
        self.config.set('ai.cloud.max_concurrent', self.cloud_concurrency_spin.value())

        self.config.set('danmaku.style.size', self.font_size_spin.value())
        self.config.set('danmaku.style.color', self.color_button.text() or '#FFFFFF')
        self.config.set('danmaku.style.random_color', self.random_color_check.isChecked())
        self.config.set('danmaku.animation.fps', self.fps_combo.currentData())
        self.config.set('danmaku.animation.speed', self.speed_spin.value())
        self.config.set('danmaku.animation.opacity', self.opacity_slider.value() / 100)
        self.config.set('danmaku.animation.max_count', self.max_count_spin.value())
        self.config.set('danmaku.display.position', self.position_combo.currentData())

        self.config.set('performance.ai_interval', self.ai_interval_spin.value())
        self.config.set('performance.use_gpu', self.gpu_checkbox.isChecked())
        self.config.set('performance.num_threads', self.threads_spin.value())

        self.config.save()

        if self.ai_engine and self.cloud_enabled.isChecked():
            self.ai_engine.update_cloud_config(
                self.provider_combo.currentData(),
                self.api_key_input.text().strip(),
                self.base_url_input.text().strip() or None,
                self.model_combo.currentText().strip() or None
            )

        self.accept()

    def _reset_defaults(self):
        from copy import deepcopy
        from utils.config_manager import DEFAULT_CONFIG
        self.config.config = deepcopy(DEFAULT_CONFIG)
        self._load_settings()
