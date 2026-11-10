"""Record a hypothesis, then run the unchanged base harness with sends disabled."""
from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import io
import json
import os
import re
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from env_loader import load_lab_env

ARTIFACTS = ROOT / "artifacts"
PLANS = ROOT / "analysis" / "cp2_plans"
LOG = ARTIFACTS / "version_log.csv"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def now():
    return datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds")


def make_rate_limit_retry(complete, events, retries):
    """Retry only rejected 429 requests, preserving request arguments and failures."""
    from openai import RateLimitError

    def wrapped(self, *complete_args, **complete_kwargs):
        for retry in range(retries + 1):
            try:
                return complete(self, *complete_args, **complete_kwargs)
            except RateLimitError as exc:
                if retry == retries:
                    raise
                match = re.search(r"try again in ([0-9.]+)s", str(exc), re.IGNORECASE)
                delay = max(10.0, float(match.group(1)) + 1.0) if match else 30.0
                if delay > 60:
                    raise
                events.append({"at": now(), "retry": retry + 1, "delay_seconds": delay})
                print(f"Provider HTTP 429; retrying identical request in {delay:.1f}s", flush=True)
                time.sleep(delay)
    return wrapped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["plan", "run"])
    parser.add_argument("version")
    parser.add_argument("--artifact", choices=["system_prompt.md", "tools.yaml", "system_prompt.md+tools.yaml"])
    parser.add_argument("--hypothesis")
    parser.add_argument("--expected")
    parser.add_argument("--targets", nargs="*", default=[])
    parser.add_argument("--integration", action="store_true")
    parser.add_argument("--rate-limit-retries", type=int, default=3,
                        help="Retry only HTTP 429 without a model response; record every retry.")
    args = parser.parse_args()
    if not 0 <= args.rate_limit_retries <= 3:
        parser.error("--rate-limit-retries must be between 0 and 3")
    os.chdir(ROOT)
    plan_path = PLANS / f"{args.version}.json"
    with LOG.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames, rows = reader.fieldnames, list(reader)
    if args.action == "plan":
        if plan_path.exists() or not all([args.artifact, args.hypothesis, args.expected]):
            raise SystemExit("Plan must be new and include artifact/hypothesis/expected.")
        if "+" in args.artifact and not args.integration:
            raise SystemExit("Multiple artifact changes are allowed only for a labelled integration run.")
        previous_path = ROOT / rows[-1]["run_file"]
        previous = read(previous_path)
        assert previous["summary"]["provider_error_cases"] == 0
        assert previous["summary"]["measured_cases"] == previous["summary"]["total_cases"]
        write(plan_path, {
            "version": args.version, "recorded_before_edit_at": now(),
            "changed_artifact": args.artifact, "hypothesis": args.hypothesis,
            "expected": args.expected, "target_cases": args.targets,
            "previous_run": previous_path.relative_to(ROOT).as_posix(),
            "before_hashes": {name: digest(ARTIFACTS / name) for name in ["system_prompt.md", "tools.yaml"]},
            "integration": args.integration,
            "conditions": "RapidAPI subscription passed after v0; v0 had 7 tool errors. Same Groq/model; Telegram execution disabled; scorer unchanged.",
        })
        print(f"Recorded before edit: {plan_path.relative_to(ROOT)}")
        return

    plan = read(plan_path)
    assert not any(row["version"] == args.version for row in rows), "Version already has a valid run."
    changed = [name for name, before in plan["before_hashes"].items() if digest(ARTIFACTS / name) != before]
    expected_changes = plan["changed_artifact"].split("+")
    assert len(expected_changes) == 1 or plan["integration"], "Combined changes require integration label"
    assert changed == expected_changes, f"Expected {expected_changes}, found {changed}"
    snapshot = ARTIFACTS / "versions" / args.version
    snapshot.mkdir(parents=True, exist_ok=True)
    for name in ["system_prompt.md", "tools.yaml"]:
        target = snapshot / name
        if target.exists():
            assert digest(target) == digest(ARTIFACTS / name), "Cannot overwrite an experiment snapshot"
        else:
            shutil.copyfile(ARTIFACTS / name, target)
    write(snapshot / "manifest.json", {
        "version": args.version, "snapshot_at": now(), "plan": plan_path.relative_to(ROOT).as_posix(),
        "plan_sha256": digest(plan_path), "prompt_hash": digest(snapshot / "system_prompt.md"),
        "tools_hash": digest(snapshot / "tools.yaml"),
        "runtime_hashes": {name: digest(ROOT / name) for name in
                           ["agent.py", "run_eval.py", "tools/__init__.py",
                            "tools/analyze_text/tool.py", "tools/rank/tool.py"]},
    })
    load_lab_env(ROOT)
    sensitive = [value for key, value in os.environ.items() if value and (key.endswith("_KEY") or "TOKEN" in key)]

    def redact(text):
        for value in sensitive:
            text = text.replace(value, "[REDACTED]")
        return text

    test_env = dict(os.environ)
    for key in list(test_env):
        if key.endswith("_KEY") or "TOKEN" in key or key == "DAY03_ENV_FILE":
            test_env.pop(key, None)
    test_env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_tool_contract.py", "-p", "no:cacheprovider"],
                           capture_output=True, text=True, encoding="utf-8", env=test_env)
    (snapshot / "contract_test.txt").write_text(redact(tests.stdout + tests.stderr), encoding="utf-8")
    print(redact(tests.stdout + tests.stderr), flush=True)
    if tests.returncode:
        raise SystemExit("Contract tests failed; eval not started.")

    from tools import TOOL_FUNCTIONS
    def disabled_send(text="", confirmed=False):
        return {"tool": "send", "status": "blocked_for_eval", "message": "No Telegram delivery is allowed in CP2 eval."}
    TOOL_FUNCTIONS["send"] = disabled_send
    for key in ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]:
        os.environ.pop(key, None)
    import requests
    original_request = requests.Session.request
    def guarded_request(self, method, url, *request_args, **kwargs):
        from urllib.parse import urlparse
        if (urlparse(str(url)).hostname or "").lower() == "api.telegram.org":
            raise RuntimeError("Telegram network access disabled for eval")
        return original_request(self, method, url, *request_args, **kwargs)
    requests.Session.request = guarded_request
    # A rejected 429 has no model response or tool execution to score. Retry the
    # identical request after the server's delay; never retry a scored response
    # or an HTTP 400 tool-choice failure inside a case.
    from providers.openai_provider import OpenAIProvider
    original_complete = OpenAIProvider.complete
    rate_limit_events = []
    OpenAIProvider.complete = make_rate_limit_retry(original_complete, rate_limit_events, args.rate_limit_retries)
    before = set((ROOT / "runs").glob("*.json"))
    captured = io.StringIO()
    class SafeOutput(io.TextIOBase):
        def write(self, text):
            clean = redact(text)
            captured.write(clean)
            sys.__stdout__.write(clean)
            sys.__stdout__.flush()
            return len(text)
        def flush(self):
            sys.__stdout__.flush()
    sys.argv = ["run_eval.py", "--provider", "groq", "--model", "openai/gpt-oss-20b",
                "--version", args.version, "--suite", "base", "--eval-cases", "data/eval_base.json",
                "--system-prompt", str(snapshot / "system_prompt.md"), "--tools", str(snapshot / "tools.yaml")]
    started = now()
    try:
        with contextlib.redirect_stdout(SafeOutput()), contextlib.redirect_stderr(SafeOutput()):
            runpy.run_path(str(ROOT / "run_eval.py"), run_name="__main__")
    finally:
        attempt = len(list(snapshot.glob("eval_attempt_*.txt"))) + 1
        (snapshot / f"eval_attempt_{attempt}.txt").write_text(captured.getvalue(), encoding="utf-8")
        new_paths = set((ROOT / "runs").glob("*.json")) - before
        for path in new_paths:
            run = json.loads(redact(path.read_text(encoding="utf-8")))
            run["execution_policy"] = {"telegram": "disabled_and_credentials_removed", "scorer": "unchanged",
                                       "hypothesis_plan": plan_path.relative_to(ROOT).as_posix(), "started_at": started,
                                       "rate_limit_retries": rate_limit_events}
            write(path, run)
    assert len(new_paths) == 1, "Expected exactly one new run"
    path = new_paths.pop()
    run = read(path)
    previous = read(ROOT / plan["previous_run"])
    summary = run["summary"]
    old_cases = {item["id"]: item for item in previous["results"]}
    analysis = {
        "run_file": path.relative_to(ROOT).as_posix(), "previous_run": plan["previous_run"],
        "hypothesis": plan["hypothesis"], "expected": plan["expected"], "summary": summary,
        "fixed": [], "regressions": [], "still_failed": [], "tool_errors": [],
    }
    for item in run["results"]:
        before_pass = old_cases[item["id"]]["result"]["passed"]
        passed = item["result"]["passed"]
        if not passed or not before_pass:
            category = "fixed" if passed else ("regressions" if before_pass else "still_failed")
            analysis[category].append({"id": item["id"], "result": item["result"], "expect": item["expect"]})
        for event in item.get("tool_results", []):
            if isinstance(event.get("result"), dict) and event["result"].get("error"):
                analysis["tool_errors"].append({"case": item["id"], **event})
    write(snapshot / f"analysis_attempt_{attempt}.json", analysis)
    valid = summary["provider_error_cases"] == 0 and summary["measured_cases"] == summary["total_cases"]
    if not valid:
        raise SystemExit("Run is invalid evidence; preserved without adding version_log row. Retry only after resolving provider error.")
    row = dict.fromkeys(fieldnames, "")
    row.update(version=args.version, author="justcoffeee", changed_artifact=plan["changed_artifact"],
               artifact_version=run["artifact_version"], prompt_hash=run["prompt_hash"], tools_hash=run["tools_hash"],
               reason="Groq/openai/gpt-oss-20b; snapshots and preregistered plan retained; Telegram disabled",
               hypothesis=plan["hypothesis"], metric_before=str(previous["summary"]["case_accuracy"]),
               metric_after=str(summary["case_accuracy"]), run_file=path.relative_to(ROOT).as_posix())
    with LOG.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows + [row])
    print("VALID_RUN " + path.relative_to(ROOT).as_posix())
    print(json.dumps({"fixed": [x["id"] for x in analysis["fixed"]], "regressions": [x["id"] for x in analysis["regressions"]],
                      "tool_error_count": len(analysis["tool_errors"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
