from agents.mocks import GATEWAYS
from typing import Dict, Any

def execute_payment(gateway_name: str, amount: float, currency: str) -> Dict[str, Any]:
    if gateway_name not in GATEWAYS:
        return {
            "status": "error",
            "gateway": gateway_name,
            "latency_ms": 0,
            "error_code": "GATEWAY_NOT_FOUND"
        }
    
    return GATEWAYS[gateway_name].process_payment(amount, currency)
