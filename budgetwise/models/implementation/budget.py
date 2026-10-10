"""Monthly category budget and spending comparison."""

import math


class Budget:
    """Compare spending with a monthly category limit."""

    def __init__(self, category: str, monthly_limit: float):
        if not isinstance(category, str) or not category.strip():
            raise ValueError("Category must be a non-empty string.")

        self.__category = category.strip()
        self.set_monthly_limit(monthly_limit)

    def get_category(self) -> str:
        return self.__category

    def get_monthly_limit(self) -> float:
        return self.__monthly_limit

    def set_monthly_limit(self, value: float) -> None:
        self.__monthly_limit = self._validate_amount(
            value, "Monthly limit"
        )

    @staticmethod
    def _validate_amount(value: float, name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number.")

        amount = float(value)

        if not math.isfinite(amount) or amount < 0:
            raise ValueError(f"{name} must be finite and non-negative.")

        return amount

    def status(self, actual_spending: float) -> tuple[str, float]:
        actual = self._validate_amount(
            actual_spending, "Actual spending"
        )

        if actual > self.__monthly_limit:
            return "over", actual - self.__monthly_limit

        if actual < self.__monthly_limit:
            return "under", self.__monthly_limit - actual

        return "equal", 0.0
