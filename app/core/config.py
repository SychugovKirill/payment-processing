from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str = "static-secret-key"
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/payments_db"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    
    class Config:
        env_file = ".env"

settings = Settings()
