import asyncio
import json
from sqlalchemy import select
from app.models.payment import OutboxEvent
from app.core.database import async_session_maker
from app.worker.rabbitmq import setup_rabbitmq
import aio_pika

async def run_relay():
    connection, channel, exchange = await setup_rabbitmq()
    while True:
        async with async_session_maker() as db:
            query = (
                select(OutboxEvent)
                .where(OutboxEvent.status == "pending")
                .limit(50)
                .with_for_update(skip_locked=True)
            )
            result = await db.execute(query)
            events = result.scalars().all()
            
            for event in events:
                message = aio_pika.Message(
                    body=json.dumps(event.payload).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                )
                await exchange.publish(message, routing_key="payments.new.key")
                event.status = "processed"
            
            if events:
                await db.commit()
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_relay())
