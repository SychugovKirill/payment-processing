import asyncio
import random
import json
import httpx
import aio_pika
from sqlalchemy import select
from app.models.payment import Payment, PaymentStatus
from app.core.database import async_session_maker
from app.worker.rabbitmq import setup_rabbitmq

async def process_message(message: aio_pika.abc.AbstractIncomingMessage, exchange: aio_pika.abc.AbstractExchange):
    async with message.process(ignore_processed=True):
        body = json.loads(message.body.decode())
        payment_id = body.get("payment_id")
        retry_count = message.headers.get("x-retry-count", 0)

        async with async_session_maker() as db:
            query = select(Payment).where(Payment.id == payment_id)
            result = await db.execute(query)
            payment = result.scalar_one_or_none()
            
            if not payment or payment.status != PaymentStatus.pending:
                return

            await asyncio.sleep(random.uniform(0.5, 1.0))
            is_success = random.random() < 0.9
            payment.status = PaymentStatus.succeeded if is_success else PaymentStatus.failed
            await db.commit()

            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        payment.webhook_url, 
                        json={"payment_id": payment_id, "status": payment.status.value},
                        timeout=5.0
                    )
            except Exception:
                if retry_count < 2: 
                    new_msg = aio_pika.Message(
                        body=message.body,
                        headers={"x-retry-count": retry_count + 1},
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    )
                    await asyncio.sleep(2 ** retry_count) #
                    await exchange.publish(new_msg, routing_key="payments.new.key")
                else:
                    await message.reject(requeue=False) #

async def run_consumer():
    connection, channel, exchange = await setup_rabbitmq()
    queue = await channel.get_queue("payments.new")
    await queue.consume(lambda msg: process_message(msg, exchange))
    print("Consumer is running...")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(run_consumer())
