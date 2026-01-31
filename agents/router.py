import numpy as np
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("router")

class ThompsonSamplingRouter:
    def __init__(self, gateways: List[str]):
        self.gateways = gateways
        # Initialize Beta distribution parameters: alpha=1 (successes), beta=1 (failures)
        self.counts = {gw: {"alpha": 1.0, "beta": 1.0} for gw in gateways}
    
    def select_gateway(self) -> str:
        sampled_probs = {}
        for gw in self.gateways:
            # Sample from Beta(alpha, beta)
            sampled_probs[gw] = np.random.beta(self.counts[gw]["alpha"], self.counts[gw]["beta"])
        
        selected = max(sampled_probs, key=sampled_probs.get)
        logger.info(f"Router selected {selected} (probs: {sampled_probs})")
        return selected
    
    def update(self, gateway: str, success: bool):
        if gateway not in self.counts:
            return
        
        if success:
            self.counts[gateway]["alpha"] += 1
        else:
            self.counts[gateway]["beta"] += 1

    def get_state(self) -> Dict[str, Dict[str, float]]:
        return self.counts
