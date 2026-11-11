"""Delivery guard checks; no external HTTP or credentials required."""
import pytest
import requests
from types import SimpleNamespace
from openai import BadRequestError

from scripts.run_live_evidence import delivery_disabled, preserve_declined_tool_response, new_evidence_paths
import json
from tools import TOOL_FUNCTIONS


def test_send_is_blocked_even_if_model_sets_confirmed_true():
    original = TOOL_FUNCTIONS["send"]
    with delivery_disabled():
        assert TOOL_FUNCTIONS["send"](text="test", confirmed=True)["status"] == "blocked_for_evidence"
        assert TOOL_FUNCTIONS["send"](text="test", confirmed=False)["status"] == "blocked_for_evidence"
    assert TOOL_FUNCTIONS["send"] is original


def test_telegram_transport_is_blocked_before_request():
    with delivery_disabled(), pytest.raises(RuntimeError, match="disabled"):
        requests.Session().request("POST", "https://api.telegram.org/bot-test/sendMessage")


def test_non_delivery_requests_delegate_without_rewriting(monkeypatch):
    calls = []
    marker = object()

    def fake_request(self, method, url, *args, **kwargs):
        calls.append((method, url, args, kwargs))
        return marker

    monkeypatch.setattr(requests.Session, "request", fake_request)
    with delivery_disabled():
        assert requests.Session().request("GET", "https://example.invalid", params={"q": "test"}) is marker
    assert calls == [("GET", "https://example.invalid", (), {"params": {"q": "test"}})]


def test_required_tool_rejection_preserves_exact_text_and_is_failed_by_scorer():
    from run_eval import evaluate_phase_b
    text = "The model answered directly instead of calling rank."
    body = {"message": "Tool choice is required, but model did not call a tool",
            "code": "tool_use_failed", "failed_generation": text}
    events, requests_seen = [], []

    def complete(self, **kwargs):
        requests_seen.append(kwargs)
        raise BadRequestError("rejected", response=SimpleNamespace(status_code=400, headers={}, request=SimpleNamespace()), body=body)

    response = preserve_declined_tool_response(complete, events)(object(), tool_choice="required")
    assert response.text == text and response.tool_calls == []
    assert len(requests_seen) == 1 and requests_seen[0] == {"tool_choice": "required"}
    case = {"id": "test", "failure_type": "wrong_tool", "expect": {"tool_calls": [{"name": "rank", "args": {}}]}}
    result = evaluate_phase_b(case, [], response.text)
    assert result["passed"] is False and result["observed_mismatch"] == "missing_tool_call"
    assert events[0]["body"] == body and events[0]["http_status"] == 400


@pytest.mark.parametrize("body", [None,
    {"code": "tool_use_failed", "message": "Invalid tool arguments", "failed_generation": "text"},
    {"code": "tool_use_failed", "message": "Tool choice is required, but model did not call a tool", "failed_generation": ""},
])
def test_other_bad_requests_remain_provider_errors(body):
    events = []

    def complete(self):
        raise BadRequestError("original", response=SimpleNamespace(status_code=400, headers={}, request=SimpleNamespace()), body=body)

    with pytest.raises(BadRequestError):
        preserve_declined_tool_response(complete, events)(object())
    assert events == []


def test_output_selection_ignores_concurrent_other_model_and_version(tmp_path):
    ours = tmp_path / "ours.json"
    other = tmp_path / "other.json"
    ours.write_text(json.dumps({"artifact_version": "target", "model": "120b"}), encoding="utf-8")
    other.write_text(json.dumps({"artifact_version": "old", "model": "20b"}), encoding="utf-8")
    assert new_evidence_paths(tmp_path, set(), "target", "120b") == {ours}


def test_output_selection_ignores_existing_and_partial_files(tmp_path):
    old = tmp_path / "existing.json"
    partial = tmp_path / "writing.json"
    old.write_text(json.dumps({"artifact_version": "target", "model": "120b"}), encoding="utf-8")
    partial.write_text('{"artifact_version":', encoding="utf-8")
    assert new_evidence_paths(tmp_path, {old}, "target", "120b") == set()
