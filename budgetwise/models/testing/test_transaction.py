import sys
import unittest
from pathlib import Path

# Add the project root so this file can also run as a standalone script.
PROJECT_ROOT = Path(__file__).resolve().parents[3] # change 3 based on file level
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from budgetwise.models import (
    Transaction, ExpenseTransaction, IncomeTransaction,
    EXPENSE_TYPE, INCOME_TYPE,
    DISCRETIONARY_CATEGORIES, ESSENTIAL_CATEGORIES,
    UNCLASSIFIED_CATEGORIES, EARNED_INCOME_CATEGORIES,
    PASSIVE_INCOME_CATEGORIES,
)

# A real expense row: T1044, Food, 1,810 on a card, originally in rupees.
EXPENSE_ROW = ("T1044", "U075", "2021-05-06", "Food", 1810.0, "Card", "₹")
# A real income row: T9824, Salary, 62,061 by bank transfer.
INCOME_ROW = ("T9824", "U061", "2024-12-12", "Salary", 62061.0,
              "Bank Transfer", "plain")
# A real row with a blank date. 486 rows have none.
UNDATED_ROW = ("T12350", "U097", None, "Food", 6299.0, "", "plain")
# The field order the constructor takes, used by the two builders below.
FIELD_ORDER = ("transaction_id", "user_id", "date", "category", "amount",
               "payment_mode", "original_currency")


# Function to build one expense with sensible defaults
def make_expense(**overrides):
    """
    Description:
    - Build an expense from the real T1044 row, letting a test override
      only the field it is about.

    Input arguments:
       overrides (dict): any of the seven constructor fields.

    Return:
        ExpenseTransaction: The built transaction.
    """
    fields = dict(zip(FIELD_ORDER, EXPENSE_ROW))
    fields.update(overrides)
    return ExpenseTransaction(**fields)


# Function to build one income row with sensible defaults
def make_income(**overrides):
    """
    Description:
    - Build an income row from the real T9824 row.

    Input arguments:
       overrides (dict): any of the seven constructor fields.

    Return:
        IncomeTransaction: The built transaction.
    """
    fields = dict(zip(FIELD_ORDER, INCOME_ROW))
    fields.update(overrides)
    return IncomeTransaction(**fields)


class TestConstruction(unittest.TestCase):
    """
    Description:
    - What the constructor accepts, and the tidying it applies.
    """

    # Test that every field reads back through its getter
    def test_all_seven_fields_read_back(self):
        """
        Objective:
        - Check the seven getters work, since they are the only way to
          read the seven private fields.

        Expectation:
        - Each one returns what the constructor was given, unchanged.
        """
        row = make_expense()
        self.assertEqual(row.get_transaction_id(), "T1044")
        self.assertEqual(row.get_user_id(), "U075")
        self.assertEqual(row.get_date(), "2021-05-06")
        self.assertEqual(row.get_category(), "Food")
        self.assertEqual(row.get_amount(), 1810.0)
        self.assertEqual(row.get_payment_mode(), "Card")
        self.assertEqual(row.get_original_currency(), "₹")

    # Test the two default arguments
    def test_payment_mode_and_currency_default(self):
        """
        Objective:
        - Check a row can be built when the payment mode and currency are
          unknown. 808 rows have no payment mode.

        Expectation:
        - The mode comes out empty and the currency reads 'plain', rather
          than raising or storing None.
        """
        row = ExpenseTransaction("T1", "U1", "2023-01-01", "Food", 100.0)
        self.assertEqual(row.get_payment_mode(), "")
        self.assertEqual(row.get_original_currency(), "plain")

    # Test that text fields are coerced to str
    def test_text_fields_are_coerced(self):
        """
        Objective:
        - Check the identifiers are stored as text, so a number from the
          loader cannot break string formatting later.

        Expectation:
        - The integers 1044 and 75 read back as '1044' and '75'.
        """
        row = ExpenseTransaction(1044, 75, "2023-01-01", "Food", 100.0)
        self.assertEqual(row.get_transaction_id(), "1044")
        self.assertEqual(row.get_user_id(), "75")

    # Test that an int amount becomes a float
    def test_amount_is_coerced_to_float(self):
        """
        Objective:
        - Check the amount is always one numeric type, so arithmetic and
          currency formatting behave the same on every row.

        Expectation:
        - An int amount of 1810 is stored as a float.
        """
        row = make_expense(amount=1810)
        self.assertIsInstance(row.get_amount(), float)

    # Test that the constructor refuses what the setter refuses
    def test_constructor_rejects_a_negative_amount(self):
        """
        Objective:
        - Check the constructor goes through set_amount rather than
          writing the field directly, so a bad object cannot exist.

        Expectation:
        - Building with -5.0 raises ValueError and returns no object.
        """
        with self.assertRaises(ValueError):
            make_expense(amount=-5.0)


