"""Monthly spending limit and over/under comparison."""

from math import isfinite


class Budget:
    """A category's monthly spending limit."""

    def __init__(self, category, monthly_limit):
        if not isinstance(category, str):
            raise TypeError("category must be text")
        category = category.strip()
        if not category:
            raise ValueError("category must not be empty")

        self.__category = category
        self.__monthly_limit = self._validated_amount(
            monthly_limit, "monthly_limit"
        )

    def get_category(self):
        """Return the category this limit applies to."""
        return self.__category

    def get_monthly_limit(self):
        """Return the nonnegative monthly spending limit."""
        return self.__monthly_limit

    def status(self, actual):
        """Return (status, actual minus limit) for a month's actual spend."""
        actual = self._validated_amount(actual, "actual")
        difference = actual - self.__monthly_limit
        if difference > 0:
            return "over", difference
        if difference < 0:
            return "under", difference
        return "exact", 0.0

    @staticmethod
    def _validated_amount(value, name):
        if isinstance(value, bool):
            raise TypeError(f"{name} must be numeric")
        try:
            amount = float(value)
        except (TypeError, ValueError, OverflowError):
            raise ValueError(f"{name} must be numeric") from None
        if not isfinite(amount) or amount < 0:
            raise ValueError(f"{name} must be finite and nonnegative")
        return amount