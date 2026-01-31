from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
from core.state import AgentState, PaymentContext
from agents.router import ThompsonSamplingRouter
from agents.sentinel import CircuitBreakerSentinel
from agents.recovery import RecoveryAgent
from agents.tools import execute_payment
import logging

logger = logging.getLogger("orchestrator")

# Initialize Agents
# In a real app, these might be singletons or injected
gateways = ["Issuer_Alpha", "Issuer_Beta", "Issuer_Gamma"]
router = ThompsonSamplingRouter(gateways)
sentinel = CircuitBreakerSentinel()
recovery = RecoveryAgent()

def route_step(state: AgentState) -> AgentState:
    """
    Selects the best gateway using Thompson Sampling.
    """
    # If a route was already forced by recovery, use it
    if state.get("intervention_plan") == "retry_alternate" and state.get("route_decision"):
        # The recovery agent might have set a specific route or we might just re-route
        # For simple retry_alternate, let's pick a random one that isn't the previous one?
        # For simplicity in this demo, we just let the router pick again, hoping for a different result
        # or we could explicitly exclude the failing one.
        pass
    
    selected_gateway = router.select_gateway()
    
    # Check circuit breaker
    status = sentinel.get_status(selected_gateway)
    if status == "OPEN":
        logger.warning(f"Gateway {selected_gateway} is OPEN. Rerouting...")
        # Simple retry logic internally to pick another if open? 
        # Or just let it fail and let recovery handle it?
        # Ideally, router should know about availability. 
        # For this demo, we'll try to pick another one if the first is open.
        for gw in gateways:
            if sentinel.get_status(gw) != "OPEN":
                selected_gateway = gw
                break
    
    state["route_decision"] = selected_gateway
    state["history"].append({"step": "route", "gateway": selected_gateway, "status": sentinel.get_status(selected_gateway)})
    return state

def execute_step(state: AgentState) -> AgentState:
    """
    Executes the payment on the selected gateway.
    """
    gateway = state["route_decision"]
    context = state["payment_context"]
    
    logger.info(f"Executing payment {context['transaction_id']} via {gateway}")
    
    result = execute_payment(gateway, context["amount"], context["currency"])
    
    success = result["status"] == "success"
    state["success"] = success
    
    if not success:
        state["last_error"] = result["error_code"]
        state["history"].append({"step": "execute", "result": "failure", "error": result["error_code"]})
        # Update components
        router.update(gateway, success=False)
        sentinel.record_result(gateway, success=False)
    else:
        state["history"].append({"step": "execute", "result": "success"})
        router.update(gateway, success=True)
        sentinel.record_result(gateway, success=True)
        
    return state

def recovery_step(state: AgentState) -> AgentState:
    """
    Analyzes failure and decides on intervention.
    """
    error = state["last_error"]
    analysis = recovery.analyze_failure(error, state["history"])
    
    state["intervention_plan"] = analysis["action"]
    state["history"].append({"step": "recovery", "analysis": analysis})
    
    logger.info(f"Recovery analysis: {analysis}")
    
    return state

def should_retry(state: AgentState) -> Literal["route_step", "end"]:
    """
    Conditional edge to determine if we should retry.
    """
    plan = state.get("intervention_plan")
    
    if state["success"]:
        return "end"
        
    if state["attempt_count"] >= 3:
        logger.info("Max retries reached.")
        return "end"
        
    if plan in ["retry", "retry_alternate"]:
        state["attempt_count"] += 1
        return "route_step"
        
    return "end"

# Build Graph
graph_builder = StateGraph(AgentState)

graph_builder.add_node("route_step", route_step)
graph_builder.add_node("execute_step", execute_step)
graph_builder.add_node("recovery_step", recovery_step)

graph_builder.set_entry_point("route_step")

graph_builder.add_edge("route_step", "execute_step")
graph_builder.add_edge("execute_step", "recovery_step")
graph_builder.add_conditional_edges("recovery_step", should_retry, {
    "route_step": "route_step",
    "end": END
})

payment_graph = graph_builder.compile()
