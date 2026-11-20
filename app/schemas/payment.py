from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.payment import PaymentStatus

class PaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(..., pattern="^(RUB|USD|EUR)$")
    description: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    webhook_url: str

class PaymentResponse(BaseModel):
    id: str
    status: PaymentStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PaymentDetailResponse(PaymentResponse):
    amount: Decimal
    currency: str
    description: Optional[str]
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    webhook_url: str
    idempotency_key: str
