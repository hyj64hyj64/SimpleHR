from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Simple HR"
    secret_key: str = "CHANGE_ME_TO_A_LONG_RANDOM_STRING"
    database_url: str = "sqlite:///./hr_app.db"

    # 🔹 NEW: QuickBooks scaffolding config
    qb_client_id: Optional[str] = None
    qb_client_secret: Optional[str] = None
    qb_redirect_uri: Optional[str] = None
    qb_environment: str = "sandbox"  # or "production"
    
    class Config:
        env_file = ".env"


settings = Settings()
