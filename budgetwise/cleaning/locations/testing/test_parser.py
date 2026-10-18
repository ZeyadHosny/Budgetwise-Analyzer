import unittest

from budgetwise.cleaning.locations import normalize_location


class TestLocationParser(unittest.TestCase):

    def test_all_profiled_location_variants(self):
        cases = [
            # Pune
            ("Pune", ("Pune", None)),
            ("PUNE", ("Pune", "LOCATION_NORMALIZED")),
            ("pune", ("Pune", "LOCATION_NORMALIZED")),
            ("PUN", ("Pune", "LOCATION_NORMALIZED")),

            # Bangalore
            ("Bangalore", ("Bangalore", None)),
            ("BANGALORE", ("Bangalore", "LOCATION_NORMALIZED")),
            ("bangalore", ("Bangalore", "LOCATION_NORMALIZED")),
            ("BAN", ("Bangalore", "LOCATION_NORMALIZED")),

            # Chennai
            ("Chennai", ("Chennai", None)),
            ("CHENNAI", ("Chennai", "LOCATION_NORMALIZED")),
            ("chennai", ("Chennai", "LOCATION_NORMALIZED")),
            ("CHE", ("Chennai", "LOCATION_NORMALIZED")),

            # Hyderabad
            ("Hyderabad", ("Hyderabad", None)),
            ("HYDERABAD", ("Hyderabad", "LOCATION_NORMALIZED")),
            ("hyderabad", ("Hyderabad", "LOCATION_NORMALIZED")),
            ("HYD", ("Hyderabad", "LOCATION_NORMALIZED")),

            # Jaipur
            ("Jaipur", ("Jaipur", None)),
            ("JAIPUR", ("Jaipur", "LOCATION_NORMALIZED")),
            ("jaipur", ("Jaipur", "LOCATION_NORMALIZED")),
            ("JAI", ("Jaipur", "LOCATION_NORMALIZED")),

            # Kolkata
            ("Kolkata", ("Kolkata", None)),
            ("KOLKATA", ("Kolkata", "LOCATION_NORMALIZED")),
            ("kolkata", ("Kolkata", "LOCATION_NORMALIZED")),
            ("KOL", ("Kolkata", "LOCATION_NORMALIZED")),

            # Delhi
            ("Delhi", ("Delhi", None)),
            ("DELHI", ("Delhi", "LOCATION_NORMALIZED")),
            ("delhi", ("Delhi", "LOCATION_NORMALIZED")),
            ("DEL", ("Delhi", "LOCATION_NORMALIZED")),

            # Lucknow
            ("Lucknow", ("Lucknow", None)),
            ("LUCKNOW", ("Lucknow", "LOCATION_NORMALIZED")),
            ("lucknow", ("Lucknow", "LOCATION_NORMALIZED")),
            ("LUC", ("Lucknow", "LOCATION_NORMALIZED")),

            # Ahmedabad
            ("Ahmedabad", ("Ahmedabad", None)),
            ("AHMEDABAD", ("Ahmedabad", "LOCATION_NORMALIZED")),
            ("ahmedabad", ("Ahmedabad", "LOCATION_NORMALIZED")),
            ("AHM", ("Ahmedabad", "LOCATION_NORMALIZED")),

            # Mumbai
            ("Mumbai", ("Mumbai", None)),
            ("MUMBAI", ("Mumbai", "LOCATION_NORMALIZED")),
            ("mumbai", ("Mumbai", "LOCATION_NORMALIZED")),
            ("MUM", ("Mumbai", "LOCATION_NORMALIZED")),

            # Profiled missing values
            ("", ("Unknown", "LOCATION_UNKNOWN")),
            ("N/A", ("Unknown", "LOCATION_UNKNOWN")),
        ]

        # 42 profiled cases
        self.assertEqual(len(cases), 42)

        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(
                    normalize_location(raw),
                    expected
                )

    def test_location_with_spaces(self):
        self.assertEqual(
            normalize_location("  Pune  "),
            ("Pune", "LOCATION_NORMALIZED")
        )

    def test_missing_spaces(self):
        self.assertEqual(
            normalize_location("   "),
            ("Unknown", "LOCATION_UNKNOWN")
        )

    def test_missing_none(self):
        self.assertEqual(
            normalize_location(None),
            ("Unknown", "LOCATION_UNKNOWN")
        )

    def test_unknown_location(self):
        self.assertEqual(
            normalize_location("UnknownCity"),
            ("Unknown", "LOCATION_UNKNOWN")
        )


    def test_bengaluru_maps_to_bangalore(self):
        for raw in ("Bengaluru", "bengaluru", "BENGALURU"):
            with self.subTest(raw=raw):
                self.assertEqual(normalize_location(raw),
                                 ("Bangalore", "LOCATION_NORMALIZED"))

if __name__ == "__main__":
    unittest.main()