class TestSetAmount(unittest.TestCase):
    """
    Description:
    - The one setter in the class, and every way it can refuse a value.
    """

    # Set up one expense used by every case in this class
    def setUp(self):
        """
        Description:
        - Build T1044 fresh before each case, so a changed amount cannot
          leak into the next test.
        """
        self.row = make_expense()

    # Test the success branch
    def test_a_valid_amount_is_stored(self):
        """
        Objective:
        - Check the setter guards the value without making it read-only,
          since a correction must still be possible.

        Expectation:
        - After set_amount(2500) the getter returns 2500.0.
        """
        self.row.set_amount(2500)
        self.assertEqual(self.row.get_amount(), 2500.0)

    # Test the boundary
    def test_zero_is_allowed(self):
        """
        Objective:
        - Check the exact boundary. The rule is "no negatives", not
          "must be positive".

        Expectation:
        - set_amount(0) is accepted and stores 0.0.
        """
        self.row.set_amount(0)
        self.assertEqual(self.row.get_amount(), 0.0)

    # Test the None branch
    def test_none_is_refused(self):
        """
        Objective:
        - Check a missing amount cannot be stored. 291 rows have a blank
          amount; the pipeline skips those, so None must never arrive.

        Expectation:
        - set_amount(None) raises ValueError, and the message says None.
        """
        with self.assertRaises(ValueError) as caught:
            self.row.set_amount(None)
        self.assertIn("None", str(caught.exception))

    # Test the non-numeric branch
    def test_text_is_refused(self):
        """
        Objective:
        - Check text that slipped past the amount parser cannot be
          stored, or every later total would break somewhere else.

        Expectation:
        - set_amount("abc") raises ValueError saying the value must be
          numeric.
        """
        with self.assertRaises(ValueError) as caught:
            self.row.set_amount("abc")
        self.assertIn("numeric", str(caught.exception))

    # Test the non-numeric branch with a non-string
    def test_an_unconvertible_object_is_refused(self):
        """
        Objective:
        - Check both ways float() can fail are caught. A string raises
          ValueError, a list raises TypeError.

        Expectation:
        - set_amount([1, 2, 3]) raises ValueError, not TypeError.
        """
        with self.assertRaises(ValueError):
            self.row.set_amount([1, 2, 3])

    # Test the negative branch
    def test_a_negative_is_refused(self):
        """
        Objective:
        - Check the main rule: amounts are stored without a sign. The raw
          file holds 153 negative amounts, and cleaning strips them, so a
          negative here means a cleaning step was missed.

        Expectation:
        - set_amount(-1000) raises ValueError saying the amount must be
          unsigned.
        """
        with self.assertRaises(ValueError) as caught:
            self.row.set_amount(-1000)
        self.assertIn("unsigned", str(caught.exception))

    # Test that a refused value leaves the old one intact
    def test_a_refused_value_does_not_change_the_amount(self):
        """
        Objective:
        - Check the value is validated before it is stored, so a rejected
          call cannot leave the object half-changed.

        Expectation:
        - After a refused set_amount(-1), the amount is still 1810.0.
        """
        with self.assertRaises(ValueError):
            self.row.set_amount(-1)
        self.assertEqual(self.row.get_amount(), 1810.0)


