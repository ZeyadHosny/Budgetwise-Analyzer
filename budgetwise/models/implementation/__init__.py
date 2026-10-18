"""
Description:
- The model classes themselves. Two modules:
      transaction.py   Transaction -> ExpenseTransaction, IncomeTransaction
      account.py       Account -> CashAccount, BankAccount, UnknownAccount

- Nothing is published from here. The contract other features import
  lives one level up in models/__init__.py, so a caller writes

      from budgetwise.models import ExpenseTransaction

  and never names the file a class happens to sit in. That leaves this
  folder free to split or rename a module without any caller changing.

- account.py imports two constants from transaction.py. They are
  siblings, so that is a single dot:  from .transaction import ...
"""
