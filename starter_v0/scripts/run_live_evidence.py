"""Run the unchanged group harness or chat CLI with real APIs and delivery disabled."""
from __future__ import annotations

import argparse
import builtins
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from datetime import datetime, timezone, timedelta
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import sys
from unittest.mock import patch
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from env_loader import load_lab_env
from scripts.cp2_experiment import make_rate_limit_retry

CHAT_INPUTS = [
    "Dùng lookup để tra cứu trên web 1 tài liệu chính thức về Python asyncio. Chỉ trả lời ngắn gồm tiêu đề và URL nguồn; không gửi Telegram.",
    "Tóm tắt 1 tweet mới nhất giúp mình, nhưng mình chưa nói của tài khoản nào. Hãy hỏi lại dữ kiện còn thiếu.",
    "Tài khoản X là @sama. Lấy đúng 1 tweet mới nhất, tóm tắt ngắn và kèm URL nguồn.",
    "Soạn bản nháp Telegram với đúng nội dung: Buổi đọc paper của nhóm bắt đầu lúc 19 giờ. Chưa gửi ngay.",
    "Mình muốn gửi đúng bản nháp đó lên private channel của nhóm. Hãy hỏi mình xác nhận trước; hiện chưa có xác nhận gửi.",
    "Không gửi. Hủy yêu cầu gửi; giữ nguyên bản nháp và không thực hiện hành động nào thêm.",
]


def now():
    return datetime.now(timezone(timedelta(hours=7))).isoformat(timespec="seconds")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def new_evidence_paths(folder, before, artifact_version, model):
    """Ignore concurrent sessions rather than annotating another run's file."""
    selected = set()
    for path in set(folder.glob("*.json")) - before:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            continue
        if data.get("artifact_version") == artifact_version and data.get("model") == model:
            selected.add(path)
    return selected


def preserve_declined_tool_response(complete, events):
    """Expose actual plain model text returned inside Groq's required-tool 400.

    This is a scored no-tool response, never a successful tool call. Other 400s
    remain provider errors; no generated text or calls are invented or retried.
    """
    from openai import BadRequestError
    from providers.base import ModelResponse

    def wrapped(self, *args, **kwargs):
        try:
            return complete(self, *args, **kwargs)
        except BadRequestError as exc:
            body = getattr(exc, "body", None)
            error = body.get("error", body) if isinstance(body, dict) else {}
            if not isinstance(error, dict):
                raise
            generation = error.get("failed_generation")
            if (error.get("code") != "tool_use_failed"
                    or error.get("message") != "Tool choice is required, but model did not call a tool"
                    or not isinstance(generation, str) or not generation.strip()):
                raise
            events.append({"at": now(), "http_status": 400, "body": body,
                           "interpretation": "actual model text; zero tool calls; score missing tool as FAIL"})
            print("Captured required-tool rejection as an actual no-tool model response (not PASS)", flush=True)
            return ModelResponse(text=generation, tool_calls=[], raw={"provider_error_body": body})
    return wrapped


