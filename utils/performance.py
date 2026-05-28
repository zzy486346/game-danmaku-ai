"""Performance monitoring utilities."""

import time
import psutil
from collections import deque
from loguru import logger


class PerformanceMonitor:
    """Monitors application performance metrics."""

    def __init__(self, window_size=60):
        self.window_size = window_size
        self.frame_times = deque(maxlen=window_size)
        self.last_time = None
        self.fps = 0
        self.avg_frame_time = 0

    def start_frame(self):
        """Mark the start of a frame."""
        self.last_time = time.perf_counter()

    def end_frame(self):
        """Mark the end of a frame and update metrics."""
        if self.last_time:
            frame_time = time.perf_counter() - self.last_time
            self.frame_times.append(frame_time)
            self._update_metrics()

    def _update_metrics(self):
        """Calculate FPS and average frame time."""
        if self.frame_times:
            self.avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.fps = 1.0 / self.avg_frame_time if self.avg_frame_time > 0 else 0

    def get_fps(self):
        """Get current FPS."""
        return round(self.fps, 1)

    def get_frame_time(self):
        """Get average frame time in milliseconds."""
        return round(self.avg_frame_time * 1000, 2)

    def get_stats(self):
        """Get all performance stats."""
        return {
            "fps": self.get_fps(),
            "frame_time_ms": self.get_frame_time(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
        }

    def log_stats(self):
        """Log current performance stats."""
        stats = self.get_stats()
        logger.debug(
            f"Performance: {stats['fps']} FPS | "
            f"{stats['frame_time_ms']}ms frame | "
            f"CPU: {stats['cpu_percent']}% | "
            f"Memory: {stats['memory_mb']:.1f}MB"
        )
