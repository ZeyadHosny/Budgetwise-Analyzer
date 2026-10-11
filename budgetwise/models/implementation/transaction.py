# The two values transaction_type can take.
EXPENSE_TYPE = "Expense"
INCOME_TYPE = "Income"

# Expense categories the team agreed can be cut.
DISCRETIONARY_CATEGORIES = ("Food", "Travel", "Entertainment")
# Expense categories the team agreed cannot be cut.
ESSENTIAL_CATEGORIES = ("Rent", "Utilities", "Education", "Health")
# Expense categories that are neither.
UNCLASSIFIED_CATEGORIES = ("Savings", "Others", "Uncategorized")

# Income categories that are worked for.
EARNED_INCOME_CATEGORIES = ("Salary", "Bonus", "Freelance")
# Income categories that are returns on capital.
PASSIVE_INCOME_CATEGORIES = ("Investment",)

# Label used when a row carried no currency symbol.
DEFAULT_CURRENCY_LABEL = "plain"
# Label used when a row carried no payment mode. 808 rows in the dataset.
DEFAULT_PAYMENT_MODE = ""
# Smallest amount allowed.
MINIMUM_AMOUNT = 0.0
# How many characters a YYYY-MM-DD date has. Used to reject other formats
# before get_month slices them.
DATE_LENGTH = 10
# Position of the year inside a YYYY-MM-DD date string.
YEAR_SLICE = slice(0, 4)
# Position of the month inside a YYYY-MM-DD date string.
MONTH_SLICE = slice(5, 7)
# Where the two hyphens sit in a YYYY-MM-DD date string.
FIRST_HYPHEN_POSITION = 4
SECOND_HYPHEN_POSITION = 7


