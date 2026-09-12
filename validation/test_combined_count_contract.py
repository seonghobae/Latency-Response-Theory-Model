"""Stored benchmark counts stay raw, as specified by data/README.md.

Applications, not serialized artifacts, own the unit pseudocount. This checks
the retained published cohort without fitting models or reconstructing omitted
generation records.
"""

import csv
from decimal import Decimal
from pathlib import Path
import unittest

DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data" / "benchmarks"


def read_matrix(file_name):
    """Read exact counts and reject ambiguous case-normalized row identities."""
    with (DATA_DIRECTORY / file_name).open(newline="") as input_file:
        matrix_rows = list(csv.reader(input_file))
    item_labels = matrix_rows[0][1:]
    model_rows = {}
    for matrix_row in matrix_rows[1:]:
        model_name = matrix_row[0].lower()
        if model_name in model_rows or len(matrix_row) != len(item_labels) + 1:
            raise ValueError("ambiguous or incomplete matrix row")
        model_rows[model_name] = tuple(Decimal(value) for value in matrix_row[1:])
    return item_labels, model_rows


class CombinedCountContract(unittest.TestCase):
    """Verify benchmark-qualified count preservation, not estimator accuracy."""

    def test_combined_artifact_preserves_raw_source_counts(self):
        for matrix_kind in ("correctness", "cot_length"):
            with self.subTest(matrix_kind=matrix_kind):
                combined_labels, combined_rows = read_matrix(
                    f"{matrix_kind}_matrix_combined.csv"
                )
                source_matrices = [
                    read_matrix(f"{matrix_kind}_matrix_{benchmark_name}.csv")
                    for benchmark_name in ("aime24", "aime25", "amc23")
                ]
                self.assertEqual(combined_labels, sum(
                    [labels for labels, _ in source_matrices], []
                ))
                for model_name, combined_counts in combined_rows.items():
                    source_counts = sum(
                        [rows[model_name] for _, rows in source_matrices], ()
                    )
                    self.assertEqual(combined_counts, source_counts, model_name)


if __name__ == "__main__":
    unittest.main()
