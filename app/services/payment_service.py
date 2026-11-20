import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment, OutboxEvent, PaymentStatus
from app.schemas.payment import PaymentCreate

class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(self, payment_in: PaymentCreate, idempotency_key: str):
        # Проверка идемпотентности
        query = select(Payment).where(Payment.idempotency_key == idempotency_key)
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        payment_id = str(uuid.uuid4())
        new_payment = Payment(
            id=payment_id,
            idempotency_key=idempotency_key,
            status=PaymentStatus.pending,
            **payment_in.model_dump(by_alias=True)
        )
        
        # Outbox Pattern
        outbox_event = OutboxEvent(
            event_type="payments.new",
            payload={"payment_id": payment_id}
        )
        
        self.db.add(new_payment)
        self.db.add(outbox_event)
        await self.db.commit()
        await self.db.refresh(new_payment)
        return new_payment

    async def get_payment(self, payment_id: str):
        query = select(Payment).where(Payment.id == payment_id) #
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
