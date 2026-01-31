from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel

class PaymentContext(BaseModel):
    transaction_id: str
    amount: float
    currency: str
    payment_method: str
    merchant_id: str
    client_metadata: Dict[str, Any] = {}

class AgentState(TypedDict):
    """
    Global state for the LangGraph workflow.
    """
    transaction_id: str
    payment_context: Dict[str, Any]  # Serialized PaymentContext
    
    # Decisions made by agents
    route_decision: Optional[str] = None # Selected gateway
    intervention_plan: Optional[str] = None # E.g., "retry_with_backoff", "block"
    
    # Execution results
    attempt_count: int
    last_error: Optional[str] = None
    success: bool
    
    # History of actions for learning
    history: List[Dict[str, Any]]
