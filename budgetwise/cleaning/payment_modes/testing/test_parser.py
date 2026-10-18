import unittest

from budgetwise.cleaning.payment_modes import normalize_payment_mode


class TestPaymentModeParser(unittest.TestCase):

    def test_all_profiled_payment_mode_variants(self):
        cases = [
            # UPI
            ("UPI", ("UPI", None)),
            ("UPi", ("UPI", "PAYMENT_MODE_NORMALIZED")),
            ("Upi", ("UPI", "PAYMENT_MODE_NORMALIZED")),
            ("upi", ("UPI", "PAYMENT_MODE_NORMALIZED")),

            # Card
            ("Card", ("Card", None)),
            ("CARD", ("Card", "PAYMENT_MODE_NORMALIZED")),
            ("card", ("Card", "PAYMENT_MODE_NORMALIZED")),
            ("Crd", ("Card", "PAYMENT_MODE_NORMALIZED")),
            ("CRD", ("Card", "PAYMENT_MODE_NORMALIZED")),

            # Cash
            ("Cash", ("Cash", None)),
            ("CASH", ("Cash", "PAYMENT_MODE_NORMALIZED")),
            ("cash", ("Cash", "PAYMENT_MODE_NORMALIZED")),
            ("Csh", ("Cash", "PAYMENT_MODE_NORMALIZED")),
            ("csh", ("Cash", "PAYMENT_MODE_NORMALIZED")),

            # Bank Transfer
            ("Bank Transfer", ("Bank Transfer", None)),
            ("bank transfer", ("Bank Transfer", "PAYMENT_MODE_NORMALIZED")),
            ("BankTransfer", ("Bank Transfer", "PAYMENT_MODE_NORMALIZED")),
            ("Bank_Transfer", ("Bank Transfer", "PAYMENT_MODE_NORMALIZED")),
            ("Bank Transfr", ("Bank Transfer", "PAYMENT_MODE_NORMALIZED")),

            # Profiled missing value
            ("", ("Unknown", "PAYMENT_MODE_UNKNOWN")),
        ]

        # 20 profiled cases
        self.assertEqual(len(cases), 20)

        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(
                    normalize_payment_mode(raw),
                    expected
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


    # Synthetic dirty dataset: one-letter misspellings
    def test_dirty_spelling_variants(self):
        cases = {"UPPI": "UPI", "PUI": "UPI", "Csah": "Cash", "Cassh": "Cash",
                 "Crad": "Card", "Caard": "Card", "Bank Trasnfer": "Bank Transfer"}
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(normalize_payment_mode(raw),
                                 (expected, "PAYMENT_MODE_NORMALIZED"))

    # One letter from both Cash and Card, so left as Unknown.
    def test_ambiguous_variants_stay_unknown(self):
        for raw in ("Cah", "Cahs", "Cas", "Car", "Cad", "Cadr"):
            with self.subTest(raw=raw):
                self.assertEqual(normalize_payment_mode(raw),
                                 ("Unknown", "PAYMENT_MODE_UNKNOWN"))

if __name__ == "__main__":
    unittest.main()
