import unittest

from budgetwise.cleaning.payment_modes import normalize_payment_mode


class TestPaymentModeParser(unittest.TestCase):

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

    def test_unknown_payment_mode(self):
        self.assertEqual(
            normalize_payment_mode("Cheque"),
            ("Unknown", "PAYMENT_MODE_UNKNOWN")
        )

    def test_observed_payment_mode_variants(self):
        cases = [
            ("Upi", "UPI"),
            ("UPi", "UPI"),
            ("CARD", "Card"),
            ("Crd", "Card"),
            ("CRD", "Card"),
            ("CASH", "Cash"),
            ("Csh", "Cash"),
            ("csh", "Cash"),
            ("BankTransfer", "Bank Transfer"),
            ("Bank_Transfer", "Bank Transfer"),
            ("Bank Transfr", "Bank Transfer"),
        ]

        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(
                    normalize_payment_mode(raw),
                    (expected, "PAYMENT_MODE_NORMALIZED")
                )


if __name__ == "__main__":
    unittest.main()
