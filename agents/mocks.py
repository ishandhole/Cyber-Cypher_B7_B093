import random
import time
from typing import Dict, Any

class MockGateway:
    def __init__(self, name: str, success_rate: float, latency_mean: float, latency_std: float):
        self.name = name
        self.success_rate = success_rate
        self.latency_mean = latency_mean
        self.latency_std = latency_std
    
    def update_config(self, success_rate: float = None, latency_mean: float = None):
        if success_rate is not None:
            self.success_rate = success_rate
        if latency_mean is not None:
            self.latency_mean = latency_mean
    
    def process_payment(self, amount: float, currency: str) -> Dict[str, Any]:
        # Simulate latency
        latency = max(0.01, random.gauss(self.latency_mean, self.latency_std))
        time.sleep(latency)
        
        # Simulate outcome
        if random.random() < self.success_rate:
            return {
                "status": "success",
                "gateway": self.name,
                "latency_ms": latency * 1000,
                "error_code": None
            }
        else:
            # Simulate different error types
            error_code = random.choice(["TIMEOUT", "INSUFFICIENT_FUNDS", "BANK_DECLINE", "FRAUD_BLOCK"])
            return {
                "status": "failure",
                "gateway": self.name,
                "latency_ms": latency * 1000,
                "error_code": error_code
            }

GATEWAYS = {
    "Issuer_Alpha": MockGateway("Issuer_Alpha", 0.95, 0.2, 0.05),
    "Issuer_Beta": MockGateway("Issuer_Beta", 0.90, 0.3, 0.1),
    "Issuer_Gamma": MockGateway("Issuer_Gamma", 0.85, 0.5, 0.2)
}
