def format_currency(amount: int) -> str:
    return f"{amount:,}".replace(",", ".")


def format_number(value: int | float) -> str:
    if isinstance(value, float):
        return f"{value:,.2f}".replace(",", ".")
    return f"{value:,}".replace(",", ".")
