import sys
import unittest
from pathlib import Path

# Add the project root so this file can also run as a standalone script.
PROJECT_ROOT = Path(__file__).resolve().parents[3] # change 3 based on file level
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Both class groups are needed: the Account classes under test, and the
# real Transaction classes they hold. Each dot is one level up:
#     ..   Accounts/
#     ...  the folder holding both groups
from budgetwise.models import (
    Account, CashAccount, BankAccount, UnknownAccount,
    CASH_KIND, BANK_KIND, UNKNOWN_KIND,
    ExpenseTransaction, IncomeTransaction,
)

# Default amounts for the two builders. Deliberately different, so a total
# that mixes the two directions is obvious in a failure message.
DEFAULT_EXPENSE_AMOUNT = 100.0
DEFAULT_INCOME_AMOUNT = 500.0


# Function to build one expense for a test
def make_expense(transaction_id="T1", amount=DEFAULT_EXPENSE_AMOUNT,
                 category="Food"):
    """
    Description:
    - Build one expense with sensible defaults, so a test can override
      just the field it is about.

    Input arguments:
       transaction_id (str): The row id.
       amount (float): The amount, without a sign.
       category (str): The category.

    Return:
        ExpenseTransaction: The built transaction.
    """
    return ExpenseTransaction(transaction_id, "U1", "2023-07-14",
                              category, amount, "Card")


# Function to build one income row for a test
def make_income(transaction_id="T2", amount=DEFAULT_INCOME_AMOUNT):
    """
    Description:
    - Build one income row with sensible defaults.

    Input arguments:
       transaction_id (str): The row id.
       amount (float): The amount, without a sign.

    Return:
        IncomeTransaction: The built transaction.
    """
    return IncomeTransaction(transaction_id, "U1", "2023-07-01",
                             "Salary", amount, "Bank Transfer")


class TestConstruction(unittest.TestCase):
    """
    Description:
    - Each subclass fixes its own kind and starts empty.
    """

    # Test that each subclass reports its own kind
    def test_each_subclass_fixes_its_kind(self):
        """
        Objective:
        - Check the kind is set by the subclass rather than passed in, so
          a cash ledger cannot be built calling itself a bank ledger.

        Expectation:
        - The three subclasses report 'cash', 'bank' and 'unknown'.
        """
        self.assertEqual(CashAccount().get_kind(), CASH_KIND)
        self.assertEqual(BankAccount().get_kind(), BANK_KIND)
        self.assertEqual(UnknownAccount().get_kind(), UNKNOWN_KIND)

    # Test that the subclass constructors take no arguments
    def test_the_subclasses_take_no_arguments(self):
        """
        Objective:
        - Check there is nothing left to configure. The owner and channel
          parameters were both dropped as carrying no information.

        Expectation:
        - All three build with no arguments and start empty.
        """
        for ledger_class in (CashAccount, BankAccount, UnknownAccount):
            self.assertEqual(ledger_class().get_transaction_count(), 0)

    # Test the base constructor directly
    def test_the_base_stores_whatever_kind_it_is_given(self):
        """
        Objective:
        - Check the base constructor works, since every subclass reaches
          it through super() and would break with it.

        Expectation:
        - It stores the kind it was given and starts with an empty list.
        """
        ledger = Account("anything")
        self.assertEqual(ledger.get_kind(), "anything")
        self.assertEqual(ledger.get_transactions(), [])

    # Test that the kind is coerced to str
    def test_the_kind_is_coerced_to_str(self):
        """
        Objective:
        - Check the kind is stored as text, so the formatting in
          describe() and __repr__ cannot fail on it.

        Expectation:
        - An integer kind of 123 reads back as '123'.
        """
        self.assertEqual(Account(123).get_kind(), "123")


