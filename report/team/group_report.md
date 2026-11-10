# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/analyze_text/` (`tool.py`, `TOOL.md`, `declaration.yaml`); registry `tools/__init__.py`; commit `ac577a8` (tool), `b247ef0` (registry), `21c27f3` (test + báo cáo) trên `NguyenLeTrongManh` (trên `dev`: `1c3be2b`, `bb0628a`, `e553d4b`) | Chức năng mới tự viết (không đổi tên tool có sẵn): gọi LLM trên Groq (`openai/gpt-oss-120b`, đổi được qua `ANALYZE_TEXT_MODEL`) để `summary` / `key_points` / `sentiment` cho text agent đã lấy về từ `fetch`, `paper_text`, `timeline`. Output JSON có cấu trúc; nếu model không trả JSON thì fallback sang text thường. Đã gọi Groq thật thành công: `key_points` và `sentiment=mixed` đúng nội dung. | Dùng chung `GROQ_API_KEY` với provider. Text từ web được bọc trong `<document>` và system prompt cấm làm theo lệnh bên trong; lần chạy thật có chèn "Ignore all previous instructions…", model không làm theo. Text dài hơn 12 000 ký tự bị cắt và báo `truncated`. Read-only, không cần xác nhận. Không bao giờ raise. Declaration chỉ tích hợp vào `tools.yaml` sau baseline. |
| Tool mới 2 (`tools/rank/`) | `starter_v0/tools/rank/` (`tool.py`, `TOOL.md`, `declaration.yaml`, `eval_cases_sample.json`); registry `tools/__init__.py`; commit: `<điền hash>` | Chức năng mới tự viết: **lọc trùng và xếp hạng** item gộp từ nhiều nguồn (`lookup`, `social_search`, `timeline`, `papers`) theo `relevance` / `recency` / `popularity` / `balanced`, giữ top K trước khi `format`. Đọc được ngày tháng của Twitter, ISO (arXiv/GitHub) và RFC 2822; chỉ số tương tác gồm favorites/retweets/views/stars; có trộn thêm `score` của Tavily. Mỗi item kèm `rank_signals` để giải thích vì sao nó được xếp ở vị trí đó. | Chạy cục bộ, không gọi mạng, không cần key, `side_effect: false`. Lọc trùng URL có bỏ `utm_*`/`www`/`#`, nhưng giữ query param thật (`?v=1` ≠ `?v=2`). Không sửa list đầu vào. `items` không phải list thì trả error dict, không raise. |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py` (khối `analyze_text` + `rank`); `pytest` trên `NguyenLeTrongManh`: `97 passed, 0 failed, 14 skipped` (14 skip là stub của tool có sẵn) | 7 hàm test (18 case sau parametrize): happy path (URL/header/model/`response_format`, text bọc trong `<document>`), cắt text dài và `ANALYZE_TEXT_MODEL` không bị `GROQ_MODEL` của agent ghi đè, text xấu (`""`, `"   "`, `None`, `42`, list) không gọi API, `task`/`max_words`/`sentiment` ngoài enum được chuẩn hóa, model trả non-JSON, thiếu key, 429/401/timeout/200 nhưng thiếu `choices`. `rank`: 10 hàm test (17 case): relevance và không gọi mạng, không sửa input, lọc trùng (biến thể URL, query param thật, title có dấu), recency với 3 định dạng ngày và ngày rác, popularity với số dạng chuỗi `"12,000"`, balanced khi không có query, `items` không phải list, list rỗng, phần tử rác, `criteria`/`top_k` sai, relevance thiếu query. | Toàn bộ offline nhờ `fake_http`; `block_network` chặn mọi HTTP thật, không tốn credit Groq. |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: `analyze_text` có 7 hàm test (18 case), `rank` có 10 hàm test (17 case). Với `rank`: model gọi đúng `rank(criteria="recency")` nên eval chấm PASS, nhưng nếu code không đọc được ngày dạng Twitter (`Mon Nov 09 10:00:00 +0000 2026`) thì mọi tweet bị coi như không có ngày và thứ tự sai hoàn toàn. Test `test_rank_recency_parses_twitter_iso_and_rfc_dates_undated_last` bắt đúng lỗi này. Ví dụ lỗi unit test bắt được còn eval thì không: model gọi đúng `analyze_text(text=..., task="sentiment")`, nên eval chấm PASS vì chỉ so tên tool và args. Nhưng nếu Groq trả `"sentiment": "angry"` (ngoài enum) hoặc trả text thường thay vì JSON, UI sẽ hiển thị sai hoặc crash. Hai test `test_analyze_text_bad_task_and_max_words_are_normalised` và `test_analyze_text_non_json_reply_falls_back_to_raw_summary` bắt đúng tầng này: chúng assert cách tool chuẩn hóa response, việc mà eval không bao giờ nhìn thấy. Tương tự, test model env bảo đảm việc đổi `GROQ_MODEL` cho agent không âm thầm đổi model của tool.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
