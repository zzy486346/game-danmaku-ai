"""Screen capture module for Game Danmaku AI."""

import time
import numpy as np
import mss
from queue import Queue, Empty
from threading import Thread, Event
from loguru import logger


class ScreenCapture:
    """High-performance screen capture using mss library."""

    def __init__(self, monitor=0, fps=30, region=None):
        self.monitor_index = monitor
        self.fps = fps
        self.region = region
        self.frame_queue = Queue(maxsize=10)
        self.running = Event()
        self.capture_thread = None
        self.sct = None
        self.frame_count = 0
        self.start_time = 0

    def start(self):
        """Start screen capture in background thread."""
        if self.running.is_set():
            logger.warning("Screen capture already running")
            return

        self.sct = mss.mss()
        self.running.set()
        self.capture_thread = Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        logger.info(f"Screen capture started: monitor={self.monitor_index}, fps={self.fps}")

    def stop(self):
        """Stop screen capture."""
        self.running.clear()
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        if self.sct:
            self.sct.close()
        logger.info("Screen capture stopped")

    def _capture_loop(self):
        """Main capture loop running in background thread."""
        self.start_time = time.perf_counter()

        while self.running.is_set():
            frame_interval = 1.0 / max(1, self.fps)
            frame_start = time.perf_counter()

            try:
                frame = self._capture_frame()
                if frame is not None:
                    if self.frame_queue.full():
                        try:
                            self.frame_queue.get_nowait()
                        except Empty:
                            pass
                    self.frame_queue.put(frame)
                    self.frame_count += 1
            except Exception as e:
                logger.error(f"Capture error: {e}")

            elapsed = time.perf_counter() - frame_start
            sleep_time = frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _capture_frame(self):
        """Capture a single frame."""
        if self.region:
            monitor = {
                "left": self.region[0],
                "top": self.region[1],
                "width": self.region[2],
                "height": self.region[3]
            }
        else:
            monitor = self.sct.monitors[self.monitor_index]

        screenshot = self.sct.grab(monitor)
        frame = np.array(screenshot)
        return frame

    def get_frame(self, timeout=1.0):
        """Get the latest captured frame."""
        try:
            return self.frame_queue.get(timeout=timeout)
        except Empty:
            return None

    def get_latest_frame(self):
        """Get the most recent frame without waiting."""
        frame = None
        while not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get_nowait()
            except Empty:
                break
        return frame

    def get_fps_actual(self):
        """Get actual capture FPS."""
        elapsed = time.perf_counter() - self.start_time
        if elapsed > 0:
            return self.frame_count / elapsed
        return 0

    def get_monitors(self):
        """Get list of available monitors."""
        if not self.sct:
            self.sct = mss.mss()
        return self.sct.monitors

    def set_region(self, region):
        """Set capture region [x, y, width, height]."""
        self.region = region
        logger.info(f"Capture region set to: {region}")

    def set_fps(self, fps):
        """Set capture FPS."""
        self.fps = fps
        logger.info(f"Capture FPS set to: {fps}")
