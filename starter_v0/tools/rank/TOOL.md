---
name: rank
track: bonus
kind: local_formatter
provider: none (local scoring)
requires_env: []
inputs: [items, query, criteria, top_k]
outputs: [items, dropped_duplicates, dropped_invalid, warnings]
side_effect: false
---
# rank

**Lọc trùng và xếp hạng** các item agent đã thu thập từ nhiều nguồn (`lookup`, `social_search`,
`timeline`, `papers`, `fetch`…), rồi giữ lại top K. Chạy cục bộ, không gọi mạng, không cần key.
Tool do nhóm tự viết (CP3).

- **Dùng khi:** đã có danh sách item (thường gộp từ ≥ 2 nguồn hoặc nhiều hơn số user cần), và user muốn
  "top 5 tin quan trọng nhất", "bài mới nhất trước", "tweet nhiều tương tác nhất". Thường gọi **trước** `format`.
- **Không dùng khi:** chưa có item (phải tìm trước); chỉ có 1–2 item; hoặc user chỉ muốn trình bày
  (dùng `format`). Tool không tóm tắt nội dung (việc đó là của `analyze_text`).

## Args

| arg | type | ghi chú |
|---|---|---|
| `items` | array of object, bắt buộc | item lấy từ tool khác; không phải list → error dict; phần tử không phải object bị bỏ (`dropped_invalid`) |
| `query` | string | câu hỏi/chủ đề của user, dùng để tính relevance |
| `criteria` | `balanced` \| `relevance` \| `recency` \| `popularity` | ngoài enum → `balanced` kèm `warnings`; `relevance` mà không có `query` → `balanced` |
| `top_k` | int | ép về khoảng [1, 20]; giá trị lỗi → 5 |

## Cách chấm điểm

Mỗi item có 3 tín hiệu, mỗi tín hiệu nằm trong [0, 1]:

| Tín hiệu | Cách tính |
|---|---|
| `relevance` | Tỉ lệ từ khóa của `query` xuất hiện trong `title`/`summary` (khớp ở title được cộng thêm, có bỏ dấu tiếng Việt); nếu item có `score` của Tavily thì trộn thêm 30% |
| `recency` | Đọc `date` / `published` / `updated_at` / `updated` (ISO, RFC 2822, format của Twitter). Item mới nhất được 1.0, cũ nhất 0.1, không có ngày 0 |
| `popularity` | `log(1 + favorites + likes + 2·retweets + views/100 + stars + points)`, chuẩn hóa min-max; giá trị không phải số hữu hạn dương (`inf`, `nan`, số âm, số quá lớn, chuỗi lạ) tính là 0 |

Trọng số: `balanced` = 0.5 relevance + 0.25 recency + 0.25 popularity (không có query thì 0.5 recency +
0.5 popularity). Các criteria còn lại = 100% tín hiệu tương ứng. Nếu điểm bằng nhau thì giữ thứ tự ban đầu.

**Lọc trùng:** cùng URL sau khi bỏ `www.`, `/` cuối, `#fragment` và các tham số `utm_*`. Item không có URL
thì so theo title (bỏ dấu, bỏ khoảng trắng thừa). Giữ lại item xuất hiện đầu tiên.

## Output

```json
{"tool": "rank", "query": "gpt-5", "criteria": "balanced", "input_count": 8,
 "dropped_invalid": 0, "dropped_duplicates": 2, "warnings": [],
 "items": [{"title": "...", "url": "...", "source": "...", "summary": "...",
            "rank": 1, "rank_score": 0.83,
            "rank_signals": {"relevance": 1.0, "recency": 0.9, "popularity": 0.42}}]}
```

Item giữ nguyên mọi field gốc và được thêm `rank`, `rank_score`, `rank_signals`. Vì vậy có thể đưa thẳng
`items` vào `format`. Tool không sửa list đầu vào.

## Error contract

Không bao giờ raise. Lỗi trả về `{"tool": "rank", "error": "<ExceptionName>", "message": "..."}`:

| Tình huống | Kết quả |
|---|---|
| `items` không phải list (string, dict, số) | `ValueError` |
| `items` là `None` hoặc `[]` | Không lỗi: `items: []` |
| Phần tử không phải object, `criteria`/`top_k` sai | Không lỗi: tự chuẩn hóa, ghi vào `dropped_invalid` / `warnings` |

## Bàn giao

- **Nhóm trưởng:** khối trong `declaration.yaml` đã được dán vào cuối `artifacts/tools.yaml`
  (`tools_hash` `e69bc53ed884` → `54ed7f4a1216`) và `pytest tests/test_tool_contract.py` xanh. Còn lại:
  review, chạy eval và ghi thành một version riêng trong `version_log.csv` để đo ảnh hưởng tới routing.
  Gợi ý thêm rule vào prompt: "gộp từ nhiều nguồn hoặc user hỏi top/mới nhất/nổi bật nhất → `rank` trước
  rồi mới `format`". Từ giờ `tools.yaml` mới là bản đang dùng và có thể được tinh chỉnh; `declaration.yaml`
  đã được đồng bộ schema item/metrics sau review PR #28. Mọi object có properties để tương thích Gemini.
- **TV3 (eval):** case mẫu trong `eval_cases_sample.json`.
- **TV4 (UI):** hiển thị `items` theo `rank`, có thể thêm badge `rank_score` và tooltip `rank_signals`.
  Nếu `dropped_duplicates > 0` thì ghi chú "đã gộp N kết quả trùng". `warnings` có nội dung thì hiển thị nhỏ.
