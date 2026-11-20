from fastapi import FastAPI, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentDetailResponse
from app.core.database import get_db
from app.core.config import settings
from app.services.payment_service import PaymentService
from app.models.payment import Base
from app.core.database import engine

app = FastAPI(title="Payment System")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key") #

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/api/v1/payments", response_model=PaymentResponse, status_code=202, dependencies=[Depends(verify_api_key)])
async def create_payment(
    payment_in: PaymentCreate, 
    idempotency_key: str = Header(...), 
    db: AsyncSession = Depends(get_db)
):
    service = PaymentService(db)
    return await service.create_payment(payment_in, idempotency_key)

@app.get("/api/v1/payments/{payment_id}", response_model=PaymentDetailResponse, dependencies=[Depends(verify_api_key)])
async def get_payment(payment_id: str, db: AsyncSession = Depends(get_db)):
    service = PaymentService(db)
    payment = await service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
