"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime settings with sensible defaults.

    Override any value by setting the corresponding environment variable
    or by placing a ``.env`` file in the project root.
    """

    app_name: str = "Asset Flow"
    app_version: str = "1.0.0"
    debug: bool = False

    # Upload limits
    max_file_size_mb: int = 10

    # Image conversion
    webp_quality: int = 80

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
