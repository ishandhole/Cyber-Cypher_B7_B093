from typing import Dict, Any, Optional

class RecoveryAgent:
    def __init__(self):
        pass
        
    def analyze_failure(self, error_code: str, history: list) -> Dict[str, Any]:
        """
        Reason about the failure. In a real system, this would call an LLM.
        Here we use heuristic logic to simulate the reasoning.
        """
        
        # Simple heuristics for demo
        # Simulated "LLM" reasoning
        
        reasoning_trace = f"""
        ANALYSIS OF FAILURE: {error_code}
        Observation: Gateway returned {error_code}.
        Context: {history}
        Knowledge:
        - TIMEOUT implies network congestion or downstream issues.
        - INSUFFICIENT_FUNDS is a user-side error.
        - FRAUD_BLOCK indicates high risk.
        - BANK_DECLINE is generic but sometimes retriable via premium routes.
        
        Reasoning:
        """
        
        if not error_code:
             return {
                "action": "none", 
                "reason": "No Error", 
                "summary": "Transaction successful or no error detected.", 
                "confidence": 1.0
            }

        if error_code == "TIMEOUT":
            reasoning_trace += "Error is transient. Immediate retry on a fresh connection is likely to succeed."
            return {
                "action": "retry", 
                "reason": reasoning_trace,
                "summary": "Transient network timeout detected. Creating retry plan.",
                "confidence": 0.9
            }
        elif error_code == "INSUFFICIENT_FUNDS":
            reasoning_trace += "Error is permanent (user-side). Retry will waste resources and increase costs."
            return {
                "action": "block",
                "reason": reasoning_trace,
                "summary": "User error (insufficient funds). Retrying will likely fail.",
                "confidence": 0.95
            }
        elif error_code == "BANK_DECLINE":
            reasoning_trace += "Error is generic. A different acquirer (Premium) might have better acceptance rates for this bin."
            return {
                "action": "retry_alternate",
                "reason": reasoning_trace,
                "summary": "Generic bank decline. Attempting alternate premium route.",
                "confidence": 0.6
            }
        elif error_code == "FRAUD_BLOCK":
            reasoning_trace += "Security risk active. Stopping transaction to prevent chargeback."
            return {
                "action": "block",
                "reason": reasoning_trace,
                "summary": "High fraud risk detected locally.",
                "confidence": 0.99
            }
            
        reasoning_trace += "Error code is unrecognized. Requires human analysis."
        return {
            "action": "escalate", 
            "reason": reasoning_trace, 
            "summary": "Unknown Error. Escalated to Ops Team.", 
            "confidence": 0.5
        }
