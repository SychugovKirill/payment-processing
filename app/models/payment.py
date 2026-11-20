from datetime import datetime
from sqlalchemy import Column, String, Numeric, JSON, Enum, DateTime, func, Integer
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True, index=True) #
    amount = Column(Numeric, nullable=False) #
    currency = Column(String, nullable=False) #
    description = Column(String) #
    metadata_ = Column("metadata", JSON) #
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending) #
    idempotency_key = Column(String, unique=True, index=True, nullable=False) #
    webhook_url = Column(String, nullable=False) #
    created_at = Column(DateTime, default=func.now()) #
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class OutboxEvent(Base):
    __tablename__ = "outbox"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String, default="pending") # pending, processed
    created_at = Column(DateTime, default=func.now())
