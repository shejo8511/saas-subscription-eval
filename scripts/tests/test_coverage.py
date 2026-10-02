import unittest

from scripts.check_coverage import check


class CoverageThresholdTest(unittest.TestCase):
    def test_combined_coverage_cannot_hide_low_branch_coverage(self):
        with self.assertRaisesRegex(ValueError, "branches"):
            check(
                {
                    "totals": {
                        "num_statements": 100,
                        "covered_lines": 100,
                        "num_branches": 10,
                        "covered_branches": 7,
                    }
                }
            )

    def test_insufficient_line_coverage_fails(self):
        with self.assertRaisesRegex(ValueError, "lines"):
            check(
                {
                    "totals": {
                        "num_statements": 10,
                        "covered_lines": 7,
                        "num_branches": 10,
                        "covered_branches": 10,
                    }
                }
            )

    def test_threshold_boundary_passes(self):
        self.assertEqual(
            check(
                {
                    "totals": {
                        "num_statements": 10,
                        "covered_lines": 8,
                        "num_branches": 10,
                        "covered_branches": 8,
                    }
                }
            ),
            {"lines": 80.0, "branches": 80.0},
        )

    def test_empty_report_fails(self):
        with self.assertRaisesRegex(ValueError, "No application"):
            check(
                {
                    "totals": {
                        "num_statements": 0,
                        "covered_lines": 0,
                        "num_branches": 0,
                        "covered_branches": 0,
                    }
                }
            )
