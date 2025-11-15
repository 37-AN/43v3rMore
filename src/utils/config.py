"""Configuration management using Pydantic settings."""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Quantum Trading AI"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""
    database_url: str = ""

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # MetaTrader 5
    mt5_login: int = 0
    mt5_password: str = ""
    mt5_server: str = ""
    mt5_timeout: int = 60000

    # IBM Quantum
    ibm_quantum_token: str = ""
    ibm_quantum_backend: str = "ibmq_qasm_simulator"

    # Anthropic Claude
    anthropic_api_key: str = ""
    claude_model: str = "claude-3-sonnet-20240229"

    # Telegram
    telegram_bot_token: str = ""
    telegram_admin_chat_id: str = ""

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""
    twilio_phone_from: str = ""

    # SendGrid
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = ""

    # PayFast
    payfast_merchant_id: str = ""
    payfast_merchant_key: str = ""
    payfast_passphrase: str = ""
    payfast_sandbox: bool = True

    # Monitoring
    sentry_dsn: str = ""
    prometheus_port: int = 9090

    # Trading Configuration
    default_symbols: str = "EURUSD,GBPUSD,USDJPY,XAUUSD"
    signal_confidence_threshold: float = 0.75
    max_daily_signals: int = 10
    backtest_start_date: str = "2023-01-01"
    backtest_end_date: str = "2024-01-01"

    # Business Configuration
    free_trial_days: int = 7
    basic_plan_price: int = 500
    pro_plan_price: int = 1000
    premium_plan_price: int = 2000
    bot_license_price: int = 3000
    enterprise_price: int = 10000
    currency: str = "ZAR"

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # CORS
    cors_origins: str = "http://localhost:3000"
    cors_allow_credentials: bool = True

    @property
    def symbols_list(self) -> List[str]:
        """Parse comma-separated symbols into list."""
        return [s.strip() for s in self.default_symbols.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into list."""
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings

    Example:
        >>> settings = get_settings()
        >>> print(settings.app_name)
        'Quantum Trading AI'
    """
    return Settings()
