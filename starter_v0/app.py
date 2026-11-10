"""Streamlit UI for the Research Agent. Run from starter_v0/: streamlit run app.py

Uses the same model/tool loop and transcript format as chat.py. Tool errors are
shown to the user on purpose, so a failing tool is never hidden behind a nice answer.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

import chat
from chat import ARTIFACTS_DIR, now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from tools.send.tool import send_telegram
from versioning import artifact_version_dict, build_artifact_version


LOGO_PATH = Path(__file__).resolve().parent / "assets" / "vinuni_logo.png"
PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama", "groq"]
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4
TELEGRAM_TOKEN_IN_URL = re.compile(r"bot\d+:[A-Za-z0-9_-]+")
NO_DATA_MESSAGE = "Không có dữ liệu thật vì mọi tool đều lỗi, nên câu trả lời của model đã bị ẩn để tránh thông tin không có nguồn."
SEND_HOLD_STATUS = "awaiting_ui_confirmation"
SEND_QUESTION = "Bạn kiểm tra nguyên văn nội dung bên dưới rồi bấm xác nhận để gửi lên Telegram."
SAMPLE_QUESTIONS = [
    "Tin tức AI hôm nay có gì nổi bật?",
    "Tweet mới nhất của Sam Altman là gì?",
    "Tóm tắt bài này giúp mình: https://openai.com/research/",
    "Tóm tắt 5 tweet mới nhất giúp mình",
]
PAGE_STYLE = """
<style>
.hero {
  position: relative; overflow: hidden; color: #FFFFFF;
  padding: 1.5rem 1.75rem 1.5rem 3.5rem; margin-bottom: 1.25rem;
  background:
    repeating-linear-gradient(45deg, rgba(255,255,255,.05) 0 2px, transparent 2px 12px),
    linear-gradient(135deg, #123A7C, #1F5AA8);
}
.hero::before {
  content: ""; position: absolute; left: 0; top: 0;
  border-top: 56px solid #D7282F; border-right: 40px solid transparent;
}
.hero .title { font-size: 1.9rem; font-weight: 800; line-height: 1.2; }
.hero .subtitle { margin-top: .35rem; font-size: .95rem; opacity: .9; }
.hero .note { margin-top: .5rem; font-size: .8rem; opacity: .75; }
[data-testid="stSidebar"] { border-top: 4px solid #D7282F; }
/* The logo has a white background, so multiply blends it into the sidebar color. */
[data-testid="stSidebarLogo"], [data-testid="stHeaderLogo"] { height: 3rem; mix-blend-mode: multiply; }
.stButton > button { border-radius: 2px; }
</style>
<div class="hero">
  <div class="title">Research Agent</div>
  <div class="subtitle">Mỗi lượt hiển thị đủ tool đã gọi, arguments, nguồn và kết quả thật, kể cả khi tool lỗi.</div>
  <div class="note">Dự án lab của học viên</div>
</div>
"""


def hold_send(text: str = "", confirmed: Any = False) -> dict[str, Any]:
    """Stop the agent loop before posting, so the user approves the exact text in the UI."""
    if not confirmed:
        return send_telegram(text=text, confirmed=False)
    return {
        "tool": "send_telegram",
        "status": SEND_HOLD_STATUS,
        "text": text,
        "awaiting_user": True,
        "question": SEND_QUESTION,
    }


def install_send_gate() -> None:
    # Matched by function name so the gate still applies if the team renames the tool.
    for name, func in list(TOOL_FUNCTIONS.items()):
        if func.__name__ in {"send_telegram", "hold_send"}:
            TOOL_FUNCTIONS[name] = hold_send


def redact(turn: dict[str, Any]) -> dict[str, Any]:
    """Remove Telegram bot tokens, which appear in the URL of HTTP error messages."""
    text = json.dumps(turn, ensure_ascii=False, default=str)
    return json.loads(TELEGRAM_TOKEN_IN_URL.sub("bot<redacted>", text))


def tool_failed(event: dict[str, Any]) -> bool:
    result = event.get("result")
    return isinstance(result, dict) and bool(result.get("error"))


def all_tools_failed(turn: dict[str, Any]) -> bool:
    events = turn["tool_events"]
    return bool(events) and all(tool_failed(event) for event in events)


def pending_send(turns: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Only the latest turn can be approved, so an old draft cannot be sent later."""
    for event in (turns[-1]["tool_events"] if turns else []):
        result = event.get("result")
        if isinstance(result, dict) and result.get("status") == SEND_HOLD_STATUS:
            return event
    return None


def start_session(provider_name: str, model: str | None, version: str) -> None:
    """Read the artifacts from disk and start an empty conversation."""
    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    provider = make_provider(provider_name)
    artifact_version = build_artifact_version(version, prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join(["ui", safe_slug(version), safe_slug(provider_name), timestamp])

    st.session_state.provider = provider
    st.session_state.model = model
    st.session_state.system_prompt = prompt_path.read_text(encoding="utf-8")
    st.session_state.openai_tools = to_openai_tools(load_tool_declarations(tools_path))
    st.session_state.artifact_version = artifact_version.artifact_version
    st.session_state.history = []
    # Sessions from a public link stay out of transcripts/*.json until the team reviews them.
    st.session_state.transcript_path = chat.ROOT / "transcripts" / "ui" / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model or getattr(provider, "default_model", None),
        "system_prompt": str(prompt_path),
        "tools": str(tools_path),
        "history_window": HISTORY_WINDOW,
        "max_tool_rounds": MAX_TOOL_ROUNDS,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def save_turn(turn: dict[str, Any]) -> dict[str, Any]:
    turn = redact(turn)
    st.session_state.transcript["turns"].append(turn)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
    return turn


def run_turn(user_text: str) -> None:
    state = st.session_state
    turn: dict[str, Any] = {
        "turn_index": len(state.transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    messages = [
        {"role": "system", "content": state.system_prompt},
        *trim_history(state.history, HISTORY_WINDOW),
        {"role": "user", "content": user_text},
    ]
    try:
        turn.update(run_model_tool_loop(
            provider=state.provider,
            messages=messages,
            tools=state.openai_tools,
            model=state.model,
            max_tool_rounds=MAX_TOOL_ROUNDS,
        ))
    except Exception as exc:
        turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
    turn["ended_at"] = now_iso()

    turn = save_turn(turn)
    if turn["status"] != "provider_error":
        # An answer written without any tool data must not become context for later turns.
        answer = NO_DATA_MESSAGE if all_tools_failed(turn) else turn["assistant_text"]
        state.history.append({"role": "user", "content": user_text})
        state.history.append({"role": "assistant", "content": answer})


def resolve_send(event: dict[str, Any], approved: bool) -> None:
    """Post the held text after the button click, or drop it."""
    text = event["result"]["text"]
    started_at = now_iso()
    events: list[dict[str, Any]] = []
    if approved:
        result = send_telegram(text=text, confirmed=True)
        events.append({"tool": event["tool"], "args": {"text": text, "confirmed": True}, "result": result})
        reply = "Đã gửi lên Telegram." if result.get("status") == "sent" else "Gửi thất bại, nội dung chưa được đăng."
    else:
        reply = "Đã huỷ, chưa gửi nội dung nào."
    user_text = "[Nút trên UI] Xác nhận gửi" if approved else "[Nút trên UI] Huỷ gửi"
    state = st.session_state
    turn = save_turn({
        "turn_index": len(state.transcript["turns"]) + 1,
        "started_at": started_at,
        "user": user_text,
        "status": "ui_action",
        "assistant_text": reply,
        "rounds": [],
        "tool_events": events,
        "ended_at": now_iso(),
    })
    state.history.append({"role": "user", "content": user_text})
    state.history.append({"role": "assistant", "content": turn["assistant_text"]})


def source_lines(turn: dict[str, Any]) -> list[str]:
    lines: dict[str, str] = {}
    for event in turn["tool_events"]:
        result = event.get("result")
        if not isinstance(result, dict) or tool_failed(event):
            continue
        for item in result.get("items") or []:
            url = str(item.get("url") or "")
            if url.startswith(("http://", "https://")):
                title = re.sub(r"[\[\]]", "", str(item.get("title") or url))[:100]
                lines.setdefault(url, f"- [{title}]({url}) · {item.get('source') or ''}")
        for hit in result.get("results") or []:
            label = f"{hit.get('title')} › {hit.get('section')}"
            lines.setdefault(label, f"- {label} · hiệu lực {hit.get('effective_date')}")
    return list(lines.values())


def render_tool_event(event: dict[str, Any]) -> None:
    result = event.get("result")
    result = result if isinstance(result, dict) else {}
    failed = tool_failed(event)
    args = json.dumps(event.get("args", {}), ensure_ascii=False, sort_keys=True)
    with st.expander(f"🔧 {event.get('tool')}({args})", expanded=failed):
        st.json(result)
    if failed:
        st.error(f"Tool `{event.get('tool')}` lỗi: {result['error']}: {result.get('message', '')}")
    elif result.get("status") == "needs_confirmation":
        st.warning("Tin chưa được gửi vì chưa có xác nhận.")
    elif result.get("status") == "sent":
        st.success("Đã gửi lên Telegram.")


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        for event in turn["tool_events"]:
            render_tool_event(event)
        if turn["status"] == "provider_error":
            st.error(f"Lỗi provider: {turn['error']}")
            return
        if turn["status"] == "ui_action":
            st.markdown(turn["assistant_text"])
            return
        if all_tools_failed(turn):
            st.error(NO_DATA_MESSAGE)
            return
        if any(tool_failed(event) for event in turn["tool_events"]):
            st.warning("Một số tool bị lỗi, câu trả lời dưới đây có thể thiếu hoặc không đầy đủ nguồn.")
        if turn["status"] == "max_tool_rounds":
            st.warning(f"Agent dừng vì đã dùng hết {MAX_TOOL_ROUNDS} vòng gọi tool.")
        if turn["status"] == "waiting_for_user":
            st.info("Agent đang chờ bạn trả lời.")
        st.markdown(turn["assistant_text"])
        sources = source_lines(turn)
        if sources:
            st.markdown("**Nguồn**\n" + "\n".join(sources))


def render_send_confirmation(event: dict[str, Any]) -> None:
    with st.container(border=True):
        st.markdown("**Nội dung sẽ gửi lên Telegram**")
        st.text(event["result"]["text"])
        confirm, cancel = st.columns(2)
        if confirm.button("Gửi đúng nội dung này", key="confirm_send", type="primary", use_container_width=True):
            resolve_send(event, approved=True)
            st.rerun()
        if cancel.button("Huỷ", key="cancel_send", use_container_width=True):
            resolve_send(event, approved=False)
            st.rerun()


def render_samples() -> str | None:
    st.markdown("**Thử nhanh**")
    columns = st.columns(2)
    for index, question in enumerate(SAMPLE_QUESTIONS):
        if columns[index % 2].button(question, key=f"sample_{index}", use_container_width=True):
            return question
    return None


def main() -> None:
    st.set_page_config(page_title="Research Agent", page_icon="🔎")
    st.logo(str(LOGO_PATH))
    install_send_gate()
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.sidebar:
        provider_name = st.selectbox("Provider", PROVIDERS)
        model = st.text_input("Model", value=os.getenv("UI_MODEL", ""), placeholder="Để trống: model mặc định của provider").strip() or None
        version = st.text_input("Version", value="dev", help="Đặt đúng nhãn, ví dụ v3, khi ghi transcript nộp bài.").strip() or "dev"
        new_session = st.button("Phiên mới", help="Xoá hội thoại và đọc lại prompt, tools từ file.")

    config = (provider_name, model, version)
    if new_session or st.session_state.get("config") != config:
        st.session_state.config = config
        start_session(provider_name, model, version)

    turns = st.session_state.transcript["turns"]
    with st.sidebar:
        st.caption(f"Artifact: `{st.session_state.artifact_version}`")
        if turns:
            st.caption(f"Transcript: `{st.session_state.transcript_path.name}`")

    for turn in turns:
        render_turn(turn)
    held = pending_send(turns)
    if held:
        render_send_confirmation(held)

    sample = render_samples() if not turns else None
    typed = st.chat_input("Nhập yêu cầu research...")
    user_text = (sample or typed or "").strip()
    if user_text:
        with st.chat_message("user"):
            st.markdown(user_text)
        with st.chat_message("assistant"), st.spinner("Agent đang xử lý..."):
            run_turn(user_text)
        st.rerun()


main()
