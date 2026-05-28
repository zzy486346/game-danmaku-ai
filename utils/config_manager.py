"""Configuration manager for Game Danmaku AI."""

import yaml
from pathlib import Path
from loguru import logger

DEFAULT_CONFIG = {
    "capture": {
        "monitor": 0,
        "fps": 30,
        "region": None
    },
    "ai": {
        "ocr": {
            "enabled": True,
            "language": "ch",
            "confidence": 0.6
        },
        "object_detection": {
            "enabled": True,
            "model": "yolov8n.pt",
            "confidence": 0.5,
            "classes": []
        },
        "event_classification": {
            "enabled": True,
            "model": "game_events.pt"
        }
    },
    "danmaku": {
        "style": {
            "font": "Microsoft YaHei",
            "size": 16,
            "color": "#FFFFFF",
            "outline_color": "#000000",
            "outline_width": 2
        },
        "animation": {
            "speed": 5,
            "opacity": 0.8,
            "max_count": 50
        },
        "display": {
            "position": "top",
            "height_ratio": 0.3
        }
    },
    "performance": {
        "ai_interval": 0.5,
        "use_gpu": True,
        "num_threads": 4
    },
    "hotkeys": {
        "toggle_pause": "F9",
        "toggle_visibility": "F10",
        "open_settings": "F11"
    }
}


class ConfigManager:
    """Manages application configuration."""

    def __init__(self, config_path="config.yaml"):
        self.config_path = Path(config_path)
        self.config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = yaml.safe_load(f)
                    if loaded:
                        self._merge(self.config, loaded)
                logger.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        else:
            self.save()
            logger.info("Created default configuration file")

    def save(self):
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key_path, default=None):
        """Get config value by dot-separated key path."""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path, value):
        """Set config value by dot-separated key path."""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value

    def _merge(self, base, override):
        """Deep merge override into base."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge(base[key], value)
            else:
                base[key] = value
