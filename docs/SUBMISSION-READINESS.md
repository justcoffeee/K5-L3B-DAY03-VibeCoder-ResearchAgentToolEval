# Đối chiếu trước nộp — 11/11/2026

Nền dev `e12df663a6ce773beeffb1fa2561ea33b8a1d00e`; bản bổ sung do justcoffeee yêu cầu, Codex hỗ trợ. Chưa chốt bài nộp/LMS.

| Hạng mục | Bằng chứng / trạng thái |
|---|---|
| C1–C3 baseline và tối ưu | [CP1](CP1-STATUS.md), [CP2](CP2-STATUS.md): v0 45%, v1 75%, v2 70%, v3 80%, integration 90% base20b; giữ nguyên số lịch sử |
| C4 tool/test | analyze_text/rank; 44 test case tool mới; [báo cáo B5a](../report/team/group_report.md) |
| C5 / #14 group cuối | [Run thật](../starter_v0/runs/v4-integration-groq120b_B_group_groq_20261111T103500070067.json): 6/10 PASS, 10 measured; 3 HTTP400 no-tool được giữ text và chấm FAIL, không che lỗi; [verification](../starter_v0/analysis/group_final_verification.json) |
| C6 / #15 public UI | Code và 39 UI tests có; [URL](https://bar-barbara-coated-county.trycloudflare.com) lỗi DNS. Người dùng xác nhận lỗi; người ngoài nhóm thử và smoke public UI còn chờ |
| #16 transcript/B4 | [6 lượt CLI thật](../starter_v0/transcripts/v4-integration-groq120b_groq_20261111T103625141884.transcript.json); scripted inputs bởi Codex, live APIs, X403 được ghi rõ; không gửi Telegram. Public link và mốc trước showdown chưa xác minh |
| C7 báo cáo | B3/B4/B5a/A1 đã bổ sung evidence mới; chưa hoàn chỉnh điều kiện public demo |
| C8 cá nhân / #17 | Có 4 báo cáo và commit kỹ thuật; Huy/Mạnh cần tự hoàn thiện tự đánh giá/giải thích; các thành viên xác nhận thông tin và tự nộp LMS |

**Đổi model đã được người dùng đồng ý:** group/chat dùng `openai/gpt-oss-120b`, nhãn `v4-integration-groq120b`; hash prompt/tools giống v4-integration. 20b cạn quota ngày. Không dùng group120b so với base20b như cùng cấu hình/bộ case. [Profile](../starter_v0/analysis/final_evidence_profile.json).

Full offline suite mới: **175 passed, 14 skipped, 0 failed** ([log](../starter_v0/analysis/submission_final_pytest.txt)). 14 skip là stub starter, không nhận bonus 0 skipped. Prompt, tools, fixed datasets, scorer, agent và version log cũ giữ nguyên.

## Cần người dùng/thành viên bổ sung

1. URL hoạt động và smoke UI trên đúng profile120b; [kịch bản và mẫu kết quả](DEMO-TEST-PLAN.md). Không ghi kế hoạch thành kết quả PASS.
2. Xác nhận người ngoài nhóm thử: người dùng đã nhận bổ sung; chưa có tên/ngày/kết quả thật.
3. Tự đánh giá Huy, phần tự đọc/giải thích Mạnh và các xác nhận cá nhân khác. Không điền thay trải nghiệm.
4. Chốt commit/nhánh, quyền người chấm, deadline/gia hạn và LMS. Không suy từ commit thành đã nộp.

Phần #14 đã hoàn thành kỹ thuật trong bản bổ sung; issue chỉ đóng sau khi evidence được đưa vào dev. #15 và #16 giữ mở vì điều kiện demo chưa đủ. [Biên bản](../starter_v0/analysis/submission_readiness_checks.json).
