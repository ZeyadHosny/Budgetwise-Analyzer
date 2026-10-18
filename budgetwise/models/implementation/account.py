# The two groups are importable by name.
# transaction.py is a sibling module in this folder.
from .transaction import EXPENSE_TYPE, INCOME_TYPE

# Kind label for physical money. 3,799 rows, 25% of the dataset.
CASH_KIND = "cash"
# Kind label for money held at an institution. 11,293 rows, 71%.
BANK_KIND = "bank"
# Kind label for rows whose payment_mode was blank. 808 rows, 5%.
UNKNOWN_KIND = "unknown"


class Account:
    """
    Description:
    - A ledger of transactions grouped by how they were paid.
    - Base class for CashAccount, BankAccount and UnknownAccount. Never
      instantiated directly: is_reconcilable and describe have no sensible
      answer until a subclass supplies one.
    - An Account HAS transactions, which is aggregation and not
      inheritance. The same transaction objects also live in the
      pipeline's full list, so neither owns the other.

    Attributes:
        __kind (str): PRIVATE. 'cash', 'bank' or 'unknown'. Set once at
            construction and never reassigned.
        __transactions (list): PRIVATE. The transactions this ledger
            holds. Read only through get_transactions, which returns a
            copy, so no caller can corrupt the ledger from outside.

    Methods:
        __init__: constructor.
        get_kind: the kind of ledger this is.
        add_transaction: append one transaction.
        get_transactions: a COPY of the held transactions.
        get_transaction_count: how many are held.
        get_total_spent: the sum of the expenses held.
        get_total_received: the sum of the income held.
        format_totals: the count and both totals as one shared phrase.
        is_reconcilable: ABSTRACT. Whether these can be audited.
        describe: ABSTRACT. A one-line summary for the menu.
    """

    # Constructor
    def __init__(self, kind):
        """
        Description:
        - Constructor for the Account class.
        - Starts with an empty ledger. Transactions arrive only through
          add_transaction.

        Input arguments:
           kind (str): 'cash', 'bank' or 'unknown'.

        Return:
            None
        """
        self.__kind = str(kind)
        self.__transactions = []

    # Method to read the private kind
    def get_kind(self):
        """
        Description:
        - Return the kind of ledger this is.
        - There is no matching setter, so a cash ledger can never start
          claiming to be a bank ledger.

        Input arguments:
           None

        Return:
            str: 'cash', 'bank' or 'unknown'.
        """
        return self.__kind

    # Method to add one transaction to the ledger
    def add_transaction(self, transaction):
        """
        Description:
        - Append one transaction to this ledger.

        Input arguments:
           transaction (Transaction): The transaction to hold.

        Return:
            None
        """
        self.__transactions.append(transaction)

    # Method to read the held transactions
    def get_transactions(self):
        """
        Description:
        - Return the held transactions as a COPY, so a caller cannot
          append to or clear the ledger from outside. This is part of the
          encapsulation.

        Input arguments:
           None

        Return:
            list: A new list holding the same transaction objects.
        """
        return list(self.__transactions)

    # Method to count the held transactions
    def get_transaction_count(self):
        """
        Description:
        - Count the transactions this ledger holds.

        Input arguments:
           None

        Return:
            int: The number of transactions.
        """
        return len(self.__transactions)

    # Method to calculate the total spent
    def get_total_spent(self):
        """
        Description:
        - Add up the expenses held by this ledger.

        Input arguments:
           None

        Return:
            float: The sum of the expense magnitudes. 0.0 when empty.
        """
        return float(sum(transaction.get_amount()
                         for transaction in self.__transactions
                         if transaction.get_transaction_type() == EXPENSE_TYPE))

    # Method to calculate the total received
    def get_total_received(self):
        """
        Description:
        - Add up the income held by this ledger.

        Input arguments:
           None

        Return:
            float: The sum of the income magnitudes. 0.0 when empty.
        """
        return float(sum(transaction.get_amount()
                         for transaction in self.__transactions
                         if transaction.get_transaction_type() == INCOME_TYPE))

    # Method to format the part of the summary every ledger shares
    def format_totals(self):
        """
        Description:
        - Return the count and both money totals as one phrase, so the
          three describe overrides do not each repeat the formatting.
        - Lives on the base class because it is identical for all three
          ledgers; only the wording around it differs.

        Input arguments:
           None

        Return:
            str: e.g. '2 transactions, spent 4,363.00, received 0.00'.
        """
        return (f"{self.get_transaction_count()} transactions, "
                f"spent {self.get_total_spent():,.2f}, "
                f"received {self.get_total_received():,.2f}")

    # Method to say whether these transactions can be audited
    def is_reconcilable(self):
        """
        Description:
        - ABSTRACT. Say whether these transactions can be checked against
          an outside record.
        - Raises rather than returning a default. There is no sensible
          default: if the base returned True then BankAccount overriding
          it to True would be a pointless override, and if it returned
          False the base would be asserting something about a ledger whose
          kind is not yet known.

        Input arguments:
           None

        Return:
            Never returns (always raises NotImplementedError)
        """
        raise NotImplementedError(
            "is_reconcilable depends on the payment method - use "
            "CashAccount, BankAccount or UnknownAccount.")

    # Method to summarize the ledger for the menu
    def describe(self):
        """
        Description:
        - ABSTRACT. Return a one-line summary naming what makes this
          ledger different from the others, built around format_totals.
        - Raises for the same reason as is_reconcilable: the base class
          has nothing distinctive to describe.

        Input arguments:
           None

        Return:
            Never returns (always raises NotImplementedError)
        """
        raise NotImplementedError(
            "describe depends on the payment method - use CashAccount, "
            "BankAccount or UnknownAccount.")

    # Method to show the object during debugging
    def __repr__(self):
        """
        Description:
        - Return a short identifying form of this ledger.
        - Deliberately reads only the count, never the totals. A __repr__
          that walked the transaction list could raise if one held object
          was malformed, and a raising __repr__ breaks debuggers and
          error messages at exactly the moment they are needed.

        Input arguments:
           None

        Return:
            str: e.g. "BankAccount('bank', 2 transactions)".
        """
        return (f"{type(self).__name__}({self.__kind!r}, "
                f"{self.get_transaction_count()} transactions)")


