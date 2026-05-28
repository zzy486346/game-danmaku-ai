"""Danmaku animation system."""

import time
import random
from dataclasses import dataclass, field
from typing import List, Optional
from threading import RLock
from loguru import logger


@dataclass
class DanmakuItem:
    """A single danmaku item with animation state."""
    text: str
    style_name: str = "default"
    x: float = 0
    y: float = 0
    speed: float = 200.0
    opacity: float = 1.0
    created_at: float = field(default_factory=time.time)
    width: float = 0
    height: float = 0
    track: int = 0
    alive: bool = True

    def update(self, delta_time: float):
        """Update position based on delta time (pixels per second)."""
        self.x -= self.speed * delta_time

    def is_visible(self, screen_width: int) -> bool:
        """Check if danmaku is still visible on screen."""
        return self.x + self.width > 0

    def is_expired(self, max_lifetime: float = 15.0) -> bool:
        """Check if danmaku has expired."""
        return time.time() - self.created_at > max_lifetime


class TrackManager:
    """Manages danmaku tracks to prevent overlapping."""

    def __init__(self, track_count: int = 20, track_height: int = 30):
        self.track_count = track_count
        self.track_height = track_height
        self.tracks: List[List[DanmakuItem]] = [[] for _ in range(track_count)]

    def find_available_track(self, danmaku: DanmakuItem, screen_width: int) -> int:
        """Find an available track for a new danmaku."""
        for i in range(self.track_count):
            if self._is_track_available(i, danmaku, screen_width):
                return i
        return random.randint(0, self.track_count - 1)

    def _is_track_available(self, track_index: int, danmaku: DanmakuItem, screen_width: int) -> bool:
        """Check if a track has space for a new danmaku."""
        track = self.tracks[track_index]
        if not track:
            return True

        for existing in track:
            if not existing.alive:
                continue
            if existing.x > screen_width * 0.3:
                return False
        return True

    def add_to_track(self, track_index: int, danmaku: DanmakuItem):
        """Add danmaku to a track."""
        self.tracks[track_index].append(danmaku)

    def cleanup(self):
        """Remove dead danmaku from tracks."""
        for i in range(self.track_count):
            self.tracks[i] = [d for d in self.tracks[i] if d.alive]

    def get_track_y(self, track_index: int, offset_y: int = 0) -> int:
        """Get Y position for a track."""
        return offset_y + track_index * self.track_height


class AnimationEngine:
    """Controls danmaku animation timing and updates."""

    def __init__(self, max_count: int = 50):
        self.max_count = max_count
        self.danmaku_list: List[DanmakuItem] = []
        self.track_manager = TrackManager()
        self.last_update = time.time()
        self.lock = RLock()

    def add_danmaku(self, text: str, style_name: str = "default", speed: float = 5.0, screen_width: int = 1920) -> Optional[DanmakuItem]:
        """Add a new danmaku to the animation."""
        with self.lock:
            if len(self.danmaku_list) >= self.max_count:
                self._remove_oldest()

            danmaku = DanmakuItem(
                text=text,
                style_name=style_name,
                speed=speed,
                x=screen_width,
                y=10
            )

            track = self.track_manager.find_available_track(danmaku, screen_width)
            danmaku.track = track
            danmaku.y = self.track_manager.get_track_y(track, 10)
            self.track_manager.add_to_track(track, danmaku)

            self.danmaku_list.append(danmaku)
            return danmaku

    def update(self, screen_width: int, screen_height: int, offset_y: int = 0):
        """Update all danmaku positions."""
        with self.lock:
            current_time = time.time()
            delta_time = min(current_time - self.last_update, 0.05)
            self.last_update = current_time

            for danmaku in self.danmaku_list:
                if danmaku.alive:
                    danmaku.update(delta_time)

                    if not danmaku.is_visible(screen_width) or danmaku.is_expired():
                        danmaku.alive = False

            self.danmaku_list = [d for d in self.danmaku_list if d.alive]
            self.track_manager.cleanup()

    def _remove_oldest(self):
        """Remove the oldest danmaku."""
        if self.danmaku_list:
            self.danmaku_list[0].alive = False

    def clear(self):
        """Clear all danmaku."""
        with self.lock:
            self.danmaku_list.clear()
            self.track_manager = TrackManager()

    def get_active_danmaku(self) -> List[DanmakuItem]:
        """Get list of active danmaku."""
        with self.lock:
            return [d for d in self.danmaku_list if d.alive]

    def set_max_count(self, count: int):
        """Set maximum number of active danmaku."""
        with self.lock:
            self.max_count = count
            while len(self.danmaku_list) > self.max_count:
                self.danmaku_list[0].alive = False
                self.danmaku_list.pop(0)
