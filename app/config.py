from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Database
    database_url: str = Field(..., alias="DATABASE_URL")

    # API Security
    api_key: str = Field(..., alias="API_KEY")

    # OpenAI
    openai_api_key: str | None = Field(None, alias="OPENAI_API_KEY")

    # File Storage
    upload_dir: str = Field("/app/data/uploads", alias="UPLOAD_DIR")
    report_output_dir: str = Field("/app/data/reports", alias="REPORT_OUTPUT_DIR")

    # Zoho Integration
    zoho_client_id: str | None = Field(None, alias="ZOHO_CLIENT_ID")
    zoho_client_secret: str | None = Field(None, alias="ZOHO_CLIENT_SECRET")
    zoho_refresh_token: str | None = Field(None, alias="ZOHO_REFRESH_TOKEN")
    zoho_org_id: str | None = Field(None, alias="ZOHO_ORG_ID")
    zoho_base_url: str = Field("https://www.zohoapis.com", alias="ZOHO_BASE_URL")

    # Email (SendGrid)
    sendgrid_api_key: str | None = Field(None, alias="SENDGRID_API_KEY")
    sendgrid_from_email: str | None = Field(None, alias="SENDGRID_FROM_EMAIL")

    # Slack
    slack_bot_token: str | None = Field(None, alias="SLACK_BOT_TOKEN")
    slack_channel_finance: str | None = Field("#finance-reports", alias="SLACK_CHANNEL_FINANCE")
    slack_channel_marketing: str | None = Field("#marketing-reports", alias="SLACK_CHANNEL_MARKETING")

    # Report Scheduling
    finance_weekly_cron: str = Field("0 9 * * 1", alias="FINANCE_WEEKLY_CRON")  # Monday 9am
    finance_monthly_cron: str = Field("0 9 1 * *", alias="FINANCE_MONTHLY_CRON")  # 1st of month 9am
    marketing_weekly_cron: str = Field("0 10 * * 1", alias="MARKETING_WEEKLY_CRON")  # Monday 10am
    marketing_monthly_cron: str = Field("0 10 1 * *", alias="MARKETING_MONTHLY_CRON")  # 1st of month 10am

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
