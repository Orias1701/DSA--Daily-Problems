from config import settings


class GameService:
    TAI = "tai"
    XIU = "xiu"
    TAI_RANGE = (11, 18)
    XIU_RANGE = (3, 10)

    @staticmethod
    def get_payout_multiplier(amount: int) -> float:
        if amount >= settings.MAX_BET:
            return settings.PAYOUT_MAX_BET
        return settings.PAYOUT_NORMAL

    @staticmethod
    def check_win(choice: str, total: int) -> bool:
        if choice == GameService.TAI:
            return GameService.TAI_RANGE[0] <= total <= GameService.TAI_RANGE[1]
        return GameService.XIU_RANGE[0] <= total <= GameService.XIU_RANGE[1]

    @staticmethod
    def calculate_profit(amount: int, won: bool, multiplier: float) -> int:
        if won:
            return int(amount * multiplier) - amount
        return -amount

    @staticmethod
    def calculate_cashback(wager: int, rate: float) -> int:
        return int(wager * rate)
