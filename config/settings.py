import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _int_env(key: str, default: int) -> int:
    val = os.getenv(key)
    if val is None or val.strip() == "":
        return default
    try:
        return int(val.strip().replace("_", "").replace(",", ""))
    except ValueError:
        return default


def _float_env(key: str, default: float) -> float:
    val = os.getenv(key)
    if val is None or val.strip() == "":
        return default
    try:
        return float(val.strip())
    except ValueError:
        return default


def _int_list_env(key: str, default: List[int]) -> List[int]:
    val = os.getenv(key)
    if val is None or val.strip() == "":
        return default
    out: List[int] = []
    for part in val.split(","):
        part = part.strip().replace("_", "").replace(".", "")
        if part.isdigit():
            out.append(int(part))
    return out if out else default


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
    DAILY_RESET_HOUR: int = _int_env("DAILY_RESET_HOUR", 0)

    # Game (cược Tài Xỉu)
    MIN_BET: int = _int_env("MIN_BET", 10_000)
    MAX_BET: int = _int_env("MAX_BET", 1_000_000)
    PAYOUT_NORMAL: float = _float_env("PAYOUT_NORMAL", 1.93)
    PAYOUT_MAX_BET: float = _float_env("PAYOUT_MAX_BET", 1.87)
    TAI_MIN: int = _int_env("TAI_MIN", 11)
    TAI_MAX: int = _int_env("TAI_MAX", 18)
    # Các mức cược hiển thị trên nút (VNĐ), cách nhau bằng dấu phẩy
    BET_AMOUNT_PRESETS: List[int] = _int_list_env(
        "BET_AMOUNT_PRESETS", [10_000, 50_000, 100_000, 500_000, 1_000_000]
    )

    # Bonus
    WELCOME_BONUS: int = _int_env("WELCOME_BONUS", 20_000)
    WAGER_REQUIREMENT: int = _int_env("WAGER_REQUIREMENT", 300_000)
    CASHBACK_RATE: float = _float_env("CASHBACK_RATE", 0.005)  # 0.5%

    # Nạp tiền
    MIN_DEPOSIT: int = _int_env("MIN_DEPOSIT", 10_000)

    # Withdraw
    MIN_WITHDRAW: int = _int_env("MIN_WITHDRAW", 200_000)
    MAX_WITHDRAW_PER_DAY: int = _int_env("MAX_WITHDRAW_PER_DAY", 5)
    TICKET_INACTIVITY_MINUTES: int = _int_env("TICKET_INACTIVITY_MINUTES", 10)

    # Admin bank (thông tin nhận tiền nạp – có thể đổi trong .env)
    ADMIN_BANK_NAME: str = os.getenv("ADMIN_BANK_NAME", "Ngân hàng TMCP")
    ADMIN_BANK_NUMBER: str = os.getenv("ADMIN_BANK_NUMBER", "1234567890")
    ADMIN_BANK_HOLDER: str = os.getenv("ADMIN_BANK_HOLDER", "CONG TY SICBO")
    ADMIN_BANK_BIN: str = os.getenv("ADMIN_BANK_BIN", "")
    VIETQR_TEMPLATE: str = os.getenv("VIETQR_TEMPLATE", "compact2")


settings = Settings()
