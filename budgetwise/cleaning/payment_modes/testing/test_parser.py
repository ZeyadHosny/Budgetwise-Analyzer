import unittest

from budgetwise.cleaning.payment_modes import normalize_payment_mode


class TestPaymentModeParser(unittest.TestCase):

    # UPI
    def test_exact_upi(self):
        self.assertEqual(
            normalize_payment_mode("UPI"),
            ("UPI", None)
        )

    def test_lowercase_upi(self):
        self.assertEqual(
            normalize_payment_mode("upi"),
            ("UPI", "PAYMENT_MODE_NORMALIZED")
        )

    # Card
    def test_exact_card(self):
        self.assertEqual(
            normalize_payment_mode("Card"),
            ("Card", None)
        )

    def test_lowercase_card(self):
        self.assertEqual(
            normalize_payment_mode("card"),
            ("Card", "PAYMENT_MODE_NORMALIZED")
        )

    def test_card_abbreviation_crd(self):
        self.assertEqual(
            normalize_payment_mode("Crd"),
            ("Card", "PAYMENT_MODE_NORMALIZED")
        )

    def test_card_abbreviation_crd_uppercase(self):
        self.assertEqual(
            normalize_payment_mode("CRD"),
            ("Card", "PAYMENT_MODE_NORMALIZED")
        )

    # Cash
    def test_exact_cash(self):
        self.assertEqual(
            normalize_payment_mode("Cash"),
            ("Cash", None)
        )

    def test_lowercase_cash(self):
        self.assertEqual(
            normalize_payment_mode("cash"),
            ("Cash", "PAYMENT_MODE_NORMALIZED")
        )

    def test_cash_abbreviation_csh(self):
        self.assertEqual(
            normalize_payment_mode("Csh"),
            ("Cash", "PAYMENT_MODE_NORMALIZED")
        )

    def test_cash_abbreviation_csh_lowercase(self):
        self.assertEqual(
            normalize_payment_mode("csh"),
            ("Cash", "PAYMENT_MODE_NORMALIZED")
        )

    # Bank Transfer
    def test_exact_bank_transfer(self):
        self.assertEqual(
            normalize_payment_mode("Bank Transfer"),
            ("Bank Transfer", None)
        )

    def test_lowercase_bank_transfer(self):
        self.assertEqual(
            normalize_payment_mode("bank transfer"),
            ("Bank Transfer", "PAYMENT_MODE_NORMALIZED")
        )

    def test_bank_transfer_no_space(self):
        self.assertEqual(
            normalize_payment_mode("BankTransfer"),
            ("Bank Transfer", "PAYMENT_MODE_NORMALIZED")
        )

    def test_bank_transfer_underscore(self):
        self.assertEqual(
            normalize_payment_mode("Bank_Transfer"),
            ("Bank Transfer", "PAYMENT_MODE_NORMALIZED")
        )

    def test_bank_transfer_typo(self):
        self.assertEqual(
            normalize_payment_mode("Bank Transfr"),
            ("Bank Transfer", "PAYMENT_MODE_NORMALIZED")
        )

    # Whitespace
    def test_card_with_spaces(self):
        self.assertEqual(
            normalize_payment_mode("  Card  "),
            ("Card", "PAYMENT_MODE_NORMALIZED")
        )

    def test_bank_transfer_with_spaces(self):
        self.assertEqual(
            normalize_payment_mode("  Bank Transfer  "),
            ("Bank Transfer", "PAYMENT_MODE_NORMALIZED")
        )

    # Missing values
    def test_missing_empty_string(self):
        self.assertEqual(
            normalize_payment_mode(""),
            ("Unknown", "PAYMENT_MODE_UNKNOWN")
        )

    def test_missing_spaces(self):
        self.assertEqual(
            normalize_payment_mode("   "),
            ("Unknown", "PAYMENT_MODE_UNKNOWN")
        )

    def test_missing_none(self):
        self.assertEqual(
            normalize_payment_mode(None),
            ("Unknown", "PAYMENT_MODE_UNKNOWN")
        )

    # Unknown value
    def test_unknown_payment_mode(self):
        self.assertEqual(
            normalize_payment_mode("Cheque"),
            ("Unknown", "PAYMENT_MODE_UNKNOWN")
        )


if __name__ == "__main__":
    unittest.main()
