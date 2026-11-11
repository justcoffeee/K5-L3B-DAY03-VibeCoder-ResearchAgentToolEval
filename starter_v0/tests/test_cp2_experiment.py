"""Offline checks that provider retry cannot hide scored responses or HTTP 400s."""
from types import SimpleNamespace
import pytest
from openai import BadRequestError, RateLimitError

from scripts.cp2_experiment import make_rate_limit_retry


def provider_error(cls, status, message):
    response = SimpleNamespace(status_code=status, headers={}, request=SimpleNamespace())
    return cls(message, response=response, body=None)


def test_429_retry_preserves_request_and_records_delay(monkeypatch):
    sleeps, calls, events = [], [], []
    monkeypatch.setattr("scripts.cp2_experiment.time.sleep", sleeps.append)
    response = object()
    messages, tools = [{"role": "user", "content": "test"}], [{"type": "function"}]

    def complete(self, *args, **kwargs):
        calls.append((self, args, kwargs))
        if len(calls) == 1:
            raise provider_error(RateLimitError, 429, "Please try again in 7.5s")
        return response

    instance = object()
    actual = make_rate_limit_retry(complete, events, 3)(
        instance, messages, tools, model="test", temperature=0.0, tool_choice="required")
    assert actual is response
    assert len(calls) == 2 and calls[0] == calls[1]
    assert calls[1][1][0] is messages and calls[1][1][1] is tools
    assert sleeps == [10.0]
    assert events[0]["retry"] == 1 and events[0]["delay_seconds"] == 10.0


def test_http_400_is_not_retried(monkeypatch):
    monkeypatch.setattr("scripts.cp2_experiment.time.sleep", lambda _: pytest.fail("must not sleep"))
    calls, events = [], []

    def complete(self):
        calls.append(1)
        raise provider_error(BadRequestError, 400, "model did not call a tool")

    with pytest.raises(BadRequestError):
        make_rate_limit_retry(complete, events, 3)(object())
    assert calls == [1] and events == []


def test_persistent_429_stops_at_retry_budget(monkeypatch):
    sleeps, calls, events = [], [], []
    monkeypatch.setattr("scripts.cp2_experiment.time.sleep", sleeps.append)

    def complete(self):
        calls.append(1)
        raise provider_error(RateLimitError, 429, "rate limited")

    with pytest.raises(RateLimitError):
        make_rate_limit_retry(complete, events, 2)(object())
    assert len(calls) == 3 and len(events) == 2 and sleeps == [30.0, 30.0]


@pytest.mark.parametrize("server_delay", ["3600s", "21m3.6s", "1h2m3s"])
def test_long_quota_wait_is_reported_without_retry(monkeypatch, server_delay):
    monkeypatch.setattr("scripts.cp2_experiment.time.sleep", lambda _: pytest.fail("must not sleep"))
    events = []

    def complete(self):
        raise provider_error(RateLimitError, 429, "Please try again in " + server_delay)

    with pytest.raises(RateLimitError):
        make_rate_limit_retry(complete, events, 3)(object())
    assert events == []