class TestAddAndRead(unittest.TestCase):
    """
    Description:
    - add_transaction is the only way in. get_transactions is the only
      way out, and it hands back a copy.
    """

    # Set up one ledger used by every case in this class
    def setUp(self):
        """
        Description:
        - Build an empty bank ledger before each case, so transactions
          from one case do not leak into the next.
        """
        self.ledger = BankAccount()

    # Test that adding is counted
    def test_adding_raises_the_count(self):
        """
        Objective:
        - Check the one entry point works, since nothing else can put a
          transaction in a ledger.

        Expectation:
        - After one add, the count is 1.
        """
        self.ledger.add_transaction(make_expense())
        self.assertEqual(self.ledger.get_transaction_count(), 1)

    # Test that order is preserved
    def test_transactions_come_back_in_the_order_added(self):
        """
        Objective:
        - Check a ledger appends rather than reorders, so file order
          survives inside a ledger. It is only lost when the three
          ledgers are merged.

        Expectation:
        - Rows added as T1 then T2 come back in that order.
        """
        first, second = make_expense("T1"), make_expense("T2")
        self.ledger.add_transaction(first)
        self.ledger.add_transaction(second)
        self.assertEqual(
            [row.get_transaction_id()
             for row in self.ledger.get_transactions()],
            ["T1", "T2"])

    # Test that the same object comes back, not a copy of it
    def test_the_held_objects_are_the_same_objects(self):
        """
        Objective:
        - Check the ledger points at its transactions rather than owning
          or copying them. The pipeline's own list holds the same ones.

        Expectation:
        - The object that comes back is the same object that went in.
        """
        row = make_expense()
        self.ledger.add_transaction(row)
        self.assertIs(self.ledger.get_transactions()[0], row)

    # Test the copy semantics of the returned list
    def test_the_returned_list_is_a_copy(self):
        """
        Objective:
        - Check the ledger cannot be damaged through the list it hands
          out.

        Expectation:
        - Appending to and clearing the returned list leaves the ledger's
          own count at 1.
        """
        self.ledger.add_transaction(make_expense())
        borrowed = self.ledger.get_transactions()
        borrowed.append("junk")
        borrowed.clear()
        self.assertEqual(self.ledger.get_transaction_count(), 1)

    # Test an empty ledger
    def test_an_empty_ledger_reads_cleanly(self):
        """
        Objective:
        - Check an empty ledger is a normal state. A category filter can
          easily match nothing.

        Expectation:
        - The count is 0 and the list is empty, with nothing raised.
        """
        self.assertEqual(self.ledger.get_transaction_count(), 0)
        self.assertEqual(self.ledger.get_transactions(), [])


class TestTotals(unittest.TestCase):
    """
    Description:
    - Both totals pick rows by transaction type, not by the sign of the
      amount.
    """

    # Set up a ledger holding both directions
    def setUp(self):
        """
        Description:
        - One expense and one income, with different amounts so a total
          that mixed them would stand out in the failure message.
        """
        self.ledger = BankAccount()
        self.ledger.add_transaction(make_expense(amount=100.0))
        self.ledger.add_transaction(make_income(amount=500.0))

    # Test that spending ignores income
    def test_the_spending_total_counts_expenses_only(self):
        """
        Objective:
        - Check the spending total selects rows rather than summing
          everything, since a ledger holds both directions.

        Expectation:
        - A ledger with a 100 expense and a 500 income reports 100.0
          spent.
        """
        self.assertEqual(self.ledger.get_total_spent(), 100.0)

    # Test that income ignores spending
    def test_the_income_total_counts_income_only(self):
        """
        Objective:
        - Check the same the other way round.

        Expectation:
        - The same ledger reports 500.0 received.
        """
        self.assertEqual(self.ledger.get_total_received(), 500.0)

    # Test that several transactions accumulate
    def test_several_expenses_add_up(self):
        """
        Objective:
        - Check the total builds up across rows instead of returning the
          last one seen.

        Expectation:
        - Expenses of 100, 250 and 1,810 total 2,160.00.
        """
        ledger = CashAccount()
        for amount in (100.0, 250.0, 1810.0):
            ledger.add_transaction(make_expense(amount=amount))
        self.assertEqual(ledger.get_total_spent(), 2160.0)

    # Test an empty ledger totals zero
    def test_an_empty_ledger_totals_zero(self):
        """
        Objective:
        - Check the empty case, since the menu can print these figures
          before anything has been loaded.

        Expectation:
        - Both totals are 0, not None and not an error.
        """
        empty = CashAccount()
        self.assertEqual(empty.get_total_spent(), 0)
        self.assertEqual(empty.get_total_received(), 0)

    # Test a ledger holding only one direction
    def test_a_ledger_with_no_income_received_zero(self):
        """
        Objective:
        - Check the case where the selection matches nothing. A filtered
          run can easily produce a ledger of expenses only.

        Expectation:
        - A ledger with one expense reports 100.0 spent and 0 received.
        """
        ledger = CashAccount()
        ledger.add_transaction(make_expense())
        self.assertEqual(ledger.get_total_spent(), 100.0)
        self.assertEqual(ledger.get_total_received(), 0)