class TestDates(unittest.TestCase):
    """
    Description:
    - The month key used for grouping, and the rows that cannot produce
      one.
    """

    # Test a well-formed date
    def test_a_standard_date_is_usable(self):
        """
        Objective:
        - Check a normal YYYY-MM-DD date gives a grouping key.

        Expectation:
        - has_date() is True and get_month() is ('2021', '05').
        """
        row = make_expense()
        self.assertTrue(row.has_date())
        self.assertEqual(row.get_month(), ("2021", "05"))

    # Test that the month key is a tuple
    def test_the_month_key_is_a_tuple(self):
        """
        Objective:
        - Check the key type. The analysis groups on it, so a string
          would quietly change how grouping behaves.

        Expectation:
        - get_month() returns a tuple, not a string or a list.
        """
        self.assertIsInstance(make_expense().get_month(), tuple)

    # Test the None branch of has_date
    def test_a_missing_date_is_not_usable(self):
        """
        Objective:
        - Check a dateless row is kept but left out of date grouping.
          486 rows have no date.

        Expectation:
        - has_date() is False and get_month() is None, so date filters
          skip the row instead of failing on it.
        """
        row = ExpenseTransaction(*UNDATED_ROW)
        self.assertFalse(row.has_date())
        self.assertIsNone(row.get_month())

    # Test the wrong-length branch of has_date
    def test_a_short_date_is_not_usable(self):
        """
        Objective:
        - Catch a date written without zero padding. '2021-5-6' would
          slice to ('2021', '5-').

        Expectation:
        - has_date() is False and get_month() is None.
        """
        row = make_expense(date="2021-5-6")
        self.assertFalse(row.has_date())
        self.assertIsNone(row.get_month())

    # Test the first-hyphen branch of has_date
    def test_a_day_first_date_is_not_usable(self):
        """
        Objective:
        - Catch a date with the right length but the wrong layout, which
          a length check alone would miss. '17-07-2024' slices to
          ('17-0', '-2') - a key that looks real and is not. 953 rows in
          the raw file use this format.

        Expectation:
        - has_date() is False and get_month() is None.
        """
        row = make_expense(date="17-07-2024")
        self.assertFalse(row.has_date())
        self.assertIsNone(row.get_month())

    # Test the second-hyphen branch of has_date
    def test_a_slash_separated_date_is_not_usable(self):
        """
        Objective:
        - Check both separators are tested. '2021/05/06' fails on the
          first, '2021-05/06' only on the second.

        Expectation:
        - has_date() is False for both.
        """
        self.assertFalse(make_expense(date="2021/05/06").has_date())
        self.assertFalse(make_expense(date="2021-05/06").has_date())

    # Test that an unusable date does not cost the row its amount
    def test_an_undated_row_still_carries_its_amount(self):
        """
        Objective:
        - Check that rejecting the date does not reject the row. It still
          belongs in its category total.

        Expectation:
        - T12350 still reports 6,299.00 and the category Food.
        """
        row = ExpenseTransaction(*UNDATED_ROW)
        self.assertEqual(row.get_amount(), 6299.0)
        self.assertEqual(row.get_category(), "Food")


class TestAbstractBase(unittest.TestCase):
    """
    Description:
    - The base class refuses anything that depends on direction, rather
      than guessing at it.
    """

    # Test that the type has no answer on the base
    def test_get_transaction_type_raises(self):
        """
        Objective:
        - Check the base cannot name a transaction type. The type belongs
          to the subclass; storing it would let an object contradict its
          own class.

        Expectation:
        - It raises NotImplementedError, and the message says to use a
          subclass.
        """
        row = Transaction("T999", "U001", "2023-07-14", "Food", 5000.0)
        with self.assertRaises(NotImplementedError) as caught:
            row.get_transaction_type()
        self.assertIn("subclass", str(caught.exception))

    # Test that the direction has no answer on the base
    def test_get_signed_amount_raises(self):
        """
        Objective:
        - Check the base refuses to guess a direction. Returning the
          plain amount here would quietly count the row as income.

        Expectation:
        - It raises NotImplementedError rather than returning a number.
        """
        row = Transaction("T999", "U001", "2023-07-14", "Food", 5000.0)
        with self.assertRaises(NotImplementedError):
            row.get_signed_amount()

    # Test that the export fails on the base too
    def test_to_dict_raises_on_the_base(self):
        """
        Objective:
        - Check the refusal carries through to the export. A row with no
          direction has no business in the cleaned file.

        Expectation:
        - to_dict() raises NotImplementedError.
        """
        row = Transaction("T999", "U001", "2023-07-14", "Food", 5000.0)
        with self.assertRaises(NotImplementedError):
            row.to_dict()

    # Test that the base still builds and reads
    def test_the_base_still_stores_and_reads_its_fields(self):
        """
        Objective:
        - Check that ONLY the direction methods refuse. The storage is
          inherited by both subclasses, so it has to work here.

        Expectation:
        - The base returns its id and amount normally.
        """
        row = Transaction("T999", "U001", "2023-07-14", "Food", 5000.0)
        self.assertEqual(row.get_transaction_id(), "T999")
        self.assertEqual(row.get_amount(), 5000.0)


