from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from unittest import mock
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "scripts" / "lean_trace_report.py"


def load_report_module():
    spec = importlib.util.spec_from_file_location("lean_trace_report", REPORT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LeanTraceReportTest(unittest.TestCase):
    def test_build_check_source_prefixes_items_with_uav_namespace(self):
        report = load_report_module()

        source = report.build_check_source(
            ("eq1_friis_matches_paper_ref", "laplaceInterference")
        )

        self.assertIn("import Uav", source)
        self.assertIn("#check Uav.eq1_friis_matches_paper_ref", source)
        self.assertIn("#check Uav.laplaceInterference", source)

    def test_render_markdown_includes_status_and_rows(self):
        report = load_report_module()
        rows = (
            report.TraceRow(
                "Eq.1", "lean_verified", "eq1_friis_matches_paper_ref", "pass"
            ),
            report.TraceRow("Eq.17", "unverified", "laplaceInterference", "pass"),
        )

        markdown = report.render_markdown(rows)

        self.assertIn("| Paper equation | Status | Lean item | #check |", markdown)
        self.assertIn(
            "| Eq.1 | `lean_verified` | `eq1_friis_matches_paper_ref` | pass |",
            markdown,
        )
        self.assertIn(
            "| Eq.17 | `unverified` | `laplaceInterference` | pass |",
            markdown,
        )

    def test_lean_check_runs_trace_report(self):
        lean_check = (ROOT / "scripts" / "lean_check.sh").read_text(encoding="utf-8")

        self.assertIn("scripts/lean_trace_report.py", lean_check)

    def test_lake_command_prefers_env_var(self):
        report = load_report_module()

        with mock.patch.dict(os.environ, {"LAKE": "/tmp/custom-lake"}):
            with mock.patch.object(report.shutil, "which", return_value="/usr/bin/lake"):
                self.assertEqual("/tmp/custom-lake", report.lake_command())

    def test_lake_command_uses_path_before_local_fallback(self):
        report = load_report_module()

        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.object(report.shutil, "which", return_value="/usr/bin/lake"):
                self.assertEqual("/usr/bin/lake", report.lake_command())

    def test_lake_command_falls_back_to_local_elan_path(self):
        report = load_report_module()

        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.object(report.shutil, "which", return_value=None):
                self.assertEqual("/Users/yhl/.elan/bin/lake", report.lake_command())

    def test_trace_rows_can_represent_mixed_per_item_results(self):
        report = load_report_module()

        rows = report.trace_rows(frozenset({"laplaceInterference"}))
        row_by_item = {row.lean_item: row for row in rows}

        self.assertEqual("pass", row_by_item["eq1_friis_matches_paper_ref"].result)
        self.assertEqual("fail", row_by_item["laplaceInterference"].result)

    def test_failed_items_are_parsed_from_lean_diagnostics(self):
        report = load_report_module()
        items = ("eq1_friis_matches_paper_ref", "laplaceInterference")
        output = (
            "/tmp/TraceCheck.abc123.lean:4:7: error: "
            "Unknown constant Uav.laplaceInterference\n"
        )

        failed = report.failed_items_from_output(output, report.check_line_map(items))

        self.assertEqual(frozenset({"laplaceInterference"}), failed)

    def test_unmapped_nonzero_check_fails_all_items(self):
        report = load_report_module()

        with mock.patch.object(
            report,
            "run_lean_check",
            return_value=report.subprocess.CompletedProcess(
                args=(), returncode=1, stdout="", stderr="toolchain failed"
            ),
        ):
            _result, failed = report.run_registry_check(("a", "b"))

        self.assertEqual(frozenset({"a", "b"}), failed)


if __name__ == "__main__":
    unittest.main()
