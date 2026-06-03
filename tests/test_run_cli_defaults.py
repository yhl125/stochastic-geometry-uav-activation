import unittest
from pathlib import Path


class RunCliDefaultTests(unittest.TestCase):
    def test_default_iterations_use_paper_table_value(self):
        source = Path("src/run.py").read_text()

        self.assertIn("import params as P", source)
        self.assertIn("default=P.MC_ITERS_FINAL", source)


if __name__ == "__main__":
    unittest.main()
