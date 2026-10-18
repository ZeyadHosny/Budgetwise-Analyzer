"""Structural checks that hold before any feature is implemented.

These guard three things that fail silently if they break:

1. Every feature folder keeps the agreed shape, so nobody is left without a
   place to put their work.
2. Every testing/ folder is a Python package. Without __init__.py, unittest
   skips that folder and still reports OK - see CONTRIBUTING.md section 6.
3. No pandas or NumPy reaches the core pipeline. Project-1.pdf section 2
   forbids it, and no workbook task verifies it.

Standard library only, in keeping with the rest of the project.
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACKAGE = REPO / "budgetwise"

# One README per feature folder (P2.0 folder rules). testing/ keeps its
# __init__.py so unittest can find it.
REQUIRED_FILES = (
    "README.md",
    "__init__.py",
    "testing/__init__.py",
)

FORBIDDEN = re.compile(r"^\s*(?:import|from)\s+(pandas|numpy)\b", re.MULTILINE)


def feature_folders():
    """Every folder in the package that holds an implementation/ directory."""
    return sorted(p.parent for p in PACKAGE.glob("**/implementation"))


class TestFeatureLayout(unittest.TestCase):
    """Each feature folder keeps the shape agreed at P0.1."""

    def test_features_exist(self):
        self.assertGreater(len(feature_folders()), 0, "no feature folders found")

    def test_every_feature_has_required_files(self):
        missing = [
            f"{f.relative_to(REPO).as_posix()}/{name}"
            for f in feature_folders()
            for name in REQUIRED_FILES
            if not (f / name).exists()
        ]
        self.assertEqual(missing, [], f"missing files: {missing}")


class TestDiscoverability(unittest.TestCase):
    """Test folders must be packages or unittest skips them without saying so."""

    def test_every_testing_folder_is_a_package(self):
        orphans = [
            d.relative_to(REPO).as_posix()
            for d in PACKAGE.glob("**/testing")
            if d.is_dir() and not (d / "__init__.py").exists()
        ]
        self.assertEqual(
            orphans,
            [],
            "these test folders lack __init__.py, so their tests are silently "
            f"skipped: {orphans}",
        )

    def test_shared_test_folders_are_packages(self):
        for name in ("end_to_end", "robustness"):
            with self.subTest(folder=name):
                self.assertTrue(
                    (REPO / "tests" / name / "__init__.py").exists(),
                    f"tests/{name}/__init__.py is missing",
                )


class TestLibraryRestriction(unittest.TestCase):
    """Project-1.pdf section 2 forbids pandas and NumPy in the core pipeline."""

    def test_no_pandas_or_numpy_in_package(self):
        offenders = []
        for py in PACKAGE.rglob("*.py"):
            found = FORBIDDEN.findall(py.read_text(encoding="utf-8"))
            if found:
                offenders.append(f"{py.relative_to(REPO).as_posix()}: {set(found)}")
        self.assertEqual(
            offenders,
            [],
            "Project-1.pdf section 2 permits only the standard library for "
            f"ingestion, cleaning, aggregation and analysis: {offenders}",
        )

    def test_no_pandas_or_numpy_in_entry_point(self):
        self.assertEqual(
            FORBIDDEN.findall((REPO / "main.py").read_text(encoding="utf-8")), []
        )


class TestDataPresent(unittest.TestCase):
    """The raw datasets are committed and unmodified - see data/README.md."""

    def test_both_datasets_present(self):
        raw = REPO / "data" / "raw"
        for name in ("budgetwise_finance_dataset.csv", "budgetwise_synthetic_dirty.csv"):
            with self.subTest(dataset=name):
                self.assertTrue((raw / name).exists(), f"{name} is missing")

    def test_total_size_matches_kaggle(self):
        """Kaggle reports 2,184,425 bytes across both files."""
        raw = REPO / "data" / "raw"
        total = sum(p.stat().st_size for p in raw.glob("*.csv"))
        self.assertEqual(
            total,
            2_184_425,
            "raw data no longer matches the published dataset - check that "
            ".gitattributes still disables line-ending conversion on data/raw",
        )


if __name__ == "__main__":
    unittest.main()
