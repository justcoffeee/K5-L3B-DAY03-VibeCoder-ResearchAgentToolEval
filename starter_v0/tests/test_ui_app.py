"""Regression tests for the Streamlit UI (PR review). Offline: fake provider, mocked HTTP, fake keys."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest

import app as ui_app
import chat
import providers
from conftest import FakeResponse
from providers.base import ModelResponse, ToolCall
from tools import TOOL_FUNCTIONS

ROOT = Path(__file__).resolve().parents[1]

# Built by concatenation so these fake values never look like real keys in the source.
FAKE_SECRETS = {
    "GROQ_API_KEY": "gsk_" + "a1" * 15,
    "TAVILY_API_KEY": "tvly-" + "b2" * 15,
    "FIRECRAWL_API_KEY": "fc-" + "c3" * 15,
    "RAPIDAPI_KEY": "d4" * 20,
    "TELEGRAM_BOT_TOKEN": "123456:" + "e5" * 15,
}
TAVILY_OK = {"results": [{"title": "Tin A", "url": "https://example.com/a", "content": "Nội dung thật"}]}
ANSWER = "Câu trả lời của model"


class FakeProvider:
    default_model = "fake-model"

    def __init__(self) -> None:
        self.script: list[Any] = []
        self.calls = 0

    def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None) -> ModelResponse:
        self.calls += 1
        if not self.script:
            raise RuntimeError("fake provider script exhausted")
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


def tool_call(name: str, **args: Any) -> ModelResponse:
    return ModelResponse(tool_calls=[ToolCall(name, args)])


@pytest.fixture
def ui(monkeypatch, tmp_path):
    fake = FakeProvider()
    monkeypatch.setattr(providers, "make_provider", lambda name: fake)
    monkeypatch.setattr(chat, "ROOT", tmp_path)
    monkeypatch.delenv("UI_MODEL", raising=False)
    # The app installs its send gate in this shared registry; other tests need the real one.
    registry = dict(TOOL_FUNCTIONS)
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not at.exception
    yield SimpleNamespace(at=at, fake=fake, transcripts=tmp_path / "transcripts" / "ui")
    TOOL_FUNCTIONS.clear()
    TOOL_FUNCTIONS.update(registry)


def ask(ui, text: str, *script: Any) -> None:
    ui.fake.script = list(script)
    ui.at.chat_input[0].set_value(text).run()
    assert not ui.at.exception


def turns(ui) -> list[dict[str, Any]]:
    return ui.at.session_state.transcript["turns"]


def history(ui) -> list[str]:
    return [message["content"] for message in ui.at.session_state.history]


def saved_transcript(ui) -> str:
    files = list(ui.transcripts.glob("*.transcript.json"))
    assert len(files) == 1
    return files[0].read_text(encoding="utf-8")


def rendered(ui) -> str:
    kinds = ("error", "warning", "info", "success", "markdown", "text", "json", "expander")
    return "\n".join(str(getattr(element, "proto", element)) for kind in kinds for element in ui.at.get(kind))


def visible_answers(ui) -> list[str]:
    return [element.value for element in ui.at.markdown]


def button_keys(ui) -> list[str]:
    return [button.key for button in ui.at.button if button.key]


def confirm_key(ui) -> str:
    return next(key for key in button_keys(ui) if key.startswith("confirm_send"))


def cancel_key(ui) -> str:
    return next(key for key in button_keys(ui) if key.startswith("cancel_send"))


def has_confirmation(ui) -> bool:
    return any(key.startswith("confirm_send") for key in button_keys(ui))


# ---------------- P1: credentials never reach the transcript or the page ----------------

def assert_no_secret(ui) -> None:
    saved, page = saved_transcript(ui), rendered(ui)
    leaked = [name for name, value in FAKE_SECRETS.items() if value in saved or value in page]
    assert not leaked, f"leaked: {leaked}"


def test_provider_error_with_credentials_is_sanitized(ui, monkeypatch) -> None:
    for name, value in FAKE_SECRETS.items():
        monkeypatch.setenv(name, value)
    ask(ui, "Câu hỏi", RuntimeError("request failed: " + " ".join(FAKE_SECRETS.values())))

    assert turns(ui)[0]["status"] == "provider_error"
    assert_no_secret(ui)


def test_tool_error_with_credentials_is_sanitized(ui, monkeypatch) -> None:
    for name, value in FAKE_SECRETS.items():
        monkeypatch.setenv(name, value)
    message = "failed for url https://api.example.com/bot" + FAKE_SECRETS["TELEGRAM_BOT_TOKEN"] + " " + " ".join(FAKE_SECRETS.values())
    monkeypatch.setitem(TOOL_FUNCTIONS, "lookup", lambda **kw: {"tool": "web_search", "error": "HTTPError", "message": message})
    ask(ui, "Câu hỏi", tool_call("lookup", query="AI"), ModelResponse(text=ANSWER))

    assert_no_secret(ui)
    assert "HTTPError" in rendered(ui)


@pytest.mark.parametrize("name", ["GROQ_API_KEY", "TAVILY_API_KEY", "FIRECRAWL_API_KEY", "TELEGRAM_BOT_TOKEN"])
def test_known_key_shapes_are_removed_without_being_configured(monkeypatch, name: str) -> None:
    monkeypatch.delenv(name, raising=False)
    text = ui_app.sanitize({"error": f"boom {FAKE_SECRETS[name]}"})["error"]
    assert FAKE_SECRETS[name] not in text


def test_sensitive_fields_and_header_values_are_removed() -> None:
    cleaned = ui_app.sanitize({
        "headers": {"Authorization": "abc", "x-api-key": "short"},
        "message": "header x-rapidapi-key: abcdef123456 and Bearer abcdef123456",
    })
    assert cleaned["headers"] == {"Authorization": "<redacted>", "x-api-key": "<redacted>"}
    assert "abcdef123456" not in cleaned["message"]


def test_ordinary_text_is_not_redacted() -> None:
    turn = {"args": {"max_tokens": 100, "query": "fc-barcelona-news task-tracking token economics"}}
    assert ui_app.sanitize(turn) == turn


# ---------------- P2: every send is held for approval ----------------

@pytest.mark.parametrize("args", [{}, {"confirmed": False}, {"confirmed": True}, {"confirmed": "false"}])
def test_send_is_held_for_any_confirmed_value(ui, fake_http, args: dict[str, Any]) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    ask(ui, "Đăng đi", tool_call("send", text="Bản tin *nguyên văn*", **args))

    assert turns(ui)[0]["status"] == "waiting_for_user"
    assert ui.fake.calls == 1, "the loop must stop at the draft"
    assert len(turns(ui)[0]["tool_events"]) == 1
    assert calls == []
    assert "Bản tin *nguyên văn*" in [element.value for element in ui.at.text]
    assert has_confirmation(ui)


def test_confirm_button_posts_the_exact_draft_once(ui, monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", FAKE_SECRETS["TELEGRAM_BOT_TOKEN"])
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100123456789")
    calls = fake_http(FakeResponse({"ok": True}))
    ask(ui, "Đăng đi", tool_call("send", text="Bản tin"))
    ui.at.button(key=confirm_key(ui)).click().run()

    assert not ui.at.exception
    assert len(calls) == 1
    assert calls[0]["json"]["text"] == "Bản tin"
    assert turns(ui)[-1]["tool_events"][0]["result"]["status"] == "sent"
    assert not has_confirmation(ui)
    assert_no_secret(ui)


def test_cancel_button_posts_nothing(ui, fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    ask(ui, "Đăng đi", tool_call("send", text="Bản tin"))
    ui.at.button(key=cancel_key(ui)).click().run()

    assert not ui.at.exception
    assert calls == []
    assert turns(ui)[-1]["assistant_text"].startswith("Đã huỷ")
    assert not has_confirmation(ui)


def test_old_draft_can_no_longer_be_sent_after_a_new_message(ui, fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    ask(ui, "Đăng đi", tool_call("send", text="Nháp cũ"))
    ask(ui, "Thôi hỏi khác", ModelResponse(text="Được."))

    assert not has_confirmation(ui)
    assert calls == []


def test_new_draft_uses_a_different_button_than_the_old_one(ui, fake_http) -> None:
    fake_http(FakeResponse({"ok": True}))
    ask(ui, "Đăng đi", tool_call("send", text="Nháp cũ"))
    old_key = confirm_key(ui)
    ask(ui, "Đăng cái khác", tool_call("send", text="Nháp mới"))

    assert confirm_key(ui) != old_key


@pytest.mark.parametrize("text", ["", "   "])
def test_empty_text_creates_no_draft(ui, fake_http, text: str) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    ask(ui, "Đăng đi", tool_call("send", text=text), ModelResponse(text=ANSWER))

    assert not has_confirmation(ui)
    assert calls == []


# ---------------- P2: only retrieved data counts as a source ----------------

def assert_answer_hidden(ui) -> None:
    assert ANSWER not in visible_answers(ui)
    assert ANSWER not in history(ui)
    assert ui_app.NO_DATA_MESSAGE in [element.value for element in ui.at.error]
    assert turns(ui)[-1]["assistant_text"] == ANSWER, "the transcript keeps the raw answer as evidence"


def test_lookup_error_plus_empty_format_hides_the_answer(ui) -> None:
    ask(
        ui, "Tin AI?",
        ModelResponse(tool_calls=[ToolCall("lookup", {"query": "AI"}), ToolCall("format", {"items": []})]),
        ModelResponse(text=ANSWER),
    )
    assert_answer_hidden(ui)


def test_empty_retrieval_hides_the_answer(ui, monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", FAKE_SECRETS["TAVILY_API_KEY"])
    fake_http(FakeResponse({"results": []}))
    ask(ui, "Tin AI?", tool_call("lookup", query="AI"), ModelResponse(text=ANSWER))
    assert_answer_hidden(ui)


def test_format_alone_is_not_evidence(ui) -> None:
    items = [{"title": "Tin tự chế", "url": "https://example.com/x", "summary": "Không có nguồn"}]
    ask(ui, "Tin AI?", tool_call("format", items=items, template="bullets"), ModelResponse(text=ANSWER))
    assert_answer_hidden(ui)
    assert not any(value.startswith("**Nguồn**") for value in visible_answers(ui))


def test_rank_output_is_not_a_source(ui, monkeypatch) -> None:
    monkeypatch.setitem(TOOL_FUNCTIONS, "rank", lambda **kw: {"tool": "rank", "items": [{"title": "T", "summary": "S"}]})
    ask(ui, "Tin AI?", tool_call("rank", items=[]), ModelResponse(text=ANSWER))
    assert_answer_hidden(ui)


def test_retrieved_data_shows_answer_and_source_link(ui, monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", FAKE_SECRETS["TAVILY_API_KEY"])
    fake_http(FakeResponse(TAVILY_OK))
    ask(ui, "Tin AI?", tool_call("lookup", query="AI"), ModelResponse(text=ANSWER))

    assert ANSWER in visible_answers(ui)
    assert ANSWER in history(ui)
    assert any("[Tin A](https://example.com/a)" in value for value in visible_answers(ui))


# Data retrieved in an earlier turn of the same session can be presented again.

OLD_ITEM = {"title": "Tin A", "url": "https://example.com/a", "summary": "Nội dung thật"}


def lookup_first(ui, monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", FAKE_SECRETS["TAVILY_API_KEY"])
    fake_http(FakeResponse(TAVILY_OK))
    ask(ui, "Tin AI?", tool_call("lookup", query="AI"), ModelResponse(text="Câu trả lời có nguồn"))


def present(ui, *items: Any) -> None:
    ask(ui, "Trình bày thành bullet", tool_call("format", items=list(items), template="bullets"), ModelResponse(text=ANSWER))


def test_formatting_data_from_an_earlier_turn_stays_visible(ui, monkeypatch, fake_http) -> None:
    lookup_first(ui, monkeypatch, fake_http)
    present(ui, OLD_ITEM)

    assert ANSWER in visible_answers(ui)
    assert ANSWER in history(ui)
    assert ui_app.NO_DATA_MESSAGE not in history(ui)
    assert sum("[Tin A](https://example.com/a)" in value for value in visible_answers(ui)) == 2


def test_reworded_summary_of_earlier_data_stays_visible(ui, monkeypatch, fake_http) -> None:
    lookup_first(ui, monkeypatch, fake_http)
    present(ui, {**OLD_ITEM, "url": "https://example.com/a/", "summary": "Nội dung thật được viết lại ngắn gọn"})

    assert ANSWER in visible_answers(ui)


def test_real_url_with_invented_content_is_hidden(ui, monkeypatch, fake_http) -> None:
    lookup_first(ui, monkeypatch, fake_http)
    present(ui, {"title": "Tuyên bố bịa đặt", "url": OLD_ITEM["url"], "summary": "Hoàn toàn khác biệt"})
    assert_answer_hidden(ui)


def test_invented_url_after_a_real_lookup_is_hidden(ui, monkeypatch, fake_http) -> None:
    lookup_first(ui, monkeypatch, fake_http)
    present(ui, {**OLD_ITEM, "url": "https://example.com/invented"})
    assert_answer_hidden(ui)


def test_one_invented_item_among_real_ones_hides_the_answer(ui, monkeypatch, fake_http) -> None:
    lookup_first(ui, monkeypatch, fake_http)
    present(ui, OLD_ITEM, {"title": "Tin B", "url": "https://example.com/b", "summary": "Tự chế"})
    assert_answer_hidden(ui)


def test_earlier_format_output_is_not_evidence(ui) -> None:
    invented = {"title": "Tin tự chế", "url": "https://example.com/x", "summary": "Không có nguồn"}
    ask(ui, "Tin AI?", tool_call("format", items=[invented], template="bullets"), ModelResponse(text="Lần một"))
    present(ui, invented)
    assert_answer_hidden(ui)


def test_rank_of_earlier_data_stays_visible(ui, monkeypatch, fake_http) -> None:
    lookup_first(ui, monkeypatch, fake_http)
    monkeypatch.setitem(TOOL_FUNCTIONS, "rank", lambda **kw: {"tool": "rank", "items": kw["items"]})
    ask(ui, "Xếp hạng tin vừa rồi", tool_call("rank", items=[OLD_ITEM]), ModelResponse(text=ANSWER))

    assert ANSWER in visible_answers(ui)
    assert ANSWER in history(ui)


def test_rank_of_invented_data_after_a_real_lookup_is_hidden(ui, monkeypatch, fake_http) -> None:
    lookup_first(ui, monkeypatch, fake_http)
    invented = {"title": "Tin B", "url": "https://example.com/b", "summary": "Tự chế"}
    monkeypatch.setitem(TOOL_FUNCTIONS, "rank", lambda **kw: {"tool": "rank", "items": kw["items"]})
    ask(ui, "Xếp hạng", tool_call("rank", items=[invented]), ModelResponse(text=ANSWER))
    assert_answer_hidden(ui)


def test_failed_new_lookup_is_not_rescued_by_earlier_data(ui, monkeypatch, fake_http) -> None:
    lookup_first(ui, monkeypatch, fake_http)
    monkeypatch.setitem(TOOL_FUNCTIONS, "lookup", lambda **kw: {"tool": "web_search", "error": "HTTPError", "message": "x"})
    ask(
        ui, "Tin mới hơn?",
        ModelResponse(tool_calls=[ToolCall("lookup", {"query": "AI"}), ToolCall("format", {"items": [OLD_ITEM]})]),
        ModelResponse(text=ANSWER),
    )
    assert_answer_hidden(ui)


def test_new_session_forgets_earlier_data(ui, monkeypatch, fake_http) -> None:
    lookup_first(ui, monkeypatch, fake_http)
    ui.at.sidebar.button[0].click().run()
    assert not ui.at.exception
    assert turns(ui) == []

    present(ui, OLD_ITEM)
    assert_answer_hidden(ui)


def test_clarify_question_stays_visible(ui) -> None:
    ask(ui, "Tóm tắt tweet", tool_call("clarify", question="Tài khoản nào?"))

    assert turns(ui)[0]["status"] == "waiting_for_user"
    assert "Tài khoản nào?" in visible_answers(ui)
    assert "Tài khoản nào?" in history(ui)


def test_capability_answer_without_tools_stays_visible(ui) -> None:
    ask(ui, "Bạn làm được gì?", ModelResponse(text="Mình là research agent."))

    assert "Mình là research agent." in visible_answers(ui)
    assert "Mình là research agent." in history(ui)


# ---------------- P2: partial trace survives a later provider error ----------------

def test_provider_error_after_a_round_keeps_the_trace(ui, monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", FAKE_SECRETS["TAVILY_API_KEY"])
    calls = fake_http(FakeResponse(TAVILY_OK))
    ask(ui, "Tin AI?", tool_call("lookup", query="AI"), RuntimeError("upstream " + FAKE_SECRETS["TAVILY_API_KEY"]))

    saved = json.loads(saved_transcript(ui))["turns"][0]
    assert len(calls) == 1
    assert saved["status"] == "provider_error"
    assert [event["tool"] for event in saved["tool_events"]] == ["lookup"]
    assert saved["tool_events"][0]["args"] == {"query": "AI"}
    assert saved["tool_events"][0]["result"]["items"][0]["url"] == "https://example.com/a"
    assert len(saved["rounds"]) == 1
    assert any("[Tin A](https://example.com/a)" in value for value in visible_answers(ui))
    assert_no_secret(ui)
    assert history(ui) == []


def test_tool_loop_still_works_without_caller_lists() -> None:
    fake = FakeProvider()
    fake.script = [ModelResponse(text="Xong.")]
    result = chat.run_model_tool_loop(provider=fake, messages=[], tools=[], model=None, max_tool_rounds=1)

    assert result["status"] == "answered"
    assert result["rounds"][0]["round"] == 1
    assert result["tool_events"] == []


def test_tool_loop_fills_caller_lists_before_raising() -> None:
    fake = FakeProvider()
    fake.script = [ModelResponse(tool_calls=[ToolCall("format", {"items": []})]), RuntimeError("boom")]
    rounds: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []

    with pytest.raises(RuntimeError):
        chat.run_model_tool_loop(provider=fake, messages=[], tools=[], model=None, max_tool_rounds=2, rounds=rounds, tool_events=events)

    assert len(rounds) == 1
    assert [event["tool"] for event in events] == ["format"]
