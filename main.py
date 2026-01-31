from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import logging
from core.state import AgentState, PaymentContext
from core.graph import payment_graph

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="Payment Agent API")

class TransactionRequest(BaseModel):
    transaction_id: str
    amount: float
    currency: str
    payment_method: str
    merchant_id: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/process")
def process_payment(tx: TransactionRequest):
    logger.info(f"Received transaction: {tx.transaction_id}")
    
    # Initialize state
    initial_state = AgentState(
        transaction_id=tx.transaction_id,
        payment_context=tx.dict(),
        route_decision=None,
        intervention_plan=None,
        attempt_count=0,
        last_error=None,
        success=False,
        history=[]
    )
    
    # Invoke LangGraph
    final_state = payment_graph.invoke(initial_state)
    
    # Return result
    return {
        "transaction_id": final_state["transaction_id"],
        "success": final_state["success"],
        "route_decision": final_state["route_decision"],
        "intervention_plan": final_state["intervention_plan"],
        "last_error": final_state["last_error"],
        "history": final_state["history"]
    }

@app.get("/system/status")
def get_system_status():
    """
    Returns the internal state of the agentic system.
    """
    # Import singletons from graph module
    from core.graph import router, sentinel
    
    return {
        "router": router.get_state(),
        "sentinel": sentinel.get_all_statuses()
    }

class ConfigRequest(BaseModel):
    gateway: str
    success_rate: float
    latency_mean: float

@app.post("/system/config")
def update_config(config: ConfigRequest):
    """
    Updates the mock gateway configuration.
    """
    from agents.mocks import GATEWAYS
    
    if config.gateway not in GATEWAYS:
        raise HTTPException(status_code=404, detail="Gateway not found")
        
    GATEWAYS[config.gateway].update_config(
        success_rate=config.success_rate,
        latency_mean=config.latency_mean
    )
    
    return {"status": "updated", "gateway": config.gateway}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