class TestFormatTotals(unittest.TestCase):
    """
    Description:
    - The shared phrase the three describe() overrides are built around.
    """

    # Test the formatted phrase
    def test_it_names_the_count_and_both_totals(self):
        """
        Objective:
        - Check the shared wording, which saves the three overrides from
          each repeating the same formatting.

        Expectation:
        - The phrase carries the count and both totals with separators
          and two decimals, since a person reads these figures.
        """
        ledger = BankAccount()
        ledger.add_transaction(make_expense(amount=9567.0))
        ledger.add_transaction(make_income(amount=62061.0))
        self.assertEqual(ledger.format_totals(),
                         "2 transactions, spent 9,567.00, received 62,061.00")

    # Test the empty case
    def test_an_empty_ledger_formats_as_zeros(self):
        """
        Objective:
        - Check it still reads properly before anything is loaded.

        Expectation:
        - An empty ledger formats as zero transactions and zero on both
          totals.
        """
        self.assertEqual(CashAccount().format_totals(),
                         "0 transactions, spent 0.00, received 0.00")

    # Test that it is inherited unchanged
    def test_all_three_subclasses_share_one_implementation(self):
        """
        Objective:
        - Check this one is inherited, not overridden. Counting and
          summing is the same job for all three ledgers, so an override
          would be three identical copies.

        Expectation:
        - All three resolve to the same function as the base class.
        """
        self.assertIs(CashAccount.format_totals, Account.format_totals)
        self.assertIs(BankAccount.format_totals, Account.format_totals)
        self.assertIs(UnknownAccount.format_totals, Account.format_totals)


class TestAbstractBase(unittest.TestCase):
    """
    Description:
    - The base refuses the two questions only a payment method can
      settle, rather than giving a misleading default.
    """

    # Test that reconcilability has no answer on the base
    def test_is_reconcilable_raises(self):
        """
        Objective:
        - Check there is no default answer. True would make the bank
          override pointless; False would have the base claim something
          about a ledger whose kind is not yet known.

        Expectation:
        - It raises NotImplementedError, and the message names the
          subclasses to use.
        """
        with self.assertRaises(NotImplementedError) as caught:
            Account("cash").is_reconcilable()
        self.assertIn("CashAccount", str(caught.exception))

    # Test that describe has no answer on the base
    def test_describe_raises(self):
        """
        Objective:
        - Check the same for the summary line. The base has nothing
          distinctive to say about itself.

        Expectation:
        - It raises NotImplementedError naming the payment method as the
          missing piece.
        """
        with self.assertRaises(NotImplementedError) as caught:
            Account("cash").describe()
        self.assertIn("payment method", str(caught.exception))

    # Test that the rest of the base still works
    def test_everything_else_on_the_base_still_works(self):
        """
        Objective:
        - Check that ONLY those two refuse. All three subclasses inherit
          the storage and totals, so they have to work here.

        Expectation:
        - The base holds a transaction, counts it, totals it and formats
          the shared phrase.
        """
        ledger = Account("cash")
        ledger.add_transaction(make_expense())
        self.assertEqual(ledger.get_transaction_count(), 1)
        self.assertEqual(ledger.get_total_spent(), 100.0)
        self.assertEqual(ledger.format_totals(),
                         "1 transactions, spent 100.00, received 0.00")


