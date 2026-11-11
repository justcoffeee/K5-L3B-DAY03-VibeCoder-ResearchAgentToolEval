# Demo UI — link, kịch bản và xác nhận người thử

Người điều phối: Phạm Hoàng Huy (`justcoffeee`). Codex hỗ trợ soạn kịch bản và kiểm thử tự động; không đại diện cho một người ngoài nhóm đã dùng thử.

## Link được cung cấp

[https://bar-barbara-coated-county.trycloudflare.com](https://bar-barbara-coated-county.trycloudflare.com)

Ngày 11/11/2026, lần mở bằng browser của Codex trả `net::ERR_NAME_NOT_RESOLVED`; giao diện không tải được. Người dùng sau đó xác nhận link đang lỗi và yêu cầu bổ sung link/kịch bản chi tiết trước. Đây là **smoke test public URL bị chặn bởi DNS**, không phải một lượt UI pass. Cần bật lại tunnel hoặc cung cấp URL mới trước demo.

## Cấu hình cần đối chiếu khi link hoạt động

- Provider: `groq`.
- Model: `openai/gpt-oss-20b`.
- Version: `v4-integration`.
- Caption artifact phải là `v4-integration+p9ea16ca1d5c6+tf96eb98fa99f`.
- [Hash đầy đủ và quy tắc bàn giao](CP2-HANDOFF.md).
- Không đưa API key vào nội dung chat, ảnh chụp hoặc feedback. UI dùng key cấu hình phía server.

## Kịch bản smoke và thử ngoài nhóm

Các dòng dưới là **test case/kết quả kỳ vọng do Codex soạn**, chưa phải lời chứng hoặc kết quả người thật đã thực hiện.

| ID | Thao tác | Kết quả kỳ vọng | Trạng thái hiện tại |
|---|---|---|---|
| UI01 | Mở public URL, kiểm tra tiêu đề/sidebar | UI tải được, không lỗi kết nối; chọn đúng provider/model/version | BLOCKED: lần mở hiện tại lỗi DNS |
| UI02 | Đối chiếu caption artifact với hash đã bàn giao | Nhãn/hash khớp; phiên mới đọc đúng file hiện hành | Chờ URL hoạt động |
| UI03 | Hỏi một tài liệu chính thức về Python asyncio, yêu cầu tiêu đề/URL | Hiển thị retrieval tool, kết quả/nguồn thật; nếu tool lỗi thì hiện lỗi và không dựng nguồn giả | Chờ URL hoạt động |
| UI04 | Hỏi một tweet mới nhất nhưng không nêu tài khoản; sau đó bổ sung @sama, limit=1 | Agent hỏi dữ kiện thiếu, giữ hội thoại; lượt bổ sung dùng đúng account/count | Chờ URL hoạt động |
| UI05 | Yêu cầu bản nháp Telegram, chưa gửi; sau đó yêu cầu hỏi xác nhận | UI hiển thị đúng draft, không tin model tự đặt confirmed=true, chờ thao tác người dùng | Chờ URL hoạt động; không cần gửi thật |
| UI06 | Từ chối/hủy gửi | Không gửi; draft/hội thoại phản ánh hủy; transcript không có status sent | Chờ URL hoạt động |
| UI07 | Kiểm tra nguồn và lỗi tool ở lượt có lỗi API | Không che lỗi bằng dữ liệu bịa; không lộ key/token; URL nguồn đúng dữ liệu tool | Chờ URL hoạt động |
| UI08 | Lưu feedback và transcript session | Có thời điểm, phiên bản/hash, câu hỏi, tool trace và outcome; không dùng mock/sample | Chờ người thật và URL hoạt động |

## Mẫu xác nhận do người ngoài nhóm tự điền

- Tên/mã người thử: **chưa cung cấp**.
- Quan hệ với nhóm: **người thử xác nhận không thuộc nhóm**.
- Thời điểm và URL hoạt động: **chưa có**.
- Artifact caption/version/hash quan sát: **chưa có**.
- Các case đã thử (ID và input thực tế): **chưa có**.
- Kết quả thực tế/lỗi gặp: **chưa có**.
- Đường dẫn transcript/ảnh hoặc feedback gốc: **chưa có**.

Người dùng đã chọn sẽ bổ sung xác nhận người thật. Không thay các ô này bằng tên, lời nhận xét hoặc kết quả do AI tự sinh. Gửi Telegram thật là bonus riêng, chỉ thực hiện khi người dùng duyệt nội dung/đích nhận cụ thể.

## Điều kiện đóng #15

Code và test UI đã có; link hiện tại và kịch bản đã được ghi. Chỉ đóng khi public URL thực sự truy cập được, có smoke trên artifact cuối và feedback người ngoài nhóm đủ bằng chứng. Group eval/CLI transcript thật là bằng chứng bổ trợ, không thay thế việc một người mở và thử UI public.
