from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Директории конфигов Trino
    TRINO_CONFIG_DIR: Path = Path("/etc/trino")
    TRINO_CATALOG_DIR: Path = Path("/etc/trino/catalog")

    # Команда reload
    TRINO_RELOAD_COMMAND: str = "kill -HUP $(cat /var/trino/data/var/run/launcher.pid)"

    # Веб-интерфейс
    SECRET_KEY: str = "change-me-in-production"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"

    # Trino
    TRINO_HOST: str = "localhost"
    TRINO_PORT: int = 8080

    class Config:
        env_file = ".env"


settings = Settings()
