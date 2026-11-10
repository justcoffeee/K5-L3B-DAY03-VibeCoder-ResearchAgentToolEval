from types import SimpleNamespace

import openai
import pytest

from providers import make_provider


@pytest.mark.parametrize(
    ("raw_args", "expected_args"),
    [
        ('{"query": "agent eval"}', {"query": "agent eval"}),
        ('{"query":', {"_invalid_json_arguments": '{"query":'}),
    ],
)
def test_groq_routes_to_its_endpoint_and_preserves_tool_calls(
    monkeypatch, raw_args, expected_args
):
    """Exercise the SDK boundary offline, including malformed model arguments."""
    monkeypatch.setenv("GROQ_API_KEY", "offline-test-key")
    recorded = {}

    def complete(**kwargs):
        recorded["request"] = kwargs
        call = SimpleNamespace(
            function=SimpleNamespace(name="lookup", arguments=raw_args)
        )
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=None, tool_calls=[call]))]
        )

    def client(**kwargs):
        recorded["client"] = kwargs
        return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=complete)))

    monkeypatch.setattr(openai, "OpenAI", client)
    provider = make_provider("groq")
    response = provider.complete(
        [{"role": "user", "content": "Find agent eval research"}],
        [{"type": "function", "function": {"name": "lookup"}}],
        model="explicit-test-model",
        tool_choice="required",
    )

    assert recorded["client"] == {
        "api_key": "offline-test-key",
        "base_url": "https://api.groq.com/openai/v1",
    }
    assert recorded["request"]["model"] == "explicit-test-model"
    assert recorded["request"]["tool_choice"] == "required"
    assert recorded["request"]["tools"][0]["function"]["name"] == "lookup"
    assert response.tool_calls[0].name == "lookup"
    assert response.tool_calls[0].args == expected_args
