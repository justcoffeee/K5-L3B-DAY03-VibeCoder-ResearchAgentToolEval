# Điều kiện so sánh CP2

- Theo yêu cầu người dùng, đã xóa lịch sử tối ưu cũ v1–v5 (run, snapshot, kế hoạch, analysis), giữ nguyên baseline v0 và chạy lại tuần tự từ v1 đến v3. Không tái sử dụng metric của lịch sử đã xóa.
- Provider/model cố định: Groq / openai/gpt-oss-20b.
- v0 là run tham chiếu nguyên bản; không sửa hoặc chạy đè. Sau v0, người dùng đăng ký gói Twitter API45 và retest đã pass. Vì vậy mức thành công tool live trước/sau có khác điều kiện subscription.
- Harness base vẫn gọi model một lần cho mỗi case; multi-turn là lịch sử đã ghép, không phải mô phỏng mọi lượt agent. Không suy ra đã hỏi clarify ở lượt trước chỉ từ kết quả cuối.
- scripts/cp2_experiment.py gọi nguyên run_eval.py, không thay expected hoặc hàm chấm. Chỉ bổ sung snapshot, metadata kế hoạch, redaction credential và chặn gửi Telegram. Actual model tool calls vẫn được chấm nguyên trạng; tool send trả blocked_for_eval.
- Kết quả routing/args và tool_results được báo riêng. Một case PASS không chứng minh fetch đọc được tài liệu (có thể trả trang 404).
- Các thay đổi cùng provider/model có thể vẫn có biến động model. Một lần chạy chỉ hỗ trợ hoặc không hỗ trợ giả thuyết, chưa xác lập quan hệ nhân quả.
- Không hardcode case ID, câu hỏi hoặc expected answer vào prompt. Case ID chỉ xuất hiện trong kế hoạch/analysis để theo dõi.
- R03/M02/M06 được review cả tên tool/args thực tế và ý nghĩa query; không sửa điểm exact-match của harness.
- V1–v3 dùng bộ 10 tool baseline. Người dùng sau đó cho phép hoàn thiện: v4-integration trên dev c57ee19 dùng 12 declaration và prompt nhiều bước; đây là phép đo tích hợp, không cô lập một thay đổi. Xem integration context về sửa lỗi sort list object của scorer upstream; verifier xác nhận điểm cũ không đổi.
- RapidAPI retest CP1 từng pass không bảo đảm dịch vụ tiếp tục hoạt động: run v1 mới gặp HTTP 403/429. Giữ nguyên tool_results và báo số lỗi thực thi riêng; không mua gói hoặc sửa case để né lỗi.

- V4-integration xử lý HTTP 429 bằng retry có giới hạn, cùng tham số, chỉ khi chưa có model response; sự kiện lưu trong execution_policy. Không retry một kết quả đã chấm hoặc HTTP 400 trong từng case.