class TestSubclassOverrides(unittest.TestCase):
    """
    Description:
    - All three override the same two methods, and the bank ledger gives
      the opposite answer to the other two.
    """

    # Test that all three are Accounts
    def test_all_three_are_accounts(self):
        """
        Objective:
        - Check the is-a relationship, which is what lets the pipeline
          hold all three in one mapping.

        Expectation:
        - All three pass isinstance against Account.
        """
        for ledger in (CashAccount(), BankAccount(), UnknownAccount()):
            self.assertIsInstance(ledger, Account)

    # Test cash reconcilability
    def test_cash_cannot_be_reconciled(self):
        """
        Objective:
        - Check the cash answer. Cash carries no reference, so there is
          nothing to match against a statement.

        Expectation:
        - is_reconcilable() returns False.
        """
        self.assertFalse(CashAccount().is_reconcilable())

    # Test bank reconcilability
    def test_bank_can_be_reconciled(self):
        """
        Objective:
        - Check the override that goes the other way, which is what makes
          it a real override rather than decoration.

        Expectation:
        - is_reconcilable() returns True.
        """
        self.assertTrue(BankAccount().is_reconcilable())

    # Test unknown reconcilability
    def test_unrecorded_cannot_be_reconciled(self):
        """
        Objective:
        - Check the third answer. It matches cash, but for a different
          reason: cash leaves no trace, while here we do not know which
          statement to look in. describe() is where that is said.

        Expectation:
        - is_reconcilable() returns False.
        """
        self.assertFalse(UnknownAccount().is_reconcilable())

    # Test that each subclass really defines its own override
    def test_each_subclass_defines_its_own_overrides(self):
        """
        Objective:
        - Check the methods are genuinely overridden rather than
          inherited. An inherited one would raise.

        Expectation:
        - Both names appear in each subclass's own namespace.
        """
        for ledger_class in (CashAccount, BankAccount, UnknownAccount):
            self.assertIn("is_reconcilable", vars(ledger_class))
            self.assertIn("describe", vars(ledger_class))


class TestDescribe(unittest.TestCase):
    """
    Description:
    - Each ledger says what makes it different, so the menu can print a
      line without knowing which class it has.
    """

    # Test the cash wording
    def test_cash_names_its_limitation(self):
        """
        Objective:
        - Check the cash line tells the reader the figures cannot be
          verified.

        Expectation:
        - It carries the shared totals phrase, then the caveat.
        """
        ledger = CashAccount()
        ledger.add_transaction(make_expense(amount=4363.0))
        self.assertEqual(
            ledger.describe(),
            "Cash - 1 transactions, spent 4,363.00, received 0.00, "
            "no transaction reference, cannot be verified")

    # Test the bank wording
    def test_bank_says_it_is_traceable(self):
        """
        Objective:
        - Check the opposite claim in the same shape, so the two lines
          sit comparably in the menu.

        Expectation:
        - It carries the shared totals phrase, then 'traceable'.
        """
        ledger = BankAccount()
        ledger.add_transaction(make_income(amount=62061.0))
        self.assertEqual(
            ledger.describe(),
            "Bank - 1 transactions, spent 0.00, received 62,061.00, "
            "traceable")

    # Test the unrecorded wording
    def test_unrecorded_names_the_gap_before_the_money(self):
        """
        Objective:
        - Check the caveat comes first, so the figure cannot be quoted
          without it. This is a note about missing data, not a finding
          about how people pay.

        Expectation:
        - The line opens with the missing-payment-method wording, and the
          amount comes after it.
        """
        ledger = UnknownAccount()
        ledger.add_transaction(make_expense(amount=3888.0))
        described = ledger.describe()
        self.assertTrue(described.startswith(
            "Unrecorded - payment method not recorded in the source data"))
        self.assertIn("3,888.00", described)

    # Test that the three descriptions differ
    def test_the_three_descriptions_are_all_different(self):
        """
        Objective:
        - Check each override says something of its own. If two matched,
          one subclass would not be earning its override.

        Expectation:
        - The three lines are three distinct strings.
        """
        described = {CashAccount().describe(), BankAccount().describe(),
                     UnknownAccount().describe()}
        self.assertEqual(len(described), 3)


