from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import List, Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    BOT_TOKEN: str
    DB_URL: str
    ADMIN_IDS: str
    ADMIN_IDS_LIST: List[int] = Field(default_factory=list)

    @validator('ADMIN_IDS_LIST', pre=True, always=True)
    def parse_admin_ids(cls, v, values):
        if 'ADMIN_IDS' in values and values['ADMIN_IDS']:
            return [int(uid.strip()) for uid in values['ADMIN_IDS'].split(',')]
        return []

    YOOKASSA_SHOP_ID: Optional[str] = None
    YOOKASSA_SECRET_KEY: Optional[str] = None
    YOOKASSA_TRUSTED_IPS: List[str] = Field(default=[
        "185.71.76.0/27",
        "185.71.77.0/27",
        "77.75.153.0/25",
        "77.75.154.128/25",
        "77.75.156.11",
        "77.75.156.35",
        "2a02:5180::/32"
    ])

    CLOUDPAYMENTS_PUBLIC_ID: Optional[str] = None
    CLOUDPAYMENTS_API_SECRET: Optional[str] = None

    TELEGRAM_PAYMENT_PROVIDER_TOKEN: Optional[str] = None

    XUI_API_URL: str
    XUI_API_USER: str
    XUI_API_PASSWORD: str

    ENCRYPTION_KEY: str

    SUPPORT_CHAT_LINK: Optional[str] = None
    VPN_INFO_POST_URL: Optional[str] = None
    PRIVACY_POLICY_URL: Optional[str] = None
    TERMS_OF_SERVICE_URL: Optional[str] = None

    TRIAL_SERVER_ID: Optional[int] = None

    CRYPTO_YEARLY_PRICE_USD: Optional[int] = None
    CRYPTO_BTC_ADDRESS: Optional[str] = None
    CRYPTO_ETH_ADDRESS: Optional[str] = None
    CRYPTO_USDT_TRC20_ADDRESS: Optional[str] = None

    CRYPTOBOT_TOKEN: Optional[str] = None
    CURRENCY_EXCHANGE_API_URL: Optional[str] = None

settings = Settings()