import asyncio
import aio_pika
from app.core.config import settings

async def setup_rabbitmq(retries=5, delay=3):
    connection = None
    for attempt in range(retries):
        try:
            connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            print("Connected to RabbitMQ")
            break
        except Exception:
            await asyncio.sleep(delay)
            
    if not connection:
        raise ConnectionError("RabbitMQ unavailable")

    channel = await connection.channel()
    dlx = await channel.declare_exchange("dlx_exchange", aio_pika.ExchangeType.DIRECT)
    dlq = await channel.declare_queue("payments.dlq", durable=True)
    await dlq.bind(dlx, routing_key="payments.dlq.key")
    
    main_exchange = await channel.declare_exchange("payments_exchange", aio_pika.ExchangeType.DIRECT)
    main_queue = await channel.declare_queue(
        "payments.new", 
        durable=True,
        arguments={
            "x-dead-letter-exchange": "dlx_exchange",
            "x-dead-letter-routing-key": "payments.dlq.key"
        }
    )
    await main_queue.bind(main_exchange, routing_key="payments.new.key")
    return connection, channel, main_exchange
