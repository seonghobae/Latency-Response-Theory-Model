"""Real pandas loading checks; not full application or estimator integration.

Requires the project's existing numpy/pandas dependencies. Extracting only the
loader avoids importing scipy or running application-level estimation.
"""

import ast
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = ROOT_DIRECTORY / "data" / "benchmarks"


class CombinedPandasLoading(unittest.TestCase):
    """Check actual frames and declared shape/row contracts."""

    def setUp(self):
        source_path = ROOT_DIRECTORY / "applications" / "predictive_power.py"
        source_tree = ast.parse(source_path.read_text())
        loader_node = next(node for node in source_tree.body
                           if isinstance(node, ast.FunctionDef)
                           and node.name == "load_combined_benchmarks")
        namespace = {"np": np, "pd": pd, "DATA_DIR": DATA_DIRECTORY}
        exec(compile(ast.Module(body=[loader_node], type_ignores=[]),
                     str(source_path), "exec"), namespace)
        self.load_combined = namespace["load_combined_benchmarks"]
        self.response_frame = pd.read_csv(
            DATA_DIRECTORY / "correctness_matrix_combined.csv", index_col=0)
        self.length_frame = pd.read_csv(
            DATA_DIRECTORY / "cot_length_matrix_combined.csv", index_col=0)

    def test_real_counts_are_preserved_and_log_is_finite(self):
        response_values, count_values = self.load_combined()
        self.assertEqual(response_values.shape, (128, 100))
        np.testing.assert_array_equal(count_values, self.length_frame.to_numpy(dtype=float))
        self.assertTrue(np.isfinite(np.log(count_values)).all())

    def test_shape_and_row_mismatch_are_rejected(self):
        for invalid_frame in (self.length_frame.iloc[:-1], self.length_frame.iloc[::-1]):
            with self.subTest(shape=invalid_frame.shape):
                with patch.object(pd, "read_csv", side_effect=[self.response_frame, invalid_frame]):
                    with self.assertRaises(ValueError):
                        self.load_combined()


if __name__ == "__main__":
    unittest.main()
