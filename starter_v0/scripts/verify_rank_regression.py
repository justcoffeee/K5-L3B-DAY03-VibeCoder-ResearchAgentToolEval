"""Prove rank regression tests fail on the original parser and pass on this tree."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "0f3c8e087041ae1b500e3fddd1e23509028cf381"
TEST = "tests/test_tools_todo.py::test_rank_invalid_engagement_counts_are_zero"
MUTANT = r"""
import ast, importlib, subprocess, pytest
module = importlib.import_module("tools.rank.tool")
source = subprocess.check_output(["git", "show", "0f3c8e087041ae1b500e3fddd1e23509028cf381:starter_v0/tools/rank/tool.py"], text=True, encoding="utf-8")
node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "_num")
exec(compile(ast.Module(body=[node], type_ignores=[]), "original_num", "exec"), module.__dict__)
raise SystemExit(pytest.main(["-q", "-p", "no:cacheprovider", "tests/test_tools_todo.py::test_rank_invalid_engagement_counts_are_zero"]))
"""


def main() -> None:
    print(f"Original _num from {BASE}; expected: 3 failed, 6 passed", flush=True)
    original = subprocess.run([sys.executable, "-c", MUTANT], cwd=ROOT, text=True, encoding="utf-8", capture_output=True)
    print(original.stdout, end="", flush=True)
    print(original.stderr, end="", flush=True)
    assert original.returncode == 1 and "3 failed, 6 passed" in original.stdout
    print("Current _num; expected: 9 passed", flush=True)
    fixed = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", TEST], cwd=ROOT)
    assert fixed.returncode == 0
    print("Regression verified: original parser fails; current parser passes.")


if __name__ == "__main__":
    main()
