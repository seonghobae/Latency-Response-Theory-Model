"""Stored benchmark counts stay raw, as specified by data/README.md.

Applications, not serialized artifacts, own the unit pseudocount. This checks
the retained published cohort without fitting models or reconstructing omitted
generation records.
"""

import ast
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

    def test_versioned_combined_artifact_preserves_declared_encoding(self):
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
                    expected_counts = tuple(
                        value + (1 if matrix_kind == "cot_length" else 0)
                        for value in source_counts
                    )
                    self.assertEqual(combined_counts, expected_counts, model_name)

    def test_both_combined_consumers_preserve_encoded_values(self):
        """Execute the exact conversion expressions with a scalar frame double.

        This does not claim pandas integration or estimator execution.
        """
        class ScalarFrame:
            def __init__(self, count_value):
                self.count_value = count_value

            def to_numpy(self, dtype):
                return dtype(self.count_value)

        for file_name, frame_name in (
            ("predictive_power.py", "latency"),
            ("item_efficiency.py", "cot_df"),
        ):
            source_path = DATA_DIRECTORY.parents[1] / "applications" / file_name
            source_tree = ast.parse(source_path.read_text())
            if frame_name == "latency":
                loader = next(node for node in source_tree.body
                              if isinstance(node, ast.FunctionDef)
                              and node.name == "load_combined_benchmarks")
                conversion = next(node.value.elts[1] for node in loader.body
                                  if isinstance(node, ast.Return))
            else:
                conversion = next(node.value for node in source_tree.body
                                  if isinstance(node, ast.Assign)
                                  and any(isinstance(target, ast.Name)
                                          and target.id == "cot_array"
                                          for target in node.targets))
            expression = compile(ast.Expression(conversion), str(source_path), "eval")
            for count_value in (1, 2, 3684):
                with self.subTest(file_name=file_name, count_value=count_value):
                    self.assertEqual(eval(expression, {frame_name: ScalarFrame(count_value)}),
                                     float(count_value))


if __name__ == "__main__":
    unittest.main()
