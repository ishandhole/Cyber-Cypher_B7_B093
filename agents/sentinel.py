import time
from typing import Dict, List

class CircuitBreakerSentinel:
    def __init__(self, failure_threshold: float = 0.5, recovery_timeout: int = 30, window_size: int = 10):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.window_size = window_size
        
        # State: map gateway -> {state: "OPEN"|"CLOSED"|"HALF_OPEN", last_failure: ts, window: [bool]}
        self.state = {}
    
    def get_status(self, gateway: str) -> str:
        if gateway not in self.state:
            self.state[gateway] = {"status": "CLOSED", "last_failure_ts": 0, "window": []}
        
        state = self.state[gateway]
        
        if state["status"] == "OPEN":
            if time.time() - state["last_failure_ts"] > self.recovery_timeout:
                state["status"] = "HALF_OPEN"
                return "HALF_OPEN"
            return "OPEN"
            
        return state["status"]
    
    def record_result(self, gateway: str, success: bool):
        if gateway not in self.state:
            self.state[gateway] = {"status": "CLOSED", "last_failure_ts": 0, "window": []}
            
        gs = self.state[gateway]
        
        if gs["status"] == "HALF_OPEN":
            if success:
                gs["status"] = "CLOSED"
                gs["window"] = [True]
            else:
                gs["status"] = "OPEN"
                gs["last_failure_ts"] = time.time()
            return

        # Slide window
        gs["window"].append(success)
        if len(gs["window"]) > self.window_size:
            gs["window"].pop(0)
            
        # Check threshold
        failures = len([x for x in gs["window"] if not x])
        total = len(gs["window"])
        
        if total >= self.window_size and (failures / total) > self.failure_threshold:
            gs["status"] = "OPEN"
            gs["last_failure_ts"] = time.time()

    def get_all_statuses(self) -> Dict[str, Any]:
        """Returns the full state of all circuit breakers."""
        # Refresh statuses to catch timeouts
        for gw in list(self.state.keys()):
            self.get_status(gw)
        return self.state
