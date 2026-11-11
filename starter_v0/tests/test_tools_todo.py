"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import json
import math

import pytest
import requests

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

# ---------------- analyze_text (team tool, Groq) ----------------

analyze_text = TOOL_FUNCTIONS["analyze_text"]


def _groq_reply(content: str, model: str = "openai/gpt-oss-120b") -> FakeResponse:
    return FakeResponse({"model": model, "choices": [{"message": {"role": "assistant", "content": content}}]})


@pytest.fixture
def groq_env(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk-test")
    monkeypatch.delenv("ANALYZE_TEXT_MODEL", raising=False)
    monkeypatch.delenv("GROQ_MODEL", raising=False)


def test_analyze_text_sends_groq_request_and_maps_json_reply(groq_env, fake_http) -> None:
    calls = fake_http(_groq_reply(json.dumps({
        "summary": "Chi phí giảm 40%.", "key_points": ["Giảm chi phí", " ", "Ngữ cảnh 1M token"], "sentiment": "Mixed",
    })))

    result = analyze_text(text="  Bài viết về model mới.  ", task="key_points", focus="chi phí", max_words=80)

    assert len(calls) == 1
    req = calls[0]
    assert req["url"] == "https://api.groq.com/openai/v1/chat/completions"
    assert req["headers"]["Authorization"] == "Bearer gsk-test"
    assert req["json"]["model"] == "openai/gpt-oss-120b"
    assert req["json"]["response_format"] == {"type": "json_object"}
    user_msg = req["json"]["messages"][1]["content"]
    assert "Task: key_points" in user_msg and "at most 80 words" in user_msg and "chi phí" in user_msg
    assert "<document>\nBài viết về model mới.\n</document>" in user_msg  # stripped + wrapped as data
    assert result == {
        "tool": "analyze_text", "task": "key_points", "model": "openai/gpt-oss-120b",
        "summary": "Chi phí giảm 40%.", "key_points": ["Giảm chi phí", "Ngữ cảnh 1M token"], "sentiment": "mixed",
        "parse_ok": True, "truncated": False, "input_chars": len("Bài viết về model mới."),
    }


def test_analyze_text_truncates_long_text_and_uses_its_own_model_env(groq_env, monkeypatch, fake_http) -> None:
    monkeypatch.setenv("GROQ_MODEL", "agent/model")  # agent provider's model must NOT leak into the tool
    monkeypatch.setenv("ANALYZE_TEXT_MODEL", "custom/model")
    calls = fake_http(_groq_reply('{"summary": "ok", "key_points": [], "sentiment": "neutral"}', model="custom/model"))

    result = analyze_text(text="a" * 13000)

    assert calls[0]["json"]["model"] == "custom/model"
    assert "a" * 12000 + "\n</document>" in calls[0]["json"]["messages"][1]["content"]
    assert "a" * 12001 not in calls[0]["json"]["messages"][1]["content"]
    assert result["truncated"] is True and result["input_chars"] == 13000


@pytest.mark.parametrize("bad_text", ["", "   ", None, 42, ["list"]])
def test_analyze_text_empty_or_non_string_text_returns_error_without_request(groq_env, fake_http, bad_text) -> None:
    calls = fake_http(_groq_reply("{}"))

    result = analyze_text(text=bad_text)

    assert result["tool"] == "analyze_text"
    assert result["error"] == "ValueError"
    assert calls == []


@pytest.mark.parametrize("raw_words, expected", [("50", 50), (0, 30), (9999, 500), ("abc", 150), (None, 150)])
def test_analyze_text_bad_task_and_max_words_are_normalised(groq_env, fake_http, raw_words, expected) -> None:
    calls = fake_http(_groq_reply('{"summary": "s", "key_points": [], "sentiment": "angry"}'))

    result = analyze_text(text="nội dung", task="translate", max_words=raw_words)

    assert result["task"] == "summary"
    assert result["sentiment"] is None  # out-of-enum sentiment from the model is dropped
    assert f"at most {expected} words" in calls[0]["json"]["messages"][1]["content"]


def test_analyze_text_non_json_reply_falls_back_to_raw_summary(groq_env, fake_http) -> None:
    fake_http(_groq_reply("Đây là bản tóm tắt dạng text thường."))

    result = analyze_text(text="nội dung")

    assert result["parse_ok"] is False
    assert result["summary"] == "Đây là bản tóm tắt dạng text thường."
    assert result["key_points"] == [] and result["sentiment"] is None


def test_analyze_text_without_key_returns_error_and_no_request(monkeypatch, fake_http) -> None:
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    calls = fake_http(_groq_reply("{}"))

    result = analyze_text(text="nội dung")

    assert result["error"] == "RuntimeError"
    assert "GROQ_API_KEY" in result["message"]
    assert calls == []


@pytest.mark.parametrize("failure, expected_error", [
    (FakeResponse(status_code=429), "HTTPError"),
    (FakeResponse(status_code=401), "HTTPError"),
    (requests.Timeout("read timed out"), "Timeout"),
    (FakeResponse({"error": {"message": "model decommissioned"}}), "KeyError"),  # 200 but no "choices"
])
def test_analyze_text_api_failures_return_error_dict(groq_env, fake_http, failure, expected_error) -> None:
    fake_http(failure)

    result = analyze_text(text="nội dung")

    assert result["tool"] == "analyze_text"
    assert result["error"] == expected_error


# ---------------- rank (team tool, local) ----------------

rank_tool = TOOL_FUNCTIONS["rank"]


def _titles(result) -> list[str]:
    return [item["title"] for item in result["items"]]


def test_rank_relevance_orders_by_query_match_and_adds_rank_fields(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    items = [
        {"title": "Giá vàng hôm nay", "url": "https://a.com/1", "summary": "thị trường vàng"},
        {"title": "GPT-5 ra mắt", "url": "https://b.com/2", "summary": "OpenAI công bố GPT-5"},
        {"title": "Tin công nghệ", "url": "https://c.com/3", "summary": "nhắc tới GPT-5 trong bài"},
    ]

    result = rank_tool(items=items, query="GPT-5", criteria="relevance", top_k=3)

    assert calls == []  # purely local, never touches the network
    assert _titles(result) == ["GPT-5 ra mắt", "Tin công nghệ", "Giá vàng hôm nay"]
    top = result["items"][0]
    assert top["rank"] == 1 and top["url"] == "https://b.com/2" and top["summary"] == "OpenAI công bố GPT-5"
    assert top["rank_signals"]["relevance"] == 1.0
    assert result["items"][2]["rank_signals"]["relevance"] == 0.0
    assert "rank" not in items[0]  # input list is not mutated


def test_rank_dedupes_same_url_variants_and_same_title_without_url() -> None:
    items = [
        {"title": "A", "url": "https://www.example.com/post/?utm_source=x#top"},
        {"title": "A copy", "url": "https://example.com/post"},
        {"title": "Video", "url": "https://youtube.com/watch?v=1"},
        {"title": "Video 2", "url": "https://youtube.com/watch?v=2"},  # real query param -> NOT a duplicate
        {"title": "Tin Nóng  Hôm Nay"},
        {"title": "tin nong hom nay"},  # same title after folding accents/case/spaces
    ]

    result = rank_tool(items=items, top_k=20)

    assert result["dropped_duplicates"] == 2
    assert sorted(_titles(result)) == sorted(["A", "Video", "Video 2", "Tin Nóng  Hôm Nay"])


def test_rank_recency_parses_twitter_iso_and_rfc_dates_undated_last() -> None:
    items = [
        {"title": "no date"},
        {"title": "tweet", "date": "Mon Nov 09 10:00:00 +0000 2026"},
        {"title": "paper", "published": "2026-10-01T00:00:00Z"},
        {"title": "rss", "date": "Tue, 10 Nov 2026 08:00:00 +0000"},
        {"title": "garbage date", "date": "hôm qua"},
    ]

    result = rank_tool(items=items, criteria="recency", top_k=5)

    assert _titles(result) == ["rss", "tweet", "paper", "no date", "garbage date"]
    assert result["items"][0]["rank_signals"]["recency"] == 1.0
    assert result["items"][2]["rank_signals"]["recency"] == 0.1
    assert result["items"][3]["rank_signals"]["recency"] == 0.0


def test_rank_popularity_uses_metrics_and_stars_with_string_counts() -> None:
    items = [
        {"title": "quiet", "metrics": {"favorites": 3, "retweets": 0, "views": None}},
        {"title": "viral", "metrics": {"favorites": "12,000", "retweets": 4000, "views": 900000}},
        {"title": "repo", "stars": 500},
        {"title": "bad metrics", "metrics": "n/a"},
    ]

    result = rank_tool(items=items, criteria="popularity", top_k=4)

    assert _titles(result) == ["viral", "repo", "quiet", "bad metrics"]
    assert result["items"][0]["rank_signals"]["popularity"] == 1.0


def test_rank_balanced_without_query_uses_recency_and_popularity() -> None:
    items = [
        {"title": "old but viral", "date": "2026-01-01", "metrics": {"favorites": 10000}},
        {"title": "new and quiet", "date": "2026-11-10", "metrics": {"favorites": 1}},
        {"title": "new and viral", "date": "2026-11-09", "metrics": {"favorites": 9000}},
    ]

    result = rank_tool(items=items)

    assert result["criteria"] == "balanced"
    assert _titles(result)[0] == "new and viral"


@pytest.mark.parametrize("bad_items", ["GPT-5 news", {"title": "x"}, 42])
def test_rank_non_list_items_returns_error_dict(bad_items) -> None:
    result = rank_tool(items=bad_items)

    assert result["tool"] == "rank"
    assert result["error"] == "ValueError"


@pytest.mark.parametrize("empty", [None, []])
def test_rank_empty_items_returns_empty_result_not_error(empty) -> None:
    result = rank_tool(items=empty)

    assert "error" not in result
    assert result["items"] == [] and result["input_count"] == 0


def test_rank_drops_non_object_entries_and_normalises_bad_args() -> None:
    items = [{"title": f"t{i}", "url": f"https://x.com/{i}"} for i in range(25)] + ["oops", None, 7]

    result = rank_tool(items=items, criteria="hottest", top_k="999")

    assert result["dropped_invalid"] == 3
    assert result["criteria"] == "balanced"
    assert len(result["items"]) == 20  # top_k clamped to the max
    assert any("hottest" in w for w in result["warnings"])
    assert _titles(result)[:3] == ["t0", "t1", "t2"]  # all-tie -> original order kept


@pytest.mark.parametrize("raw_k, expected_len", [(0, 1), (-3, 1), ("2", 2), ("abc", 5), (None, 5)])
def test_rank_top_k_is_coerced(raw_k, expected_len) -> None:
    items = [{"title": f"t{i}", "url": f"https://x.com/{i}"} for i in range(8)]

    assert len(rank_tool(items=items, top_k=raw_k)["items"]) == expected_len


def test_rank_relevance_without_query_falls_back_with_warning() -> None:
    result = rank_tool(items=[{"title": "a"}, {"title": "b"}], criteria="relevance", query="  ")

    assert result["criteria"] == "balanced"
    assert result["warnings"] == ["criteria 'relevance' needs a query, used 'balanced'"]


@pytest.mark.parametrize("bad_count", [
    pytest.param(float("inf"), id="infinity"),
    pytest.param("inf", id="infinity-string"),
    pytest.param(10**400, id="overflowing-integer"),
    pytest.param(float("nan"), id="nan"),
    pytest.param("nan", id="nan-string"),
    pytest.param(-1, id="negative"),
    pytest.param("-3", id="negative-string"),
    pytest.param(True, id="boolean"),
    pytest.param("oops", id="not-a-number"),
])
def test_rank_invalid_engagement_counts_are_zero(bad_count) -> None:
    result = rank_tool(items=[
        {"title": "bad count", "metrics": {"favorites": bad_count}},
        {"title": "valid count", "metrics": {"favorites": 10}},
    ], criteria="popularity")

    assert "error" not in result
    assert _titles(result) == ["valid count", "bad count"]
    for item in result["items"]:
        assert math.isfinite(item["rank_score"])
        assert all(math.isfinite(value) for value in item["rank_signals"].values())
    assert result["items"][1]["rank_signals"]["popularity"] == 0.0
