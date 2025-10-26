from pydantic_settings import BaseSettings
from pydantic import Field
class Settings(BaseSettings):
    database_url: str = Field(..., alias="DATABASE_URL")
    api_key: str = Field(..., alias="API_KEY")
    openai_api_key: str | None = Field(None, alias="OPENAI_API_KEY")
    upload_dir: str = Field("/app/data/uploads", alias="UPLOAD_DIR")
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
settings = Settings()