class Transaction:
    """
    Description:
    - One cleaned transaction from the BudgetWise dataset. One object per
      cleaned CSV row.
    - Base class for ExpenseTransaction and IncomeTransaction. Never
      instantiated directly: get_transaction_type and get_signed_amount
      have no answer until a subclass supplies one.
    - Every attribute is private and read through a getter, including from
      the subclasses.

    Attributes:
        __transaction_id (str): PRIVATE. The row id, e.g. 'T1044'.
        __user_id (str): PRIVATE. The account holder id, e.g. 'U075'.
        __date (str): PRIVATE. 'YYYY-MM-DD', or None when the row had no
            date. 486 rows have none.
        __category (str): PRIVATE. Transaction category.
        __amount (float): PRIVATE. The unsigned magnitude.
        __payment_mode (str): PRIVATE. Payment method.
        __original_currency (str): PRIVATE. The symbol the row carried.

    Methods:
        __init__: constructor.
        get_transaction_id, get_user_id, get_date, get_category,
            get_amount, get_payment_mode, get_original_currency: the only
            way to read each attribute.
        set_amount: the one setter.
        has_date: whether a usable date is present.
        get_month: the (year, month) tuple key.
        get_transaction_type: ABSTRACT. 'Expense' or 'Income'.
        get_signed_amount: ABSTRACT. The magnitude with direction applied.
        to_dict: the transaction as a dictionary.
    """

    # Constructor
    def __init__(self, transaction_id, user_id, date, category, amount,
                 payment_mode=DEFAULT_PAYMENT_MODE,
                 original_currency=DEFAULT_CURRENCY_LABEL):
        """
        Description:
        - Constructor for the Transaction class.
        - Receives cleaned values of the transaction.
        - The amount is assigned through set_amount, so an object can
          never exist in a state the setter would have refused.

        Input arguments:
           transaction_id (str): The row id, e.g. 'T1044'.
           user_id (str): The account holder id, e.g. 'U075'.
           date (str): 'YYYY-MM-DD', or None if the row had no date.
           category (str): The normalized category, e.g. 'Food'.
           amount (float): The unsigned magnitude, e.g. 1810.0.
           payment_mode (str): The normalized mode, e.g. 'Card'.
           original_currency (str): The symbol the row carried.

        Return:
            None (raises ValueError if the amount is unusable)
        """
        self.__transaction_id = str(transaction_id)
        self.__user_id = str(user_id)
        self.__date = date
        self.__category = str(category)
        self.__payment_mode = str(payment_mode)
        self.__original_currency = str(original_currency)
        self.__amount = MINIMUM_AMOUNT
        self.set_amount(amount)

    # Method to read the private row id
    def get_transaction_id(self):
        """
        Description:
        - Return the transaction id.

        Input arguments:
           None

        Return:
            str: e.g. 'T1044'.
        """
        return self.__transaction_id

    # Method to read the private user id
    def get_user_id(self):
        """
        Description:
        - Return the account holder id.

        Input arguments:
           None

        Return:
            str: e.g. 'U075'.
        """
        return self.__user_id

    # Method to read the private date
    def get_date(self):
        """
        Description:
        - Return the cleaned date, or None when the row had no date.

        Input arguments:
           None

        Return:
            str: 'YYYY-MM-DD', or None.
        """
        return self.__date

    # Method to read the private category
    def get_category(self):
        """
        Description:
        - Return the normalized category.

        Input arguments:
           None

        Return:
            str: e.g. 'Food'.
        """
        return self.__category

    # Method to read the private amount
    def get_amount(self):
        """
        Description:
        - Return the unsigned magnitude.

        Input arguments:
           None

        Return:
            float: e.g. 1810.0.
        """
        return self.__amount

    # Method to read the private payment mode
    def get_payment_mode(self):
        """
        Description:
        - Return the normalized payment mode.

        Input arguments:
           None

        Return:
            str: 'Cash', 'Card', 'UPI', 'Bank Transfer', or '' when the
             row is blank.
        """
        return self.__payment_mode

    # Method to read the private original currency
    def get_original_currency(self):
        """
        Description:
        - Return the symbol this transaction originally carried.

        Input arguments:
           None

        Return:
            str: e.g. a rupee sign, or 'plain' when there was none.
        """
        return self.__original_currency

    # Method to store the amount
    def set_amount(self, value):
        """
        Description:
        - Store the amount, refusing anything negative, missing or
          unparseable.

        Input arguments:
           value (float): The amount to store. Must be zero or greater.

        Return:
            None (raises ValueError when the value is unusable)
        """
        if value is None:
            raise ValueError("amount must not be None")
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"amount must be numeric, got {value!r}") from None
        if value < MINIMUM_AMOUNT:
            raise ValueError(
                f"amount must be an unsigned magnitude, got {value!r}")
        self.__amount = value

    # Method saying whether this row can take part in date analysis
    def has_date(self):
        """
        Description:
        - Say whether this transaction carries a usable date.

        Input arguments:
           None

        Return:
            bool: True when a usable YYYY-MM-DD date is present.
        """
        if self.__date is None:
            return False
        if len(self.__date) != DATE_LENGTH:
            return False
        if self.__date[FIRST_HYPHEN_POSITION] != "-":
            return False
        if self.__date[SECOND_HYPHEN_POSITION] != "-":
            return False
        return True

    # Method returning the tuple key section 4.2 asks for
    def get_month(self):
        """
        Description:
        - Return the (year, month) pair used to group transactions.

        Input arguments:
           None

        Return:
            tuple: ('2021', '05'), or None when there is no usable date.
        """
        if not self.has_date():
            return None
        return (self.__date[YEAR_SLICE], self.__date[MONTH_SLICE])

    # Method naming the kind of transaction
    def get_transaction_type(self):
        """
        Description:
        - ABSTRACT. Name the kind of transaction.
        - Raises rather than returning 'Unknown'.

        Input arguments:
           None

        Return:
            Never returns (always raises NotImplementedError)
        """
        raise NotImplementedError(
            "transaction_type comes from the subclass"
            "Build an ExpenseTransaction or an IncomeTransaction.")

    # Method returning the amount with its direction applied
    def get_signed_amount(self):
        """
        Description:
        - ABSTRACT. Return the magnitude with direction applied.
        - Raises rather than returning the unsigned magnitude.

        Input arguments:
           None

        Return:
            Never returns (always raises NotImplementedError)
        """
        raise NotImplementedError(
            "direction comes from transaction_type"
            "Build an ExpenseTransaction or an IncomeTransaction.")

    # Method to export one row
    def to_dict(self):
        """
        Description:
        - Return this transaction as one row of the cleaned CSV transaction.

        Input arguments:
           None

        Return:
            dict: The eight exported fields.
        """
        return {
            "transaction_id": self.__transaction_id,
            "user_id": self.__user_id,
            "date": self.__date,
            "transaction_type": self.get_transaction_type(),
            "category": self.__category,
            "amount": self.__amount,
            "payment_mode": self.__payment_mode,
            "original_currency": self.__original_currency,
        }

    # Method to show the object during debugging
    def __repr__(self):
        """
        Description:
        - Return a short identifying form of this transaction.

        Input arguments:
           None

        Return:
            str: e.g. "ExpenseTransaction('T1044', 'Food', 1,810.00)".
        """
        return (f"{type(self).__name__}({self.__transaction_id!r}, "
                f"{self.__category!r}, {self.__amount:,.2f})")


