import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: List[int] = [
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    ]
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./data/bot.db"
    )
    BANK_API_ENABLED: bool = os.getenv("BANK_API_ENABLED", "false").lower() == "true"
    BANK_API_URL: str = os.getenv("BANK_API_URL", "")
    DAILY_RESET_HOUR: int = int(os.getenv("DAILY_RESET_HOUR", "0"))

    # Game
    MIN_BET: int = 10_000
    MAX_BET: int = 1_000_000
    PAYOUT_NORMAL: float = 1.93
    PAYOUT_MAX_BET: float = 1.87
    TAI_MIN: int = 11
    TAI_MAX: int = 18

    # Bonus
    WELCOME_BONUS: int = 20_000
    WAGER_REQUIREMENT: int = 300_000
    CASHBACK_RATE: float = 0.005  # 0.5%

    # Withdraw
    MIN_WITHDRAW: int = 200_000
    MAX_WITHDRAW_PER_DAY: int = 5
    TICKET_INACTIVITY_MINUTES: int = 10

    # Admin bank (for deposit instructions)
    ADMIN_BANK_NAME: str = os.getenv("ADMIN_BANK_NAME", "Ngân hàng TMCP")
    ADMIN_BANK_NUMBER: str = os.getenv("ADMIN_BANK_NUMBER", "1234567890")
    ADMIN_BANK_HOLDER: str = os.getenv("ADMIN_BANK_HOLDER", "CONG TY SICBO")


settings = Settings()