@contextmanager
def delivery_disabled():
    """Preserve selected tool calls for scoring; block every Telegram delivery."""
    import requests
    from tools import TOOL_FUNCTIONS
    original_request = requests.Session.request

    def blocked_send(text="", confirmed=False):
        return {"tool": "send", "status": "blocked_for_evidence",
                "message": "Telegram delivery is disabled for this evidence session."}

    def guarded_request(self, method, url, *args, **kwargs):
        if (urlparse(str(url)).hostname or "").lower() == "api.telegram.org":
            raise RuntimeError("Telegram network access disabled for evidence")
        return original_request(self, method, url, *args, **kwargs)

    with patch.dict(TOOL_FUNCTIONS, {"send": blocked_send}), patch.object(requests.Session, "request", guarded_request):
        yield


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["group", "chat"])
    parser.add_argument("--model", default="openai/gpt-oss-20b")
    parser.add_argument("--version", default="v4-integration")
    args = parser.parse_args()
    os.chdir(ROOT)
    load_lab_env(ROOT)
    secrets = [value for key, value in os.environ.items()
               if len(value) > 7 and (key.endswith("_KEY") or "TOKEN" in key)]

    def redact(text):
        for secret in secrets:
            text = text.replace(secret, "[REDACTED]")
        return text

    from versioning import build_artifact_version, artifact_version_dict
    artifact = artifact_version_dict(build_artifact_version(args.version, ROOT / "artifacts/system_prompt.md", ROOT / "artifacts/tools.yaml"))
    handoff = json.loads((ROOT / "analysis/cp2_handoff.json").read_text(encoding="utf-8"))
    assert artifact["prompt_hash"] == handoff["prompt_hash"]
    assert artifact["tools_hash"] == handoff["tools_hash"]
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    plan_path = ROOT / "analysis" / f"live_{args.mode}_{stamp}.plan.json"
    plan = {"recorded_before_execution_at": now(), "mode": args.mode, **artifact,
            "provider": "groq", "model": args.model,
            "requested_by": "justcoffeee", "executed_by": "Codex (AI assistant)",
            "telegram": "disabled_for_entire_session", "real_external_human_test": False,
            "response_normalization": "Preserve actual failed_generation text only for exact required-tool/no-call rejection; score as no tool, retain raw HTTP 400 body. Other errors unchanged.",
            "inputs": CHAT_INPUTS if args.mode == "chat" else "data/eval_group.json",
            "group_dataset_sha256": hashlib.sha256((ROOT / "data/eval_group.json").read_bytes()).hexdigest()}
    write_json(plan_path, plan)
    folder = ROOT / ("runs" if args.mode == "group" else "transcripts")
    folder.mkdir(exist_ok=True)
    before = set(folder.glob("*.json"))
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

    from providers.openai_provider import OpenAIProvider
    retry_events = []
    declined_tool_responses = []
    complete = preserve_declined_tool_response(make_rate_limit_retry(OpenAIProvider.complete, retry_events, 3), declined_tool_responses)
    policy = {"plan": plan_path.relative_to(ROOT).as_posix(), "requested_by": "justcoffeee",
              "operator": "Codex (AI assistant)", "telegram": "disabled_for_entire_session",
              "provider_tool_apis": "live", "model": args.model, "version": args.version, "real_external_human_test": False,
              "scripted_user_inputs": args.mode == "chat", "rate_limit_retries": retry_events,
              "preserved_required_tool_rejections": declined_tool_responses,
              "normalization_is_scored_model_failure": True}
    previous_argv = sys.argv
    try:
        with delivery_disabled(), patch.object(OpenAIProvider, "complete", complete), redirect_stdout(SafeOutput()), redirect_stderr(SafeOutput()):
            common = ["--provider", "groq", "--model", args.model, "--version", args.version]
            if args.mode == "group":
                sys.argv = ["run_eval.py", *common, "--suite", "group", "--eval-cases", "data/eval_group.json"]
                runpy.run_path(str(ROOT / "run_eval.py"), run_name="__main__")
            else:
                inputs = iter([*CHAT_INPUTS, "/exit"])

                def scripted_input(prompt=""):
                    value = next(inputs)
                    print(prompt + value, flush=True)
                    return value

                sys.argv = ["chat.py", *common, "--max-tool-rounds", "4"]
                with patch.object(builtins, "input", scripted_input):
                    runpy.run_path(str(ROOT / "chat.py"), run_name="__main__")
    finally:
        sys.argv = previous_argv
        (ROOT / "analysis" / f"live_{args.mode}_{stamp}.log.txt").write_text(captured.getvalue(), encoding="utf-8")
        new_paths = new_evidence_paths(folder, before, artifact["artifact_version"], args.model)
        for path in new_paths:
            data = json.loads(redact(path.read_text(encoding="utf-8")))
            data["execution_policy"] = policy
            write_json(path, data)
    assert len(new_paths) == 1, "Expected one new evidence file"
    path = new_paths.pop()
    data = json.loads(path.read_text(encoding="utf-8"))
    if args.mode == "group":
        summary = data["summary"]
        valid = summary["provider_error_cases"] == 0 and summary["measured_cases"] == summary["total_cases"] == 10
    else:
        valid = len(data["turns"]) == len(CHAT_INPUTS) and all(t["status"] in {"answered", "waiting_for_user"} for t in data["turns"])
    print(("VALID_EVIDENCE " if valid else "INCOMPLETE_EVIDENCE ") + path.relative_to(ROOT).as_posix())
    if not valid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
