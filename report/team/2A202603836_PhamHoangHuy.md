# Báo cáo cá nhân — Phạm Hoàng Huy — 2A202603836

## 1. Thông tin thành viên

- Họ tên: Phạm Hoàng Huy
- MSSV: 2A202603836
- GitHub: justcoffeee
- Email: huyclaynun@gmail.com

## 2. Phần việc phụ trách

- Nhóm trưởng: issue #9 (setup/baseline), #10 (tối ưu v1–v3), #17 (tích hợp/báo cáo/chốt bài).

## 3. Đóng góp cụ thể

- Đã hoàn thành CP1 với hỗ trợ Codex: bổ sung phân công, quy trình phát triển, tạo môi trường và .env cục bộ, chạy kiểm thử offline và preflight.
- Bổ sung adapter Groq theo lựa chọn của nhóm, giữ nguyên artifact baseline.
- Đã chạy preflight Groq và baseline v0 bằng openai/gpt-oss-20b: 9/20 case PASS (45%), routing 70%, arguments 45%, multiturn 33,33%; 0 lỗi provider.
- Ghi version_log.csv, phân tích đủ 11 case FAIL trong B2; tách 7 lỗi tool RapidAPI khỏi metric model. Các vòng chạy lại v1–v3 đạt 75% → 70% → 80%; kế hoạch, snapshot và lượt lỗi đều được lưu. Hoàn thiện prompt nhiều bước và đo lại bản tích hợp với hỗ trợ Codex; [CP2 status](../../docs/CP2-STATUS.md).
- Xác minh lại RapidAPI sau đăng ký gói free: hai endpoint HTTP 200, hai tool registry đều trả 1 item, không lỗi; giữ nguyên baseline cũ.
- Hoàn thiện #10 với hỗ trợ Codex: v4-integration 18/20 (90%), 0 lỗi provider, 7 lỗi RapidAPI; full offline suite 164 passed, 14 skipped. Tích hợp 12 declaration với schema upstream, khóa hash/runtime, cung cấp lệnh/handoff cho TV3/TV4.

## 4. Bằng chứng

- [TEAM.md](../../TEAM.md), [quy trình](../../docs/TEAM-WORKFLOW.md), [trạng thái CP1](../../docs/CP1-STATUS.md).
- [Pytest CP1 (lịch sử)](../../starter_v0/analysis/cp1_pytest.txt): 64 passed, 17 skipped, 0 failed; kết quả CP2 nằm trong mục test cuối bên dưới.
- [Preflight Groq](../../starter_v0/analysis/cp1_groq_preflight_gpt_oss_20b.txt): pass.
- [Run v0](../../starter_v0/runs/v0_B_base_groq_20261110T175003235889.json), [analysis](../../starter_v0/analysis/cp1_baseline_analysis.json), [version log](../../starter_v0/artifacts/version_log.csv).
- [CP2 status](../../docs/CP2-STATUS.md), [handoff](../../docs/CP2-HANDOFF.md), [test cuối](../../starter_v0/analysis/cp2_pytest_final.txt), [verifier](../../starter_v0/analysis/cp2_verification.txt).
- AI/công cụ hỗ trợ: Codex, Git, Python/pip, pytest.
- Kiểm tra bằng công cụ: chạy test offline, kiểm tra diff prompt/tools/eval, kiểm tra gitignore .env/.venv.
- Commit/PR: CP1 xem [trạng thái và bằng chứng](../../docs/CP1-STATUS.md); CP2 có commit [a993a7e](https://github.com/justcoffeee/K5-L3B-DAY03-VibeCoder-ResearchAgentToolEval/commit/a993a7ec5744daf8ad6c5f148a80b2afaf2008d4), đã tích hợp vào `dev` qua [PR #30](https://github.com/justcoffeee/K5-L3B-DAY03-VibeCoder-ResearchAgentToolEval/pull/30).

## 5. Tự đánh giá

Chờ thành viên tự viết; không suy đoán hoặc điền thay trải nghiệm cá nhân.

## Bổ sung theo yêu cầu justcoffeee — 11/11/2026

justcoffeee yêu cầu hoàn thiện #14–#16, cung cấp URL và quyết định đổi sang Groq `openai/gpt-oss-120b` khi 20b hết quota. Codex thực hiện API runs, script chặn gửi/thu bằng chứng, kiểm thử và tổng hợp tài liệu; không ghi là thành viên tự thao tác. Group mới 6/10 PASS, 10/10 measured; 3 HTTP400 chứa text model được giữ và chấm FAIL thiếu tool. Transcript CLI thật 6 lượt, lỗi X403 hiển thị trung thực, không gửi Telegram. Full suite 175 passed, 14 skipped. [B3/B4 và evidence](../../report/team/group_report.md), [phần còn chờ](../../docs/SUBMISSION-READINESS.md).

URL demo lỗi DNS; người dùng sẽ bổ sung xác nhận người thật. Chưa coi public UI/người ngoài nhóm thử hoặc tự đánh giá cá nhân là hoàn thành.
