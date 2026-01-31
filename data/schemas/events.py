from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TransactionEvent(BaseModel):
    transaction_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    merchant_id: str
    amount: float
    currency: str
    payment_method: str
    bin: Optional[str] = None
    
class PaymentResult(BaseModel):
    transaction_id: str
    gateway: str
    status: str # "success", "failure", "error"
    error_code: Optional[str] = None
    latency_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Intervention(BaseModel):
    transaction_id: str
    action: str # "retry", "change_route", "block", "alert"
    reason: str
    parameters: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
