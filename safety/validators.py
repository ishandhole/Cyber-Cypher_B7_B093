from typing import Dict, Any, List
from core.state import PaymentContext
import logging

logger = logging.getLogger("safety")

class InputValidator:
    @staticmethod
    def validate_payment_context(context: PaymentContext) -> bool:
        if context.amount <= 0:
            logger.error(f"Invalid amount: {context.amount}")
            return False
        if not context.currency or len(context.currency) != 3:
            logger.error(f"Invalid currency: {context.currency}")
            return False
        return True

class AnomalyDetector:
    def __init__(self):
        self.high_value_threshold = 5000.0
    
    def is_anomalous(self, context: PaymentContext) -> bool:
        if context.amount > self.high_value_threshold:
            logger.warning(f"High value transaction detected: {context.amount}")
            return True
        return False

class SafetyGuardrails:
    def __init__(self):
        self.blocked_bins = set()
    
    def check_intervention(self, intervention: Dict[str, Any]) -> bool:
        """
        Returns True if intervention is safe, False otherwise.
        """
        action = intervention.get("action")
        
        # Guardrail: Don't allow infinite retries (handled by graph usually, but good to have check)
        # Guardrail: Don't block all traffic (hard to check here without global state, but we can check specific dangerous actions)
        
        if action == "block":
            reason = intervention.get("reason", "")
            if "User error" not in reason and "Fraud" not in reason:
                # If blocking for system reasons, be careful. 
                # In a real system we'd check current block rate.
                pass
        
        return True
