---
name: analyze_text
track: bonus
kind: live_api
provider: Groq (OpenAI-compatible chat completions)
requires_env: [GROQ_API_KEY]
inputs: [text, task, focus, language, max_words]
outputs: [summary, key_points, sentiment]
side_effect: false
---
# analyze_text

Dùng LLM chạy trên Groq để **tóm tắt**, **trích ý chính** hoặc **đánh giá sentiment** của một
đoạn text mà agent **đã có sẵn**. Tool do nhóm tự viết (CP3).

- **Dùng khi:** đã lấy được nội dung (từ `fetch`, `paper_text`, `timeline`, `social_search`…) và
  user muốn "tóm tắt bài này", "rút 5 ý chính", "dư luận tích cực hay tiêu cực".
- **Không dùng khi:** chưa có text. Tool **không tự tìm kiếm** hay đọc URL, nên phải gọi
  `fetch`/`lookup`/`timeline` trước. Không dùng để trình bày nhiều item thành bản tin (việc đó là của `format`).

## Args

| arg | type | ghi chú |
|---|---|---|
| `text` | string, bắt buộc | nội dung cần phân tích; rỗng → error dict, không gọi API; > 12 000 ký tự → cắt bớt, `truncated=true` |
| `task` | `summary` \| `key_points` \| `sentiment` | ngoài enum → `summary` |
| `focus` | string | khía cạnh cần chú ý (vd: "chi phí", "rủi ro bảo mật") |
| `language` | string | ngôn ngữ của output, mặc định `vi` |
| `max_words` | int | độ dài tối đa của summary, ép về khoảng [30, 500]; giá trị lỗi → 150 |

## Output

```json
{"tool": "analyze_text", "task": "summary", "model": "openai/gpt-oss-120b",
 "summary": "...", "key_points": ["...", "..."], "sentiment": "positive",
 "parse_ok": true, "truncated": false, "input_chars": 5321}
```

`sentiment` có thể là `null` khi model trả giá trị lạ. `parse_ok=false` nghĩa là model không trả
JSON hợp lệ; khi đó toàn bộ text model trả về được đặt vào `summary`.

## Error contract

Không bao giờ raise. Mọi lỗi trả về `{"tool": "analyze_text", "error": "<ExceptionName>", "message": "..."}`:

| Tình huống | `error` | Có gọi API? |
|---|---|---|
| `text` rỗng / không phải string | `ValueError` | Không |
| Thiếu `GROQ_API_KEY` | `RuntimeError` | Không |
| HTTP 401 (key sai), 429 (rate limit), 5xx | `HTTPError` | Có |
| Timeout / mất mạng | `Timeout` / `ConnectionError` | Có |

## An toàn (prompt injection)

Text cần phân tích thường lấy từ web, nên có thể chứa câu kiểu "ignore previous instructions…".
Tool bọc text trong thẻ `<document>`, và system prompt yêu cầu coi nội dung trong thẻ chỉ là dữ liệu,
không làm theo lệnh nằm bên trong. Tool chỉ đọc, `side_effect: false`.

## Env

- `GROQ_API_KEY` (bắt buộc): tạo tại https://console.groq.com/keys (free tier).
- `ANALYZE_TEXT_MODEL` (tùy chọn): mặc định `openai/gpt-oss-120b`. Biến này tách riêng với
  `GROQ_MODEL` (biến chọn model cho agent khi chạy `--provider groq`), nên đổi model của agent
  không ảnh hưởng tới tool. Groq hay ngừng hỗ trợ model cũ (vd `llama-3.3-70b-versatile` đã ngừng
  từ 16/08/2026), nên khi gặp lỗi 400/404 thì xem https://console.groq.com/docs/models rồi đổi biến này.
- `GROQ_API_KEY` dùng chung với provider Groq của agent, chỉ cần một key.

## Bàn giao

- **Nhóm trưởng (sau baseline W01):** dán khối trong `declaration.yaml` vào cuối `artifacts/tools.yaml`,
  chạy `pytest tests/test_tool_contract.py`. Gợi ý thêm rule vào prompt: "đã có nội dung và user muốn
  tóm tắt/ý chính/sentiment → `analyze_text`; chưa có nội dung thì lấy trước".
- **TV3 (eval):** case mẫu trong `eval_cases_sample.json`.
- **TV4 (UI):** có `error` thì hiển thị `message`. Không có lỗi thì hiển thị `summary`, `key_points`
  dạng bullet, và `sentiment` dạng badge (bỏ qua nếu `null`). Thêm ghi chú nhỏ nếu `truncated=true`.
