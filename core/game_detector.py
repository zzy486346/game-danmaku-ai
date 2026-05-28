"""Game detection module."""

import time
from threading import Thread, Event
from loguru import logger

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


GAME_KEYWORDS = [
    'game', 'play', 'steam', 'epic', 'origin', 'uplay',
    'minecraft', 'fortnite', 'league', 'dota', 'csgo', 'valorant',
    'overwatch', 'apex', 'pubg', 'roblox', 'wow', 'ffxiv'
]


class GameDetector:
    """Detects running games and manages capture targets."""

    def __init__(self):
        self.current_game = None
        self.detected_games = []
        self.running = Event()
        self.detection_thread = None

    def start(self):
        """Start game detection."""
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available, game detection disabled")
            return

        self.running.set()
        self.detection_thread = Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        logger.info("Game detector started")

    def stop(self):
        """Stop game detection."""
        self.running.clear()
        if self.detection_thread:
            self.detection_thread.join(timeout=2)
        logger.info("Game detector stopped")

    def _detection_loop(self):
        """Main detection loop."""
        while self.running.is_set():
            try:
                games = self._scan_for_games()
                if games != self.detected_games:
                    self.detected_games = games
                    if games:
                        self.current_game = games[0]
                        logger.info(f"Detected games: {games}")
            except Exception as e:
                logger.error(f"Game detection error: {e}")

            time.sleep(5)

    def _scan_for_games(self):
        """Scan running processes for games."""
        games = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                name = proc.info['name'].lower()
                for keyword in GAME_KEYWORDS:
                    if keyword in name:
                        games.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid']
                        })
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return games

    def get_current_game(self):
        """Get currently detected game."""
        return self.current_game

    def get_detected_games(self):
        """Get list of all detected games."""
        return self.detected_games

    def is_game_running(self):
        """Check if any game is running."""
        return len(self.detected_games) > 0
