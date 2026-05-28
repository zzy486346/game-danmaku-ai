"""Cloud Vision API integration for Game Danmaku AI."""

import base64
import json
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from loguru import logger

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class CloudVisionProvider(ABC):
    """Base class for cloud vision API providers."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.last_call_time = 0
        self.min_interval = 0.5

    @abstractmethod
    def analyze_image(self, image_base64: str, prompt: str) -> Optional[str]:
        """Analyze image and return response."""
        pass

    def _encode_image(self, image) -> str:
        """Encode numpy image to base64."""
        import cv2
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return base64.b64encode(buffer).decode('utf-8')

    def _rate_limit(self):
        """Simple rate limiting."""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call_time = time.time()


class OpenAIProvider(CloudVisionProvider):
    """OpenAI GPT-4 Vision API provider."""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", model: str = "gpt-4o"):
        super().__init__(api_key, base_url, model)

    def analyze_image(self, image_base64: str, prompt: str) -> Optional[str]:
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return None

        self._rate_limit()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None


class ClaudeProvider(CloudVisionProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str, base_url: str = "https://api.anthropic.com/v1", model: str = "claude-sonnet-4-20250514"):
        super().__init__(api_key, base_url, model)

    def analyze_image(self, image_base64: str, prompt: str) -> Optional[str]:
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return None

        self._rate_limit()

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": self.model,
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        }

        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['content'][0]['text']
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return None


class OpenAICompatibleProvider(CloudVisionProvider):
    """Provider for OpenAI-compatible APIs (e.g., local LLMs, other providers)."""

    def __init__(self, api_key: str, base_url: str, model: str = "gpt-4o"):
        super().__init__(api_key, base_url, model)

    def analyze_image(self, image_base64: str, prompt: str) -> Optional[str]:
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return None

        self._rate_limit()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"API error: {e}")
            return None


class DeepSeekProvider(OpenAICompatibleProvider):
    """DeepSeek API provider."""

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1", model: str = "deepseek-vl2"):
        super().__init__(api_key, base_url, model)


class XiaomiProvider(OpenAICompatibleProvider):
    """Xiaomi MiMo API provider."""

    def __init__(self, api_key: str, base_url: str = "https://api.xiaomimimo.com/v1", model: str = "mimo-v2.5-pro"):
        super().__init__(api_key, base_url, model)


class QwenProvider(OpenAICompatibleProvider):
    """Alibaba Qwen API provider."""

    def __init__(self, api_key: str, base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1", model: str = "qwen3.6-plus"):
        super().__init__(api_key, base_url, model)


PROVIDERS = {
    "openai": OpenAIProvider,
    "claude": ClaudeProvider,
    "deepseek": DeepSeekProvider,
    "xiaomi": XiaomiProvider,
    "qwen": QwenProvider,
    "openai_compatible": OpenAICompatibleProvider,
}

PROVIDER_CONFIGS = {
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
    },
    "claude": {
        "name": "Claude (Anthropic)",
        "base_url": "https://api.anthropic.com/v1",
        "models": ["claude-sonnet-4-20250514", "claude-haiku-4-5-20251001"]
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "models": ["deepseek-vl2", "deepseek-chat"]
    },
    "xiaomi": {
        "name": "小米 MiMo",
        "base_url": "https://api.xiaomimimo.com/v1",
        "models": ["mimo-v2.5-pro", "mimo-v2.5", "mimo-v2-pro"]
    },
    "qwen": {
        "name": "阿里 Qwen",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": ["qwen3.6-plus", "qwen-vl-max", "qwen-vl-plus", "qwen-max", "qwen-plus"]
    },
    "openai_compatible": {
        "name": "OpenAI兼容API",
        "base_url": "",
        "models": []
    }
}


def create_provider(provider_type: str, api_key: str, base_url: str = None, model: str = None) -> Optional[CloudVisionProvider]:
    """Create a cloud vision provider instance."""
    if provider_type not in PROVIDERS:
        logger.error(f"Unknown provider type: {provider_type}")
        return None

    if not api_key:
        logger.error("API key is required")
        return None

    config = PROVIDER_CONFIGS.get(provider_type, {})
    base_url = base_url or config.get("base_url", "")
    model = model or (config.get("models", ["gpt-4o"])[0] if config.get("models") else "gpt-4o")

    provider_class = PROVIDERS[provider_type]
    return provider_class(api_key=api_key, base_url=base_url, model=model)
