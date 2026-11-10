# CP1 — Setup và baseline v0

Issue: [#9](https://github.com/justcoffeee/K5-L3B-DAY03-VibeCoder-ResearchAgentToolEval/issues/9).
Người phụ trách: Phạm Hoàng Huy (justcoffeee). Nhánh làm việc: phamhoanghuy.

## Kết quả

- Đã điền đủ 4 tài khoản và phân công trong TEAM.md, giữ nguyên thông tin cá nhân người dùng cung cấp.
- Có quy trình nhánh cá nhân → PR vào dev; Python 3.14.8, dependency đã cài, pip check pass.
- Cấu hình key mới trong .env cục bộ; .env/.venv được gitignore, không đưa key vào evidence.
- Groq adapter dùng SDK sẵn có; preflight pass với openai/gpt-oss-20b.
- Pytest: **64 passed, 17 skipped, 0 failed** (55 contract + 7 example + 2 Groq).
- Prompt, tool declaration, eval base và extension nguyên bản khi đo v0.
- Baseline: **20 measured / 20 total, 0 provider errors, 9 passed**.

| Metric | Giá trị |
|---|---:|
| case_accuracy | 0.45 |
| tool_routing_accuracy | 0.70 |
| argument_accuracy | 0.45 |
| multiturn_accuracy | 0.3333 |

Artifact version: `v0+peb1c8179815b+te69bc53ed884`.
version_log.csv đã có dòng v0, B1/B2 đã ghi đủ 11 case FAIL và giả thuyết nguyên nhân.
Không sửa metric/query/case để làm đẹp kết quả. v1–v3 chưa thực hiện.

## Evidence

- [Run v0](../starter_v0/runs/v0_B_base_groq_20261110T175003235889.json).
- [Version log](../starter_v0/artifacts/version_log.csv).
- [Phân tích 11 case fail và 7 tool errors](../starter_v0/analysis/cp1_baseline_analysis.json).
- [Pytest output](../starter_v0/analysis/cp1_pytest.txt).
- [Preflight Groq thành công](../starter_v0/analysis/cp1_groq_preflight_gpt_oss_20b.txt).
- [Tool smoke](../starter_v0/analysis/cp1_tool_smoke.json).
- [Môi trường/hash](../starter_v0/analysis/cp1_environment.json).
- Log lỗi lịch sử: [OpenRouter thiếu key](../starter_v0/analysis/cp1_preflight.txt),
  [Llama model 404](../starter_v0/analysis/cp1_groq_preflight.txt).

## Giới hạn cần xử lý

**Cập nhật sau khi đăng ký gói free Twitter API45:** timeline và search đều HTTP 200,
qua TOOL_FUNCTIONS trả đúng 1 item khi limit=1, không có error.
Header quota lần kiểm tra endpoint thứ hai: còn 998/1000 request (trước 2 lần gọi tool xác minh tiếp theo).
Xem [retest subscription](../starter_v0/analysis/cp1_rapidapi_subscription_retest.json).
Lỗi quyền truy cập RapidAPI đã được khắc phục ở lần retest; vẫn giữ nguyên run v0 và metric cũ
để thể hiện đúng điều kiện lúc đo. Không suy ra metric của một lần eval chưa chạy.

Baseline **hợp lệ để đo routing/arguments theo rubric**, chưa chứng minh toàn bộ tool live hoạt động.
Tavily và Firecrawl smoke pass; RapidAPI timeline 403, social_search 429 ở smoke và 403 trong run.
Có 7 tool_errors RapidAPI dù provider_error_cases=0. Kiểm tra subscription/quota/quyền Twitter API45;
chưa có bằng chứng để khẳng định nguyên nhân cụ thể. Không tự mua gói API hoặc đổi tool khi đo v0.

Các URL cố định R04/R11/M04 trả nội dung trang 404; không đổi case để né lỗi.
R14 gọi send sai mục đích, nhưng code guard trả needs_confirmation; không gửi Telegram.
R03/M02/M06 dùng đúng tool, nhưng query khác exact-match expectation; cần review ngữ nghĩa riêng.
Thông tin họ tên, MSSV, email và GitHub của cả 4 thành viên đã được bổ sung trong TEAM.md từ dữ liệu nhóm trưởng cung cấp. Nhánh nộp/commit chốt sẽ được ghi ở bước chốt bài CP5.

## Bàn giao

Có thể dùng run v0 này làm mốc so sánh cho issue #10: mỗi vòng một giả thuyết, cùng Groq/model.
Ưu tiên khảo sát hỏi lại khi thiếu thông tin, boundary hành động, ưu tiên correction mới nhất;
không sửa đồng thời nhiều giả thuyết rồi gọi là một version. Phối hợp TV2 khi tích hợp tool mới.
RapidAPI đã pass retest; thông tin cá nhân 4 thành viên đã đủ trong TEAM.md. Các URL 404 của case cố định vẫn là giới hạn được ghi nhận, không sửa case để né lỗi.
Chỉ đóng #9 khi đã kiểm tra đầy đủ checklist, thông tin nhóm và giới hạn live được nhóm chấp nhận/xử lý.
