"""Event classification engine for game events."""

import numpy as np
from loguru import logger
from enum import Enum


class GameEvent(Enum):
    """Game event types."""
    KILL = "kill"
    DEATH = "death"
    SKILL = "skill"
    VICTORY = "victory"
    DEFEAT = "defeat"
    LEVEL_UP = "level_up"
    ITEM_PICKUP = "item_pickup"
    DAMAGE = "damage"
    HEAL = "heal"
    UNKNOWN = "unknown"


EVENT_MESSAGES = {
    GameEvent.KILL: ["击杀！", "消灭敌人！", "干得漂亮！"],
    GameEvent.DEATH: ["倒下了...", "被击败", "再接再厉"],
    GameEvent.SKILL: ["技能释放！", "大招来了！", "酷炫技能！"],
    GameEvent.VICTORY: ["胜利！", "大吉大利！", "恭喜获胜！"],
    GameEvent.DEFEAT: ["失败...", "下次再来", "不要气馁"],
    GameEvent.LEVEL_UP: ["升级啦！", "等级提升！", "变强了！"],
    GameEvent.ITEM_PICKUP: ["捡到道具！", "获得物品！", "好东西！"],
    GameEvent.DAMAGE: ["受到伤害！", "小心！", "快躲开！"],
    GameEvent.HEAL: ["恢复生命！", "治疗成功！", "回血了！"],
}


class EventClassifier:
    """Classifies game events from screen captures."""

    def __init__(self, model_path=None):
        self.model_path = model_path
        self.model = None
        self.event_history = []
        self.max_history = 100
        self._initialize()

    def _initialize(self):
        """Initialize classification model."""
        if self.model_path:
            try:
                import torch
                self.model = torch.load(self.model_path)
                self.model.eval()
                logger.info(f"Event classifier model loaded: {self.model_path}")
            except Exception as e:
                logger.warning(f"Failed to load event classifier: {e}")
                self.model = None
        else:
            logger.info("Event classifier using rule-based detection")

    def classify(self, image, ocr_results=None, detections=None):
        """Classify game events from image and context.

        Args:
            image: numpy array (BGR format)
            ocr_results: OCR recognition results
            detections: object detection results

        Returns:
            list of GameEvent
        """
        events = []

        if self.model:
            events.extend(self._model_classify(image))
        else:
            events.extend(self._rule_classify(ocr_results, detections))

        for event in events:
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)

        return events

    def _model_classify(self, image):
        """Classify using deep learning model."""
        try:
            import torch
            from torchvision import transforms

            transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

            input_tensor = transform(image).unsqueeze(0)
            with torch.no_grad():
                output = self.model(input_tensor)
                probabilities = torch.softmax(output, dim=1)
                predicted_class = torch.argmax(probabilities, dim=1).item()
                confidence = probabilities[0][predicted_class].item()

            if confidence > 0.7:
                event_type = list(GameEvent)[predicted_class]
                return [event_type]
        except Exception as e:
            logger.error(f"Model classification error: {e}")

        return []

    def _rule_classify(self, ocr_results, detections):
        """Classify using rule-based heuristics."""
        events = []

        if ocr_results:
            for item in ocr_results:
                text = item['text'].lower()

                if any(word in text for word in ['击杀', '消灭', 'kill', 'defeated']):
                    events.append(GameEvent.KILL)
                elif any(word in text for word in ['死亡', '倒下', 'death', 'defeat']):
                    events.append(GameEvent.DEATH)
                elif any(word in text for word in ['胜利', '获胜', 'victory', 'winner']):
                    events.append(GameEvent.VICTORY)
                elif any(word in text for word in ['失败', '落败', 'defeat', 'loser']):
                    events.append(GameEvent.DEFEAT)
                elif any(word in text for word in ['升级', 'level up', 'levelup']):
                    events.append(GameEvent.LEVEL_UP)
                elif any(word in text for word in ['获得', '捡到', 'pickup', 'obtained']):
                    events.append(GameEvent.ITEM_PICKUP)

        if detections:
            damage_indicators = ['explosion', 'fire', 'effect']
            for det in detections:
                if det['class'] in damage_indicators:
                    events.append(GameEvent.DAMAGE)

        return events

    def get_event_message(self, event):
        """Get a random message for an event type."""
        import random
        messages = EVENT_MESSAGES.get(event, ["发生了什么？"])
        return random.choice(messages)

    def get_recent_events(self, count=10):
        """Get recent events from history."""
        return self.event_history[-count:]

    def clear_history(self):
        """Clear event history."""
        self.event_history.clear()