class TestRepr(unittest.TestCase):
    """
    Description:
    - The debugging form. What matters is that it is cheap and cannot
      raise.
    """

    # Test the formatted output
    def test_repr_names_the_class_kind_and_count(self):
        """
        Objective:
        - Check it carries enough to identify the ledger at a prompt.

        Expectation:
        - The string names the class, the kind and the count.
        """
        ledger = BankAccount()
        ledger.add_transaction(make_expense())
        self.assertEqual(repr(ledger), "BankAccount('bank', 1 transactions)")

    # Test that it does not read the totals
    def test_repr_does_not_walk_the_transactions(self):
        """
        Objective:
        - Check it stays away from the totals. Reading them would raise
          if one held object were malformed, and a __repr__ that raises
          breaks debuggers exactly when they are needed.

        Expectation:
        - A ledger holding a plain string still prints normally.
        """
        ledger = CashAccount()
        ledger.add_transaction("not a transaction")
        self.assertEqual(repr(ledger), "CashAccount('cash', 1 transactions)")

    # Test it on the base class
    def test_repr_works_on_the_base_class(self):
        """
        Objective:
        - Check the base can still be printed even though it cannot
          describe itself.

        Expectation:
        - It prints with its kind and a zero count.
        """
        self.assertEqual(repr(Account("cash")),
                         "Account('cash', 0 transactions)")


class TestEncapsulation(unittest.TestCase):
    """
    Description:
    - The two fields are private, and a subclass cannot reach them
      either.
    """

    # Test that the transaction list is not reachable by its plain name
    def test_the_transaction_list_is_not_reachable_directly(self):
        """
        Objective:
        - Check the ledger's storage really is private, so
          get_transactions is the only way to read it.

        Expectation:
        - Reading __transactions on the object raises AttributeError,
          because Python has renamed it.
        """
        with self.assertRaises(AttributeError):
            BankAccount().__transactions

    # Test that the storage is mangled under the base class name
    def test_the_storage_is_mangled_to_the_base_class(self):
        """
        Objective:
        - Check both fields belong to Account rather than to the
          subclass, which is why a subclass reads them through the
          inherited methods.

        Expectation:
        - They are reachable only as _Account__transactions and
          _Account__kind.
        """
        ledger = BankAccount()
        ledger.add_transaction(make_expense())
        self.assertEqual(len(ledger._Account__transactions), 1)
        self.assertEqual(ledger._Account__kind, "bank")

    # Test that a subclass cannot reach the private list
    def test_a_subclass_cannot_reach_the_private_list(self):
        """
        Objective:
        - Check even a subclass cannot swap out the ledger's contents,
          which is the point of private rather than protected.

        Expectation:
        - A subclass writing self.__transactions creates its own new
          attribute; the ledger still holds its one real transaction.
        """
        class SneakyBank(BankAccount):
            def cheat(self):
                self.__transactions = ["junk", "junk"]

        ledger = SneakyBank()
        ledger.add_transaction(make_expense())
        ledger.cheat()
        self.assertEqual(ledger.get_transaction_count(), 1)

    # Test that there is no setter for the kind
    def test_there_is_no_setter_for_the_kind(self):
        """
        Objective:
        - Check the kind cannot change after the ledger is built, so it
          cannot start reporting itself differently mid-run.

        Expectation:
        - Assigning ledger.kind creates an unrelated public attribute;
          get_kind() still returns 'cash'.
        """
        ledger = CashAccount()
        ledger.kind = "bank"
        self.assertEqual(ledger.get_kind(), "cash")


if __name__ == "__main__":
    unittest.main(verbosity=2)
