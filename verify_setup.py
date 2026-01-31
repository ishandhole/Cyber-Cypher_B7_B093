import sys
import os

print("Verifying imports...")
try:
    from core.state import AgentState
    from core.kafka import EventBus
    from agents.router import ThompsonSamplingRouter
    from agents.sentinel import CircuitBreakerSentinel
    from agents.recovery import RecoveryAgent
    from safety.validators import InputValidator
    from ui.dashboard import generate_mock_transaction
    from main import app
    from core.graph import payment_graph
    
    print("Imports successful.")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

print("Verifying Graph Compilation...")
try:
    # Just checking if it exists and is compiled
    assert payment_graph is not None
    print("Graph compiled successfully.")
except Exception as e:
    print(f"Graph verification failed: {e}")
    sys.exit(1)

print("System verification passed!")