class CashAccount(Account):
    """
    Description:
    - Physical money. 3,799 rows, ~25% of the dataset.
    - Overrides both abstract methods.

    Attributes:
        Inherited from Account. Adds none of its own.

    Methods:
        __init__: constructor.
        is_reconcilable: OVERRIDE. Returns False.
        describe: OVERRIDE. Names the limitation.
    """

    # Constructor
    def __init__(self):
        """
        Description:
        - Constructor for the CashAccount class.
        - Takes no arguments and fixes the kind, so a caller cannot build
          a cash ledger that reports itself as a bank ledger.

        Input arguments:
           None

        Return:
            None
        """
        super().__init__(CASH_KIND)

    # Method to say whether these transactions can be audited
    def is_reconcilable(self):
        """
        Description:
        - OVERRIDE. Cash carries no transaction reference, so there is
          nothing to match against a statement.

        Input arguments:
           None

        Return:
            bool: False.
        """
        return False

    # Method to summarize the ledger for the menu
    def describe(self):
        """
        Description:
        - OVERRIDE. Names the limitation: cash cannot be verified.

        Input arguments:
           None

        Return:
            str: e.g. 'Cash - 2 transactions, spent 4,363.00, received
                 0.00, no transaction reference, cannot be verified'.
        """
        return (f"Cash - {self.format_totals()}, "
                f"no transaction reference, cannot be verified")


class BankAccount(Account):
    """
    Description:
    - Money held at an institution: Card, UPI or Bank Transfer.
      11,293 rows, ~70% of the dataset.
    - Overrides both abstract methods. Holds no attributes and adds no
      methods of its own: what distinguishes it is that it answers
      is_reconcilable with True while the other two answer False.

    Attributes:
        Inherited from Account. Adds none of its own.

    Methods:
        __init__: constructor.
        is_reconcilable: OVERRIDE. Returns True.
        describe: OVERRIDE.
    """

    # Constructor
    def __init__(self):
        """
        Description:
        - Constructor for the BankAccount class.
        - Takes no arguments and fixes the kind to 'bank'.

        Input arguments:
           None

        Return:
            None
        """
        super().__init__(BANK_KIND)

    # Method to say whether these transactions can be audited
    def is_reconcilable(self):
        """
        Description:
        - OVERRIDE. Every bank transaction carries a reference, so the
          ledger can be matched against a statement.

        Input arguments:
           None

        Return:
            bool: True.
        """
        return True

    # Method to summarize the ledger for the menu
    def describe(self):
        """
        Description:
        - OVERRIDE. Says the ledger is traceable.

        Input arguments:
           None

        Return:
            str: e.g. 'Bank - 2 transactions, spent 9,567.00, received
                 62,061.00, traceable'.
        """
        return f"Bank - {self.format_totals()}, traceable"


class UnknownAccount(Account):
    """
    Description:
    - Transactions whose payment_mode was blank. 808 rows, ~5% of the
      dataset.

    Attributes:
        Inherited from Account. Adds none of its own.

    Methods:
        __init__: constructor.
        is_reconcilable: OVERRIDE. Returns False.
        describe: OVERRIDE. Names the gap.
    """

    # Constructor
    def __init__(self):
        """
        Description:
        - Constructor for the UnknownAccount class.
        - Takes no arguments and fixes the kind to 'unknown'.

        Input arguments:
           None

        Return:
            None
        """
        super().__init__(UNKNOWN_KIND)

    # Method to say whether these transactions can be audited
    def is_reconcilable(self):
        """
        Description:
        - OVERRIDE. Returns False for a different reason than CashAccount
          does. Cash cannot be reconciled because it leaves no trace;
          these cannot be reconciled because we do not know which
          statement to look in. Same answer, different cause, and
          describe is where that difference is stated.

        Input arguments:
           None

        Return:
            bool: False.
        """
        return False

    # Method to summarize the ledger for the menu
    def describe(self):
        """
        Description:
        - OVERRIDE. Names the gap rather than implying a payment method.

        Input arguments:
           None

        Return:
            str: e.g. 'Unrecorded - payment method not recorded in the
                 source data, 2 transactions, spent 3,888.00, received
                 13,239.00'.
        """
        return (f"Unrecorded - payment method not recorded in the source "
                f"data, {self.format_totals()}")
