# Báo cáo cá nhân — Phạm Hoàng Huy — 2A202603836

## 1. Thông tin thành viên

- Họ tên: Phạm Hoàng Huy
- MSSV: 2A202603836
- GitHub: justcoffeee
- Email: Chờ bổ sung

## 2. Phần việc phụ trách

- Nhóm trưởng: issue #9 (setup/baseline), #10 (tối ưu v1–v3), #17 (tích hợp/báo cáo/chốt bài).

## 3. Đóng góp cụ thể

- CP1 đang thực hiện với hỗ trợ Codex: bổ sung phân công, quy trình phát triển,
  tạo môi trường và .env cục bộ, chạy kiểm thử offline và preflight.
- Bổ sung adapter Groq theo lựa chọn của nhóm trưởng, giữ nguyên artifact baseline.
- Đã chạy preflight Groq và baseline v0 bằng openai/gpt-oss-20b: 9/20 case PASS (45%), routing 70%, arguments 45%, multiturn 33,33%; 0 lỗi provider.
- Ghi version_log.csv, phân tích đủ 11 case FAIL trong B2; tách 7 lỗi tool RapidAPI khỏi metric model. Các vòng v1–v3 chưa thực hiện.
- Xác minh lại RapidAPI sau đăng ký gói free: hai endpoint HTTP 200, hai tool registry đều trả 1 item, không lỗi; giữ nguyên baseline cũ.

## 4. Bằng chứng

- [TEAM.md](../../TEAM.md), [quy trình](../../docs/TEAM-WORKFLOW.md), [trạng thái CP1](../../docs/CP1-STATUS.md).
- [Pytest](../../starter_v0/analysis/cp1_pytest.txt): 64 passed, 17 skipped, 0 failed.
- [Preflight Groq](../../starter_v0/analysis/cp1_groq_preflight_gpt_oss_20b.txt): pass.
- [Run v0](../../starter_v0/runs/v0_B_base_groq_20261110T175003235889.json), [analysis](../../starter_v0/analysis/cp1_baseline_analysis.json), [version log](../../starter_v0/artifacts/version_log.csv).
- AI/công cụ hỗ trợ: Codex, Git, Python/pip, pytest.
- Kiểm tra bằng công cụ: chạy test offline, kiểm tra diff prompt/tools/eval, kiểm tra gitignore .env/.venv.
- Commit/PR: Xem lịch sử commit CP1 của nhánh phamhoanghuy và PR vào dev tham chiếu issue #9.
- Phần tự kiểm tra/giải thích trực tiếp của thành viên: Chờ Phạm Hoàng Huy bổ sung sau khi tự chạy và đọc kết quả.

## 5. Tự đánh giá

Chờ thành viên tự viết; không suy đoán hoặc điền thay trải nghiệm cá nhân.
