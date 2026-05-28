"""Danmaku style definitions."""

import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class DanmakuStyle:
    """Style configuration for a danmaku."""
    font_family: str = "Microsoft YaHei"
    font_size: int = 16
    color: str = "#FFFFFF"
    outline_color: str = "#000000"
    outline_width: int = 2
    opacity: float = 0.8
    bold: bool = False
    italic: bool = False


PRESET_STYLES = {
    "default": DanmakuStyle(),
    "highlight": DanmakuStyle(
        color="#FFD700",
        font_size=20,
        bold=True
    ),
    "warning": DanmakuStyle(
        color="#FF4444",
        font_size=18,
        bold=True
    ),
    "success": DanmakuStyle(
        color="#44FF44",
        font_size=18
    ),
    "info": DanmakuStyle(
        color="#4488FF",
        font_size=14
    ),
    "small": DanmakuStyle(
        font_size=12,
        opacity=0.6
    ),
    "large": DanmakuStyle(
        font_size=24,
        bold=True
    ),
}


EVENT_STYLE_MAP = {
    "kill": "highlight",
    "death": "warning",
    "victory": "success",
    "defeat": "warning",
    "skill": "info",
    "level_up": "success",
    "item_pickup": "info",
    "damage": "warning",
    "heal": "success",
}


def get_style_for_event(event_type: str) -> DanmakuStyle:
    """Get appropriate style for an event type."""
    style_name = EVENT_STYLE_MAP.get(event_type, "default")
    return PRESET_STYLES.get(style_name, PRESET_STYLES["default"])


def get_style(style_name: str) -> DanmakuStyle:
    """Get style by name."""
    return PRESET_STYLES.get(style_name, PRESET_STYLES["default"])


RANDOM_COLORS = [
    "#FFFFFF",  # 白色
    "#FF6B6B",  # 珊瑚红
    "#4ECDC4",  # 青色
    "#45B7D1",  # 天蓝色
    "#96CEB4",  # 薄荷绿
    "#FFEAA7",  # 淡黄色
    "#DDA0DD",  # 梅红色
    "#98D8C8",  # 翡翠绿
    "#F7DC6F",  # 金黄色
    "#BB8FCE",  # 淡紫色
]


def get_random_style(**overrides) -> DanmakuStyle:
    """Get a style with random color."""
    overrides["color"] = random.choice(RANDOM_COLORS)
    return DanmakuStyle(**overrides)
