#!/usr/bin/env python3
"""Generate a Lean #check traceability report from FORMULA_REGISTRY."""

from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
FORMAL = ROOT / "formal"
DEFAULT_REPORT = ROOT / "outputs" / "reports" / "lean_trace_check.md"
LOCAL_LAKE = "/Users/yhl/.elan/bin/lake"

sys.path.insert(0, str(ROOT / "src"))
from formulas import FORMULA_REGISTRY  # noqa: E402


@dataclass(frozen=True)
class TraceRow:
    paper_eq: str
    status: str
    lean_item: str
    result: str


def registry_lean_items() -> tuple[str, ...]:
    seen: set[str] = set()
    items: list[str] = []
    for entry in FORMULA_REGISTRY.values():
        for item in entry.lean_items:
            if item not in seen:
                seen.add(item)
                items.append(item)
    return tuple(items)


def build_check_source(items: tuple[str, ...]) -> str:
    lines = ["import Uav", ""]
    lines.extend(f"#check Uav.{item}" for item in items)
    return "\n".join(lines) + "\n"


def check_line_map(items: tuple[str, ...]) -> dict[int, str]:
    first_check_line = 3
    return {
        first_check_line + index: item
        for index, item in enumerate(items)
    }


def lake_command() -> str:
    return os.environ.get("LAKE") or shutil.which("lake") or LOCAL_LAKE


def run_lean_check(source: str, lake: str | None = None) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=FORMAL,
        prefix="TraceCheck.",
        suffix=".lean",
        delete=False,
    ) as temp:
        temp.write(source)
        temp_path = Path(temp.name)

    try:
        return subprocess.run(
            [lake or lake_command(), "env", "lean", str(temp_path)],
            cwd=FORMAL,
            check=False,
            text=True,
            capture_output=True,
        )
    finally:
        temp_path.unlink(missing_ok=True)


def failed_items_from_output(
    output: str,
    line_to_item: dict[int, str],
) -> frozenset[str]:
    failed: set[str] = set()
    for match in re.finditer(r"TraceCheck\.[^:\n]+\.lean:(\d+):\d+:\s+error:", output):
        item = line_to_item.get(int(match.group(1)))
        if item is not None:
            failed.add(item)
    return frozenset(failed)


def run_registry_check(
    items: tuple[str, ...],
) -> tuple[subprocess.CompletedProcess[str], frozenset[str]]:
    result = run_lean_check(build_check_source(items))
    failed = failed_items_from_output(
        result.stdout + result.stderr,
        check_line_map(items),
    )
    if result.returncode != 0 and not failed:
        return result, frozenset(items)
    return result, failed


def trace_rows(failed_items: frozenset[str]) -> tuple[TraceRow, ...]:
    rows: list[TraceRow] = []
    for entry in FORMULA_REGISTRY.values():
        for item in entry.lean_items:
            check_result = "fail" if item in failed_items else "pass"
            rows.append(TraceRow(entry.paper_eq, entry.status, item, check_result))
    return tuple(rows)


def render_markdown(rows: tuple[TraceRow, ...]) -> str:
    lines = [
        "# Lean #check Trace Report",
        "",
        "This report is generated from `FORMULA_REGISTRY` by elaborating a Lean file",
        "with `#check Uav.<item>` commands through `lake env lean`.",
        "",
        "| Paper equation | Status | Lean item | #check |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(
        f"| {row.paper_eq} | `{row.status}` | `{row.lean_item}` | {row.result} |"
        for row in rows
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    report_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_REPORT
    result, failed_items = run_registry_check(registry_lean_items())
    rows = trace_rows(failed_items)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_markdown(rows), encoding="utf-8")

    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
