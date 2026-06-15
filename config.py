from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    allowed_frontend_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_frontend_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_frontend_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()