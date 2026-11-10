"""Verify recorded CP2 evidence offline without executing tools or contacting providers."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    def deny_network(*args, **kwargs):
        raise BaseException("CP2 evidence verification must remain offline")

    socket.socket.connect = deny_network
    socket.socket.connect_ex = deny_network
    socket.create_connection = deny_network
    socket.getaddrinfo = deny_network
    from run_eval import evaluate_phase_b, summarize

    for relative, expected in read(ROOT / "analysis/cp2_workspace_guard.json").items():
        # TEAM.md is unrelated workspace data; only the recorded immutable technical inputs are checked.
        if relative == "../TEAM.md":
            continue
        if relative == "run_eval.py" and digest(ROOT / relative) != expected:
            # PR #28 fixed sorting list-of-dict values. Preserve the original
            # harness/hash and verify both provenance and old case scores.
            context = read(ROOT / "analysis/cp2_integration_context.json")
            assert digest(ROOT / context["original_harness"]) == expected
            assert digest(ROOT / relative) == context["runtime_hashes"][relative]
            continue
        assert digest(ROOT / relative) == expected, f"Changed protected input: {relative}"
    cases = {case["id"]: case for case in read(ROOT / "data/eval_base.json")["cases"]}
    with (ROOT / "artifacts/version_log.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len({row["version"] for row in rows}) == len(rows), "Duplicate version label"
    valid_paths = set()
    previous = None
    for row in rows:
        version = row["version"]
        run = read(ROOT / row["run_file"])
        valid_paths.add(row["run_file"])
        summary = run["summary"]
        assert summary["provider_error_cases"] == 0, version
        assert summary["measured_cases"] == summary["total_cases"] == len(cases), version
        assert run["provider"] == "groq" and run["model"] == "openai/gpt-oss-20b", version
        assert run["version"] == version, version
        snapshot = ROOT / "artifacts/versions" / version
        for field, filename in [("prompt_hash", "system_prompt.md"), ("tools_hash", "tools.yaml")]:
            assert digest(snapshot / filename) == row[field] == run[field], f"{version}: {field}"
        expected_label = f"{version}+p{row['prompt_hash'][:12]}+t{row['tools_hash'][:12]}"
        assert row["artifact_version"] == run["artifact_version"] == expected_label, version
        assert {item["id"] for item in run["results"]} == set(cases), version
        for result in run["results"]:
            case = cases[result["id"]]
            assert result["expect"] == case["expect"], f"{version}: modified expectation"
            assert result["input"] == (case.get("input") or case.get("query") or case.get("turns")), version
            recalculated = evaluate_phase_b(case, result["result"]["actual_tool_calls"], result["result"]["actual_text"])
            assert result["result"] == recalculated, f"{version}: scorer mismatch in {case['id']}"
        assert summarize(run["results"]) == summary, f"{version}: summary mismatch"
        assert float(row["metric_after"]) == summary["case_accuracy"], version
        if previous is not None:
            assert float(row["metric_before"]) == previous["summary"]["case_accuracy"], version
            plan = read(ROOT / "analysis/cp2_plans" / f"{version}.json")
            manifest = read(snapshot / "manifest.json")
            assert manifest["plan_sha256"] == digest(ROOT / manifest["plan"]), version
            for relative, expected in manifest.get("runtime_hashes", {}).items():
                assert digest(ROOT / relative) == expected, f"{version}: changed runtime {relative}"
            changed = [name for name, before in plan["before_hashes"].items() if digest(snapshot / name) != before]
            expected_changes = row["changed_artifact"].split("+")
            assert len(expected_changes) == 1 or plan["integration"], version
            assert changed == expected_changes == plan["changed_artifact"].split("+"), version
            assert run["execution_policy"]["telegram"] == "disabled_and_credentials_removed", version
        print(f"{version}: {summary['passed_cases']}/{summary['total_cases']} PASS; hashes/scoring valid")
        previous = run
    last = rows[-1]
    for field, filename in [("prompt_hash", "system_prompt.md"), ("tools_hash", "tools.yaml")]:
        assert digest(ROOT / "artifacts" / filename) == last[field], f"Active artifact differs from {last['version']}"
    invalid = []
    for path in sorted((ROOT / "runs").glob("v*_B_base_groq_*.json")):
        if path.relative_to(ROOT).as_posix() not in valid_paths:
            data = read(path)
            s = data["summary"]
            if s["provider_error_cases"] or s["measured_cases"] != s["total_cases"]:
                invalid.append(path.name)
    print("Invalid attempts preserved outside version_log:", ", ".join(invalid) or "none")
    print("CP2 evidence verification PASSED (offline; no provider or tool execution)")


if __name__ == "__main__":
    main()
