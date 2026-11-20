### Запуск проекта

```docker-compose up -d --build```

### API endpoints

#### Авторизация

Все запросы требуют статический ключ в заголовке:

```X-API-Key: static-secret-key```

1. Создание платежа

```POST /api/v1/payments```

Request:

```curl -X POST http://localhost:8080/api/v1/payments \
     -H "Content-Type: application/json" \
     -H "X-API-Key: static-secret-key" \
     -H "Idempotency-Key: unique-task-id-001" \
     -d '{
       "amount": 1500.00,
       "currency": "RUB",
       "description": "Оплата заказа #123",
       "metadata": {"user_id": 42},
       "webhook_url": "https://httpbin.org/post"
     }'
```

2. Получение информации о платеже

```GET /api/v1/payments/{payment_id}```

Request:

```
curl -H "X-API-Key: static-secret-key" \
     http://localhost:8080/api/v1/payments/UUID_ПЛАТЕЖА
```

### Мониторинг и отладка

- Swagger UI: http://localhost:8080/docs

- RabbitMQ Management: http://localhost:15672 (guest/guest)

- Логи воркера: docker-compose logs -f consumer