class TestInheritance(unittest.TestCase):
    """
    Description:
    - The is-a relationship between the base and its two subclasses.
    """

    # Test that an expense is a Transaction
    def test_an_expense_is_a_transaction(self):
        """
        Objective:
        - Check the relationship holds, since it is what lets the
          analysis keep both kinds in one list.

        Expectation:
        - An expense passes isinstance against Transaction.
        """
        self.assertIsInstance(make_expense(), Transaction)

    # Test that income is a Transaction
    def test_income_is_a_transaction(self):
        """
        Objective:
        - Check the same for the other subclass.

        Expectation:
        - An income row passes isinstance against Transaction.
        """
        self.assertIsInstance(make_income(), Transaction)

    # Test that the two subclasses are distinct
    def test_the_two_subclasses_are_different(self):
        """
        Objective:
        - Check the hierarchy really has two branches. If they were one,
          the direction rule would have nothing to dispatch on.

        Expectation:
        - The two classes are different objects.
        """
        self.assertIsNot(ExpenseTransaction, IncomeTransaction)

    # Test that each subclass inherits the base getters
    def test_the_subclasses_inherit_the_getters(self):
        """
        Objective:
        - Check the subclasses add no storage of their own, so every
          field they expose comes from the base.

        Expectation:
        - Both expose get_amount and has_date without redefining them.
        """
        for row in (make_expense(), make_income()):
            self.assertTrue(callable(row.get_amount))
            self.assertTrue(callable(row.has_date))


class TestDirection(unittest.TestCase):
    """
    Description:
    - Direction comes from the transaction type, never from the sign of
      the stored amount.
    """

    # Test the expense type label
    def test_an_expense_reports_its_type(self):
        """
        Objective:
        - Check the label the ledger totals match on. A mismatch would
          make every expense total silently read zero.

        Expectation:
        - get_transaction_type() returns the shared EXPENSE_TYPE value.
        """
        self.assertEqual(make_expense().get_transaction_type(), EXPENSE_TYPE)

    # Test the income type label
    def test_income_reports_its_type(self):
        """
        Objective:
        - Check the same on the income side.

        Expectation:
        - get_transaction_type() returns the shared INCOME_TYPE value.
        """
        self.assertEqual(make_income().get_transaction_type(), INCOME_TYPE)

    # Test that an expense is negative
    def test_an_expense_is_negative(self):
        """
        Objective:
        - Check the override that gives the inheritance its purpose: an
          expense takes money out.

        Expectation:
        - A stored 1,810 gives a signed amount of -1810.0.
        """
        self.assertEqual(make_expense().get_signed_amount(), -1810.0)

    # Test that income is positive
    def test_income_is_positive(self):
        """
        Objective:
        - Check the opposite override.

        Expectation:
        - A stored 62,061 gives a signed amount of +62061.0.
        """
        self.assertEqual(make_income().get_signed_amount(), 62061.0)

    # Test that the stored magnitude is left alone
    def test_the_stored_magnitude_is_unchanged(self):
        """
        Objective:
        - Check applying direction is a calculation, not a change to the
          stored value. The export needs the plain magnitude.

        Expectation:
        - After get_signed_amount(), get_amount() is still 1810.0.
        """
        row = make_expense()
        row.get_signed_amount()
        self.assertEqual(row.get_amount(), 1810.0)

    # Test that the same magnitude gives opposite signs
    def test_the_same_amount_gives_opposite_signs(self):
        """
        Objective:
        - Show plainly what the inheritance buys: same input, opposite
          output, decided by the class alone.

        Expectation:
        - Two rows holding 1,810 give signed amounts that negate each
          other.
        """
        expense = make_expense(amount=1810.0)
        income = make_income(amount=1810.0)
        self.assertEqual(expense.get_signed_amount(),
                         -income.get_signed_amount())


