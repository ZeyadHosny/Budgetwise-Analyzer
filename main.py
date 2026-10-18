"""BudgetWise Personal Finance & Spending Analyzer.

Entry point. Run with:

    python main.py

This file stays small on purpose. It wires the program together and hands
control to the menu; all the work happens in the budgetwise package.
"""
from budgetwise.interface.menu import run_menu


def main() -> None:
    run_menu()


if __name__ == "__main__":
    main()
