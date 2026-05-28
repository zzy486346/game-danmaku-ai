"""Settings dialog for Game Danmaku AI."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QLineEdit, QPushButton,
    QColorDialog, QGroupBox, QFormLayout, QSlider,
    QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from loguru import logger

from ai.cloud_vision import PROVIDER_CONFIGS


class SettingsDialog(QDialog):
    """Settings dialog for configuring the application."""

    def __init__(self, config, ai_engine=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.ai_engine = ai_engine
        self.setWindowTitle("Game Danmaku AI - 设置")
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Setup the UI layout."""
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._create_capture_tab()
        self._create_ai_tab()
        self._create_cloud_tab()
        self._create_danmaku_tab()
        self._create_performance_tab()

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self._save_settings)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        self.reset_button = QPushButton("重置默认")
        self.reset_button.clicked.connect(self._reset_defaults)

        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def _create_capture_tab(self):
        """Create capture settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        self.monitor_combo = QComboBox()
        self.monitor_combo.addItem("主显示器", 0)
        self.monitor_combo.addItem("显示器 1", 1)
        self.monitor_combo.addItem("显示器 2", 2)
        layout.addRow("捕获显示器:", self.monitor_combo)

        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(30)
        layout.addRow("捕获帧率:", self.fps_spin)

        self.tabs.addTab(tab, "屏幕捕获")

    def _create_ai_tab(self):
        """Create AI settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        ocr_group = QGroupBox("OCR文字识别")
        ocr_layout = QFormLayout(ocr_group)

        self.ocr_enabled = QCheckBox("启用OCR")
        ocr_layout.addRow(self.ocr_enabled)

        self.ocr_confidence = QDoubleSpinBox()
        self.ocr_confidence.setRange(0.1, 1.0)
        self.ocr_confidence.setSingleStep(0.1)
        self.ocr_confidence.setValue(0.6)
        ocr_layout.addRow("置信度阈值:", self.ocr_confidence)

        layout.addWidget(ocr_group)

        od_group = QGroupBox("目标检测")
        od_layout = QFormLayout(od_group)

        self.od_enabled = QCheckBox("启用目标检测")
        od_layout.addRow(self.od_enabled)

        self.od_confidence = QDoubleSpinBox()
        self.od_confidence.setRange(0.1, 1.0)
        self.od_confidence.setSingleStep(0.1)
        self.od_confidence.setValue(0.5)
        od_layout.addRow("置信度阈值:", self.od_confidence)

        layout.addWidget(od_group)

        layout.addStretch()
        self.tabs.addTab(tab, "本地AI")

    def _create_cloud_tab(self):
        """Create cloud API settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        cloud_group = QGroupBox("云端大模型设置")
        cloud_layout = QFormLayout(cloud_group)

        self.cloud_enabled = QCheckBox("启用云端识别")
        self.cloud_enabled.stateChanged.connect(self._on_cloud_enabled_changed)
        cloud_layout.addRow(self.cloud_enabled)

        self.provider_combo = QComboBox()
        self.provider_combo.addItem("OpenAI", "openai")
        self.provider_combo.addItem("Claude (Anthropic)", "claude")
        self.provider_combo.addItem("DeepSeek", "deepseek")
        self.provider_combo.addItem("小米 MiMo", "xiaomi")
        self.provider_combo.addItem("阿里 Qwen", "qwen")
        self.provider_combo.addItem("OpenAI兼容API", "openai_compatible")
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        cloud_layout.addRow("API提供商:", self.provider_combo)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("输入API Key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        cloud_layout.addRow("API Key:", self.api_key_input)

        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("留空使用默认地址")
        cloud_layout.addRow("API地址:", self.base_url_input)

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        cloud_layout.addRow("模型:", self.model_combo)

        self.cloud_interval_spin = QSpinBox()
        self.cloud_interval_spin.setRange(1, 30)
        self.cloud_interval_spin.setValue(5)
        self.cloud_interval_spin.setSuffix(" 秒")
        cloud_layout.addRow("识别间隔:", self.cloud_interval_spin)

        layout.addWidget(cloud_group)

        test_layout = QHBoxLayout()
        self.test_button = QPushButton("测试连接")
        self.test_button.clicked.connect(self._test_cloud_connection)
        test_layout.addWidget(self.test_button)
        self.test_status = QLabel("")
        test_layout.addWidget(self.test_status)
        test_layout.addStretch()
        layout.addLayout(test_layout)

        help_group = QGroupBox("说明")
        help_layout = QVBoxLayout(help_group)
        help_text = QLabel(
            "• 云端识别每3-5秒分析一次游戏画面\n"
            "• 支持OpenAI、Claude等主流大模型\n"
            "• OpenAI兼容API可接入其他第三方服务\n"
            "• 需要网络连接，会产生API调用费用"
        )
        help_text.setWordWrap(True)
        help_layout.addWidget(help_text)
        layout.addWidget(help_group)

        layout.addStretch()
        self.tabs.addTab(tab, "云端AI")

    def _on_cloud_enabled_changed(self, state):
        """Handle cloud enabled checkbox change."""
        enabled = state == Qt.CheckState.Checked.value
        self.provider_combo.setEnabled(enabled)
        self.api_key_input.setEnabled(enabled)
        self.base_url_input.setEnabled(enabled)
        self.model_combo.setEnabled(enabled)
        self.cloud_interval_spin.setEnabled(enabled)
        self.test_button.setEnabled(enabled)

    def _on_provider_changed(self, index):
        """Handle provider selection change."""
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
            self.base_url_input.setPlaceholderText("输入API地址，如 https://api.example.com/v1")

        self.model_combo.clear()
        for model in models:
            self.model_combo.addItem(model)

        if models:
            self.model_combo.setCurrentIndex(0)

    def _test_cloud_connection(self):
        """Test cloud API connection."""
        from ai.cloud_vision import create_provider

        provider_type = self.provider_combo.currentData()
        api_key = self.api_key_input.text().strip()
        base_url = self.base_url_input.text().strip() or None
        model = self.model_combo.currentText().strip() or None

        if not api_key:
            self.test_status.setText("请输入API Key")
            self.test_status.setStyleSheet("color: red")
            return

        self.test_status.setText("测试中...")
        self.test_status.setStyleSheet("color: gray")
        self.test_button.setEnabled(False)

        try:
            provider = create_provider(provider_type, api_key, base_url, model)
            if provider:
                self.test_status.setText("连接成功！")
                self.test_status.setStyleSheet("color: green")
            else:
                self.test_status.setText("创建提供商失败")
                self.test_status.setStyleSheet("color: red")
        except Exception as e:
            self.test_status.setText(f"连接失败: {str(e)[:50]}")
            self.test_status.setStyleSheet("color: red")
        finally:
            self.test_button.setEnabled(True)

    def _create_danmaku_tab(self):
        """Create danmaku settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        style_group = QGroupBox("弹幕样式")
        style_layout = QFormLayout(style_group)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 48)
        self.font_size_spin.setValue(16)
        style_layout.addRow("字体大小:", self.font_size_spin)

        color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.setFixedSize(30, 30)
        self.color_button.setStyleSheet("background-color: #FFFFFF")
        self.color_button.clicked.connect(lambda: self._pick_color(self.color_button))
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(QLabel("弹幕颜色"))
        color_layout.addStretch()
        style_layout.addRow(color_layout)

        self.random_color_check = QCheckBox("使用随机颜色")
        style_layout.addRow(self.random_color_check)

        layout.addWidget(style_group)

        anim_group = QGroupBox("动画效果")
        anim_layout = QFormLayout(anim_group)

        self.fps_combo = QComboBox()
        self.fps_combo.addItem("30 FPS", 30)
        self.fps_combo.addItem("60 FPS", 60)
        self.fps_combo.addItem("120 FPS", 120)
        self.fps_combo.addItem("144 FPS", 144)
        anim_layout.addRow("弹幕帧率:", self.fps_combo)

        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(1, 20)
        self.speed_spin.setValue(5)
        anim_layout.addRow("滚动速度:", self.speed_spin)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(80)
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("80%")
        opacity_layout.addWidget(self.opacity_label)
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        anim_layout.addRow("透明度:", opacity_layout)

        self.max_count_spin = QSpinBox()
        self.max_count_spin.setRange(10, 200)
        self.max_count_spin.setValue(50)
        anim_layout.addRow("最大弹幕数:", self.max_count_spin)

        layout.addWidget(anim_group)

        display_group = QGroupBox("显示位置")
        display_layout = QFormLayout(display_group)

        self.position_combo = QComboBox()
        self.position_combo.addItem("顶部", "top")
        self.position_combo.addItem("居中", "center")
        self.position_combo.addItem("底部", "bottom")
        display_layout.addRow("弹幕区域:", self.position_combo)

        layout.addWidget(display_group)

        self.tabs.addTab(tab, "弹幕设置")

    def _create_performance_tab(self):
        """Create performance settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)

        self.ai_interval_spin = QSpinBox()
        self.ai_interval_spin.setRange(1, 10)
        self.ai_interval_spin.setValue(3)
        self.ai_interval_spin.setSuffix(" 秒")
        layout.addRow("本地AI识别间隔:", self.ai_interval_spin)

        self.gpu_checkbox = QCheckBox("使用GPU加速")
        layout.addRow(self.gpu_checkbox)

        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 16)
        self.threads_spin.setValue(4)
        layout.addRow("线程数:", self.threads_spin)

        self.tabs.addTab(tab, "性能")

    def _pick_color(self, button):
        """Open color picker dialog."""
        color = QColorDialog.getColor(QColor("#FFFFFF"), self)
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}")
            button.setText(color.name())

    def _load_settings(self):
        """Load settings from config."""
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
        self.api_key_input.setText(cloud_config.get('api_key', ''))
        self.base_url_input.setText(cloud_config.get('base_url', ''))
        self.cloud_interval_spin.setValue(cloud_config.get('interval', 5))

        model = cloud_config.get('model', '')
        if model:
            index = self.model_combo.findText(model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
            else:
                self.model_combo.setEditText(model)

        self.font_size_spin.setValue(self.config.get('danmaku.style.size', 16))
        color = self.config.get('danmaku.style.color', '#FFFFFF')
        self.color_button.setStyleSheet(f"background-color: {color}")
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
        """Save settings to config."""
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

        self.config.set('danmaku.style.size', self.font_size_spin.value())
        self.config.set('danmaku.style.color', self.color_button.text() if hasattr(self.color_button, 'text') else '#FFFFFF')
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
        """Reset all settings to defaults."""
        from copy import deepcopy
        from utils.config_manager import DEFAULT_CONFIG
        self.config.config = deepcopy(DEFAULT_CONFIG)
        self._load_settings()
