"""Configuration manager for Game Danmaku AI."""

import os
import yaml
from copy import deepcopy
from pathlib import Path
from loguru import logger

ENV_API_KEY = "GAME_DANMAKU_AI_API_KEY"
LOCAL_ENV_PATH = Path(".env")

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
        },
        "cloud": {
            "enabled": False,
            "provider": "qwen",
            "api_key": "",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen-vl-plus",
            "interval": 5,
            "max_concurrent": 4
        }
    },
    "danmaku": {
        "style": {
            "font": "Microsoft YaHei",
            "size": 16,
            "color": "#FFFFFF",
            "outline_color": "#000000",
            "outline_width": 2,
            "random_color": True
        },
        "animation": {
            "fps": 60,
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
        "ai_interval": 3,
        "use_gpu": True,
        "num_threads": 4
    },
}


class ConfigManager:
    """Manages application configuration."""

    def __init__(self, config_path="config.yaml"):
        self.config_path = Path(config_path)
        self.config = deepcopy(DEFAULT_CONFIG)
        load_local_env()
        self.load()
        self._move_api_key_to_env()

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
            if self.get('ai.cloud.api_key', ''):
                self._set_config_value('ai.cloud.api_key', '')
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key_path, default=None):
        """Get config value by dot-separated key path."""
        if key_path == 'ai.cloud.api_key':
            api_key = os.environ.get(ENV_API_KEY)
            if api_key:
                return api_key

        return self._get_config_value(key_path, default)

    def set(self, key_path, value):
        """Set config value by dot-separated key path."""
        if key_path == 'ai.cloud.api_key':
            if value:
                set_local_env_value(ENV_API_KEY, value)
                os.environ[ENV_API_KEY] = value
            value = ''

        self._set_config_value(key_path, value)

    def _get_config_value(self, key_path, default=None):
        """Get raw config value by dot-separated key path."""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def _set_config_value(self, key_path, value):
        """Set raw config value by dot-separated key path."""
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

    def _move_api_key_to_env(self):
        """Move a legacy config API key into local env storage."""
        api_key = self._get_config_value('ai.cloud.api_key', '')
        if api_key:
            set_local_env_value(ENV_API_KEY, api_key)
            os.environ[ENV_API_KEY] = api_key
            self._set_config_value('ai.cloud.api_key', '')


def load_local_env(env_path=LOCAL_ENV_PATH):
    """Load simple KEY=VALUE pairs from local .env without extra dependencies."""
    if not env_path.exists():
        return

    try:
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue

                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception as e:
        logger.error(f"Failed to load local env file: {e}")


def set_local_env_value(key: str, value: str, env_path=LOCAL_ENV_PATH):
    """Persist one KEY=VALUE pair to local .env."""
    lines = []
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8-sig') as f:
            lines = f.read().splitlines()

    replaced = False
    next_lines = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            next_lines.append(f"{key}={value}")
            replaced = True
        else:
            next_lines.append(line)

    if not replaced:
        next_lines.append(f"{key}={value}")

    with open(env_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(next_lines).strip() + "\n")