class ExpenseTransaction(Transaction):
    """
    Description:
    - Money going out. 13,517 rows, 85% of the dataset.
    - Overrides the two abstract methods and adds one of its own.
    - Reads its parent's state through the inherited getters.

    Attributes:
        Inherited from Transaction. Adds none of its own.

    Methods:
        get_transaction_type: OVERRIDE. Returns 'Expense'.
        get_signed_amount: OVERRIDE. Returns the magnitude as negative.
        is_discretionary: EXTENSION, expenses only.
    """

    # Method naming the kind of transaction
    def get_transaction_type(self):
        """
        Description:
        - OVERRIDE. This is an expense.

        Input arguments:
           None

        Return:
            str: 'Expense'.
        """
        return EXPENSE_TYPE

    # Method returning the amount with its direction applied
    def get_signed_amount(self):
        """
        Description:
        - OVERRIDE. An expense reduces the balance, so it is negative.
        - The sign comes from the class, which was chosen from
          transaction_type at construction. That is section 4.5's rule:
          direction from the type, never from the sign of the raw amount.

        Input arguments:
           None

        Return:
            float: The negative magnitude. 1,810 returns -1810.0.
        """
        return -self.get_amount()

    # Method to say whether this spending could be cut
    def is_discretionary(self):
        """
        Description:
        - EXTENSION, expenses only. Say whether this spending could be
          cut. Income is never discretionary, which is why this method is
          not on the base class.

        Input arguments:
           None

        Return:
            bool: True only for a discretionary category.
        """
        return self.get_category() in DISCRETIONARY_CATEGORIES


class IncomeTransaction(Transaction):
    """
    Description:
    - Money coming in. 2,383 rows, 15% of the dataset.
    - Overrides the two abstract methods and adds two of its own.

    Attributes:
        Inherited from Transaction. Adds none of its own.

    Methods:
        get_transaction_type: OVERRIDE. Returns 'Income'.
        get_signed_amount: OVERRIDE. Returns the magnitude as positive.
        is_earned: EXTENSION, income only. Whether it was worked for.
        get_source_type: EXTENSION, income only. Classifies the source.
    """

    # Method naming the kind of transaction
    def get_transaction_type(self):
        """
        Description:
        - OVERRIDE. This is income.

        Input arguments:
           None

        Return:
            str: 'Income'.
        """
        return INCOME_TYPE

    # Method returning the amount with its direction applied
    def get_signed_amount(self):
        """
        Description:
        - OVERRIDE. Income increases the balance, so it is positive.

        Input arguments:
           None

        Return:
            float: The positive magnitude. 62,061 returns 62061.0.
        """
        return self.get_amount()

    # Method to say whether this income was worked for
    def is_earned(self):
        """
        Description:
        - EXTENSION, income only. Say whether this income was worked for
          rather than earned on capital.
        - Salary, Bonus and Freelance are worked for; Investment is not.

        Input arguments:
           None

        Return:
            bool: True for an earned category.
        """
        return self.get_category() in EARNED_INCOME_CATEGORIES

    # Method to classify the income source
    def get_source_type(self):
        """
        Description:
        - EXTENSION, income only. Classify where this income came from.

        Input arguments:
           None

        Return:
            str: 'earned', 'passive', or 'other'.
                 T9824 Salary returns 'earned'.
                 T2849 Investment returns 'passive'.
        """
        category = self.get_category()
        if category in EARNED_INCOME_CATEGORIES:
            return "earned"
        if category in PASSIVE_INCOME_CATEGORIES:
            return "passive"
        return "other"