class TestExpenseOnly(unittest.TestCase):
    """
    Description:
    - Behaviour that belongs to expenses alone.
    """

    # Test every discretionary category
    def test_every_discretionary_category_is_true(self):
        """
        Objective:
        - Check every category the team agreed can be cut. Looping the
          constant means a category added later is covered for free.

        Expectation:
        - Food, Travel and Entertainment each return True.
        """
        for category in DISCRETIONARY_CATEGORIES:
            self.assertTrue(make_expense(category=category).is_discretionary(),
                            f"{category} should be discretionary")

    # Test every essential category
    def test_every_essential_category_is_false(self):
        """
        Objective:
        - Check essential spending is never suggested for cutting. A
          recommendation to cut rent would discredit the report.

        Expectation:
        - Rent, Utilities, Education and Health each return False.
        """
        for category in ESSENTIAL_CATEGORIES:
            self.assertFalse(make_expense(category=category).is_discretionary(),
                             f"{category} should not be discretionary")

    # Test every unclassified category
    def test_every_unclassified_category_is_false(self):
        """
        Objective:
        - Check the three unclassified categories answer False on
          purpose, not by accident. You cannot suggest cutting spending
          you cannot identify.

        Expectation:
        - Savings, Others and Uncategorized each return False. That means
          "do not suggest cutting this", not "this is essential" - the
          report wording has to keep them apart.
        """
        for category in UNCLASSIFIED_CATEGORIES:
            self.assertFalse(make_expense(category=category).is_discretionary(),
                             f"{category} should not be discretionary")

    # Test that the three tuples do not overlap
    def test_the_three_category_groups_do_not_overlap(self):
        """
        Objective:
        - Check the three category lists do not share a name. One listed
          twice would make the answer depend on check order.

        Expectation:
        - The three lists together hold as many distinct names as their
          lengths add up to.
        """
        groups = (set(DISCRETIONARY_CATEGORIES), set(ESSENTIAL_CATEGORIES),
                  set(UNCLASSIFIED_CATEGORIES))
        self.assertEqual(sum(len(group) for group in groups),
                         len(set().union(*groups)))

    # Test that income does not inherit the expense method
    def test_income_has_no_is_discretionary(self):
        """
        Objective:
        - Check the method belongs to the expense subclass only. The
          question is meaningless for income.

        Expectation:
        - It is absent from an income row, not merely returning False.
        """
        self.assertFalse(hasattr(make_income(), "is_discretionary"))


class TestIncomeOnly(unittest.TestCase):
    """
    Description:
    - Behaviour that belongs to income alone: worked for, or earned on
      capital.
    """

    # Test every earned category
    def test_every_earned_category_is_earned(self):
        """
        Objective:
        - Check the first case: money that was worked for.

        Expectation:
        - Salary, Bonus and Freelance each report is_earned() True and a
          source of 'earned'.
        """
        for category in EARNED_INCOME_CATEGORIES:
            row = make_income(category=category)
            self.assertTrue(row.is_earned(), f"{category} should be earned")
            self.assertEqual(row.get_source_type(), "earned")

    # Test every passive category
    def test_every_passive_category_is_passive(self):
        """
        Objective:
        - Check the second case: a return on capital. This is what makes
          the two methods worth having at all.

        Expectation:
        - Investment reports is_earned() False and a source of 'passive'.
        """
        for category in PASSIVE_INCOME_CATEGORIES:
            row = make_income(category=category)
            self.assertFalse(row.is_earned(), f"{category} is not earned")
            self.assertEqual(row.get_source_type(), "passive")

    # Test the third branch of get_source_type
    def test_an_unlisted_category_is_other(self):
        """
        Objective:
        - Check the fall-through case, which real data reaches: 285 rows
          have a blank category and become 'Uncategorized'.

        Expectation:
        - An income row in neither list reports is_earned() False and a
          source of 'other'.
        """
        row = make_income(category="Uncategorized")
        self.assertFalse(row.is_earned())
        self.assertEqual(row.get_source_type(), "other")

    # Test that an expense does not inherit the income methods
    def test_an_expense_has_no_income_methods(self):
        """
        Objective:
        - Check both methods belong to the income subclass only. Neither
          question applies to an expense.

        Expectation:
        - is_earned and get_source_type are both absent from an expense.
        """
        expense = make_expense()
        self.assertFalse(hasattr(expense, "is_earned"))
        self.assertFalse(hasattr(expense, "get_source_type"))


