import tomllib
import unittest
from pathlib import Path


class UvProjectConfigTests(unittest.TestCase):
    def test_pyproject_declares_runtime_dependencies(self):
        data = tomllib.loads(Path("pyproject.toml").read_text())
        deps = set(data["project"]["dependencies"])

        for package in ("numpy", "scipy", "matplotlib"):
            self.assertTrue(
                any(dep.lower().startswith(package) for dep in deps),
                f"missing dependency: {package}",
            )

    def test_project_is_uv_application_not_packaged_library(self):
        data = tomllib.loads(Path("pyproject.toml").read_text())

        self.assertFalse(data["tool"]["uv"]["package"])
        self.assertGreaterEqual(data["project"]["requires-python"], ">=3.11")


if __name__ == "__main__":
    unittest.main()
