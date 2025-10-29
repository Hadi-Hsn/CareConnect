"""Intent classifier for routing user queries."""
import re
from enum import Enum

from app.core.logging import get_logger

logger = get_logger(__name__)


class Intent(str, Enum):
    """User intent types."""

    BOOKING = "booking"
    MODIFICATION = "modification"
    CANCELLATION = "cancellation"
    INFORMATION = "information"
    EMERGENCY = "emergency"
    UNKNOWN = "unknown"


class IntentClassifier:
    """Simple rule-based intent classifier."""

    def __init__(self) -> None:
        """Initialize intent classifier."""
        self.patterns = {
            Intent.BOOKING: [
                r"\b(book|schedule|make|need|want)\b.*\b(appointment|visit|checkup)\b",
                r"\bsee\b.*\b(doctor|provider|specialist)\b",
                r"\b(available|availability)\b.*\b(slot|time)\b",
            ],
            Intent.MODIFICATION: [
                r"\b(change|modify|reschedule|move)\b.*\b(appointment|visit)\b",
                r"\b(different|another)\b.*\b(time|date|slot)\b",
            ],
            Intent.CANCELLATION: [
                r"\b(cancel|delete|remove)\b.*\b(appointment|visit)\b",
                r"\bcan't make\b.*\b(appointment|visit)\b",
            ],
            Intent.INFORMATION: [
                r"\b(where|what|when|how|why)\b",
                r"\b(directions|parking|location|hours)\b",
                r"\b(prepare|preparation|instructions)\b",
                r"\b(department|facility|building)\b",
                r"\blab\b.*\b(test|work|results)\b",
            ],
            Intent.EMERGENCY: [
                r"\bemergency\b",
                r"\b(urgent|critical|immediate)\b",
                r"\b(chest pain|can't breathe|bleeding)\b",
            ],
        }

    def classify(self, query: str) -> Intent:
        """
        Classify user intent based on query text.

        Args:
            query: User query string

        Returns:
            Detected intent
        """
        query_lower = query.lower()

        # Check for emergency first (highest priority)
        if self._matches_patterns(query_lower, Intent.EMERGENCY):
            logger.info("intent_classified", intent=Intent.EMERGENCY, query_length=len(query))
            return Intent.EMERGENCY

        # Check other intents
        for intent, patterns in self.patterns.items():
            if intent == Intent.EMERGENCY:
                continue
            if self._matches_patterns(query_lower, intent):
                logger.info("intent_classified", intent=intent.value, query_length=len(query))
                return intent

        logger.info("intent_classified", intent=Intent.UNKNOWN, query_length=len(query))
        return Intent.UNKNOWN

    def _matches_patterns(self, query: str, intent: Intent) -> bool:
        """Check if query matches any pattern for given intent."""
        patterns = self.patterns.get(intent, [])
        for pattern in patterns:
            if re.search(pattern, query):
                return True
        return False

    def get_confidence_hint(self, query: str) -> dict[str, float]:
        """
        Get confidence scores for all intents (simple heuristic).

        Args:
            query: User query string

        Returns:
            Dictionary of intent -> confidence score
        """
        query_lower = query.lower()
        scores: dict[str, float] = {}

        for intent, patterns in self.patterns.items():
            match_count = sum(
                1 for pattern in patterns if re.search(pattern, query_lower)
            )
            scores[intent.value] = min(match_count / len(patterns), 1.0) if patterns else 0.0

        return scores