class TestExport(unittest.TestCase):
    """
    Description:
    - The row shape written to the cleaned output file.
    """

    # Test the full exported row
    def test_to_dict_exports_all_eight_fields(self):
        """
        Objective:
        - Check the whole export in one go, including the original
          currency symbol, which has to survive for the record.

        Expectation:
        - The exported row matches T1044 field for field, with the type
          filled in by the subclass and the amount still unsigned.
        """
        exported = make_expense().to_dict()
        self.assertEqual(exported, {
            "transaction_id": "T1044",
            "user_id": "U075",
            "date": "2021-05-06",
            "transaction_type": "Expense",
            "category": "Food",
            "amount": 1810.0,
            "payment_mode": "Card",
            "original_currency": "₹",
        })

    # Test that income exports its own type
    def test_income_exports_its_own_type(self):
        """
        Objective:
        - Check the exported type comes from the subclass, so the file
          can never disagree with the object that wrote it.

        Expectation:
        - An income row exports transaction_type 'Income'.
        """
        self.assertEqual(make_income().to_dict()["transaction_type"],
                         "Income")

    # Test that an undated row exports a null date
    def test_an_undated_row_exports_none(self):
        """
        Objective:
        - Check the export keeps a dateless row rather than inventing a
          date for it.

        Expectation:
        - The exported date is None.
        """
        self.assertIsNone(ExpenseTransaction(*UNDATED_ROW).to_dict()["date"])


class TestEncapsulation(unittest.TestCase):
    """
    Description:
    - The fields are private, and the setter cannot be worked around.
    """

    # Test that the private attribute is not reachable by its plain name
    def test_the_amount_is_not_reachable_directly(self):
        """
        Objective:
        - Check the field really is private, so the getter is the only
          way in rather than just the polite way.

        Expectation:
        - Reading __amount on the object raises AttributeError, because
          Python has renamed it.
        """
        with self.assertRaises(AttributeError):
            make_expense().__amount

    # Test that the storage is mangled under the base class name
    def test_the_storage_is_mangled_to_the_base_class(self):
        """
        Objective:
        - Check the field belongs to Transaction, not to the subclass,
          which is what stops a subclass shadowing it by accident.

        Expectation:
        - The value is reachable only as _Transaction__amount.
        """
        row = make_expense()
        self.assertEqual(row._Transaction__amount, 1810.0)

    # Test that a subclass cannot bypass the setter
    def test_a_subclass_cannot_write_past_the_setter(self):
        """
        Objective:
        - Check why the fields are private rather than protected. A
          protected amount would let a subclass store a negative and skip
          the validation entirely.

        Expectation:
        - A subclass writing self._amount = -500 creates a new, unrelated
          attribute; the real amount is untouched.
        """
        class SneakyExpense(ExpenseTransaction):
            def cheat(self):
                self._amount = -500          # creates a NEW attribute

        row = SneakyExpense(*EXPENSE_ROW)
        row.cheat()
        self.assertEqual(row.get_amount(), 1810.0)
        self.assertEqual(row.get_signed_amount(), -1810.0)

    # Test that the subclasses read through the inherited getters
    def test_a_subclass_reads_through_the_getter(self):
        """
        Objective:
        - Check the subclass works from live state rather than a value
          cached when the object was built.

        Expectation:
        - After set_amount(99.0), get_signed_amount() returns -99.0.
        """
        row = make_expense()
        row.set_amount(99.0)
        self.assertEqual(row.get_signed_amount(), -99.0)


class TestRepr(unittest.TestCase):
    """
    Description:
    - The debugging form. What matters most is that it never raises.
    """

    # Test the formatted output
    def test_repr_names_the_class_id_category_and_amount(self):
        """
        Objective:
        - Check it carries enough to identify the row at a prompt.

        Expectation:
        - The string names the class, id, category and amount.
        """
        self.assertEqual(repr(make_expense()),
                         "ExpenseTransaction('T1044', 'Food', 1,810.00)")

    # Test that it works on the base class too
    def test_repr_does_not_raise_on_the_base_class(self):
        """
        Objective:
        - Check it avoids the direction methods on purpose. A __repr__
          that raises breaks debuggers and error messages exactly when
          they are needed.

        Expectation:
        - A base Transaction prints normally instead of raising.
        """
        row = Transaction("T999", "U001", "2023-07-14", "Food", 5000.0)
        self.assertEqual(repr(row), "Transaction('T999', 'Food', 5,000.00)")

    # Test that it works for income as well
    def test_repr_names_the_income_subclass(self):
        """
        Objective:
        - Check each subclass labels itself without overriding __repr__,
          since the name comes from the object's own class.

        Expectation:
        - An income row's text starts with 'IncomeTransaction('.
        """
        self.assertTrue(repr(make_income()).startswith("IncomeTransaction("))


if __name__ == "__main__":
    unittest.main(verbosity=2)
