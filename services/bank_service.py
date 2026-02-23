import aiohttp
from typing import Optional, Tuple

from config import settings


class BankService:
    """Service for bank API - auto approve deposit when amount and content match."""

    def __init__(self):
        self.enabled = settings.BANK_API_ENABLED
        self.base_url = settings.BANK_API_URL.rstrip("/")

    async def check_transaction(
        self,
        amount: int,
        content: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if bank API has a matching transaction.
        Returns (found_and_valid, error_message).
        """
        if not self.enabled or not self.base_url:
            return False, None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/check",
                    params={"amount": amount, "content": content},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        return False, "API error"
                    data = await resp.json()
                    if data.get("match"):
                        return True, None
                    return False, None
        except Exception:
            return False, None
