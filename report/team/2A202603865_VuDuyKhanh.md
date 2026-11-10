# Báo cáo cá nhân — Vũ Duy Khánh — 2A202603865

## 1. Thông tin thành viên

- Họ tên: Vũ Duy Khánh
- MSSV: 2A202603865
- GitHub: khanhduyvu1
- Email: 26ai.khanhvd2@vinuni.edu.vn

## 2. Phần việc phụ trách

- TV4: UI cho tiêu chí C6 (issue #15, W07).
- Demo, transcript live và Phần A của báo cáo nhóm (issue #16, W08).

## 3. Đóng góp cụ thể

**UI Streamlit (`starter_v0/app.py`)**

- Dùng lại provider, registry, prompt và vòng lặp `run_model_tool_loop` của `chat.py`; giữ hội thoại nhiều lượt và chờ người dùng khi `clarify`; lưu transcript theo cùng định dạng với `chat.py`.
- Hiển thị tool đã gọi, kết quả thật, danh sách nguồn và lỗi tool.
- Thêm provider `groq` vào UI, dùng `GroqProvider` của nhóm từ nhánh `dev`.
- Giao diện: theme trong `.streamlit/config.toml`, logo, câu hỏi mẫu; thêm `streamlit` vào `requirements.txt`.
- Mở link dùng thử bằng Cloudflare Tunnel, key đặt trong `.env` phía server. Link là tạm thời nên được ghi riêng ở mục A1 khi chốt.

**Sửa lỗi theo review của nhóm trưởng ở PR #22**

- Che credential đã cấu hình, trường nhạy cảm và các dạng key phổ biến trước khi lưu transcript hoặc hiển thị.
- Mọi lời gọi `send` có nội dung đều được giữ thành bản nháp và dừng vòng lặp; chỉ nút xác nhận trên UI mới gửi thật.
- Chỉ kết quả từ tool lấy dữ liệu mới được tính là nguồn; `format` và `rank` tự chúng không chứng minh có nguồn.
- Giữ `rounds` và `tool_events` đã chạy khi provider lỗi ở vòng sau, bằng 2 tham số tuỳ chọn trong `chat.py`.
- Theo dõi nguồn qua các lượt trong cùng phiên, để việc trình bày lại dữ liệu đã lấy không bị ẩn nhầm, trong khi dữ liệu tự bịa vẫn bị chặn.
- Vệ sinh dữ liệu nguồn (Source Sanitization): loại bỏ ký tự điều khiển Markdown và chuẩn hoá URL (`safe_link_url`, `escape_markdown`) để ngăn chặn việc tool bên ngoài trả metadata giả mạo link lừa đảo (phishing) hoặc phá vỡ cấu trúc hiển thị danh sách nguồn.
- Thêm `starter_v0/tests/test_ui_app.py` gồm 62 regression test offline (38 test logic cốt lõi + 24 test an toàn dữ liệu/chống injection URL).

**Phát hiện khi chạy thử thật, đã báo cho nhóm**

- Khi tool lỗi vì thiếu key, model vẫn tự viết tin từ trí nhớ. Đây là lý do UI ẩn câu trả lời không có nguồn.
- Model truyền handle `SamAltman` thay vì `sama`, khiến `timeline` lỗi. Gọi thẳng API với `sama` thì trả về đủ dữ liệu.
- Bản tóm tắt của model có chỗ sai so với nguồn, ví dụ ghi Abridge "gọi vốn 5,3 tỷ USD" trong khi nguồn chỉ nói về việc cắt giảm nhân sự.

**Chưa hoàn thành tại thời điểm viết**

- PR #22 đang chờ nhóm trưởng merge vào `dev`: bản sửa hoàn tất ở commit `e4462bc` và đã gộp commit mới nhất từ `dev` ở `b353b8d`.
- Cần chạy một phiên chat live chính thức $\ge 3$ lượt trên artifact cuối cùng của nhóm (sau khi CP2 tối ưu prompt/tools) để ghi transcript nộp bài và điền bảng B4.
- Điền link public Cloudflare Tunnel vào mục A1 của báo cáo nhóm khi mở demo.
- Thử nghiệm gửi Telegram thật trên private channel để lấy điểm bonus (UI đã sẵn sàng nút bấm và logic gọi).

## 4. Bằng chứng

- Pull request: [#22](https://github.com/justcoffeee/K5-L3B-DAY03-VibeCoder-ResearchAgentToolEval/pull/22), nhánh `vuduykhanh` vào `dev`.
- Commit: `007e176` (UI ban đầu), `ee94c41` (provider `groq`), `f5ac081` (cập nhật UI), `80ad67e` (sửa 4 lỗi review), `e4462bc` (theo dõi nguồn qua các lượt), `b353b8d` (merge `dev` vào `vuduykhanh`).
- File: `starter_v0/app.py`, `starter_v0/.streamlit/config.toml`, `starter_v0/assets/vinuni_logo.png`, `starter_v0/tests/test_ui_app.py`, thay đổi trong `starter_v0/chat.py`, `starter_v0/requirements.txt`, `starter_v0/.env.example`.
- Kiểm thử: `pytest` trên nhánh sau khi gộp `dev`: **181 passed, 14 skipped, 0 failed**; toàn bộ 62 test của UI trong `test_ui_app.py` đều pass; 14 test skipped là stub TODO có sẵn của starter.
- CI: job `offline-tests` xanh ở commit `f6eea20` và các commit sửa lỗi sau đó.
- Chạy thật: các phiên thử UI local được lưu tại `starter_v0/transcripts/ui/` để kiểm tra các trường hợp tương tác thực tế với Groq, OpenRouter và Ollama.

**AI/công cụ đã dùng và cách tự kiểm tra kết quả**

- Dùng Claude Code để hỗ trợ viết khung UI Streamlit, sinh các pattern regex che secrets và viết scaffold cho các unit test offline trong `test_ui_app.py`.
- Tự chạy UI với Groq và các API thật, trực tiếp đối chiếu output hiển thị với run log để phát hiện việc model bịa tin khi tool lỗi.
- Chạy `pytest` sau mỗi lần sửa đổi code, bảo đảm kiểm thử offline không phụ thuộc vào internet hoặc secret keys.
- Tiếp thu phản hồi qua PR review của nhóm trưởng, sửa triệt để các vấn đề về an toàn thông tin, kiểm soát luồng `send`, lưu vết trạng thái và vệ sinh dữ liệu nguồn.

## 5. Tự đánh giá

**Mình làm được:**

- Xây dựng giao diện Streamlit (`starter_v0/app.py`) bám sát vòng lặp xử lý của `chat.py`, bảo đảm tính trung thực: hiển thị rõ tool được gọi, arguments, kết quả thật từ tool và không giấu lỗi khi tool thất bại.
- Thiết kế và triển khai 6 chốt chặn an toàn quan trọng:
  1. *Che giấu bí mật:* Tự động che mờ các API key (`gsk_`, `tvly-`, `fc-`, `sk-`), Bearer tokens, Telegram token/Chat ID trong transcript và trên giao diện người dùng.
  2. *Kiểm soát hành động (`hold_send`):* Không tin tưởng cờ `confirmed=true` do model tự sinh; mọi lời gọi `send` có nội dung đều được giữ thành bản nháp (`awaiting_ui_confirmation`), chỉ khi người dùng bấm nút xác nhận trên UI thì mới kích hoạt gửi Telegram thật.
  3. *Chống ảo giác (Hallucination Guard):* Phân tách rạch ròi giữa tool thu thập dữ liệu (`RETRIEVAL_TOOLS`) và tool định dạng/xếp hạng (`PRESENTATION_TOOLS`). Khi tool lấy dữ liệu gặp lỗi, UI sẽ ẩn câu trả lời do model tự bịa từ trí nhớ nhằm đảm bảo tính chính xác của dữ liệu nghiên cứu.
  4. *Bảo toàn vết thực thi (Partial Traces):* Giữ nguyên lịch sử các vòng gọi tool trước đó nếu provider gặp sự cố ở vòng tiếp theo.
  5. *Truy vết nguồn qua nhiều lượt:* Tính toán độ trùng lặp từ vựng (`MIN_SHARED_TERMS = 0.3`) để các yêu cầu định dạng lại dữ liệu đã lấy ở lượt trước không bị chặn nhầm.
  6. *Vệ sinh liên kết và siêu dữ liệu (Metadata Sanitization):* Kiểm tra URL hợp lệ qua `safe_link_url` và vô hiệu hóa cú pháp Markdown qua `escape_markdown` để chặn hoàn toàn nguy cơ link giả mạo (phishing) được inject từ dữ liệu bên ngoài.
- Viết 62 regression tests offline trong `starter_v0/tests/test_ui_app.py` bao phủ toàn bộ các case: che thông tin nhạy cảm, chặn hành động gửi, xử lý lỗi provider, truy vết bằng chứng nguồn và chống injection link độc hại. Toàn bộ test chạy offline hoàn toàn (`181 passed, 14 skipped`).

**Mình chưa làm hoặc cần hoàn thiện thêm:**

- Chưa có transcript chạy live chính thức $\ge 3$ lượt trên prompt/tools hoàn thiện sau CP2 để đưa vào bảng B4 của báo cáo nhóm.
- Link Cloudflare Tunnel mới chạy thử nghiệm cục bộ, cần mở và ghi nhận public URL chính thức khi nhóm tổ chức demo/showdown.
- Chưa kích hoạt gửi Telegram thật trên live channel để ghi nhận điểm bonus 2 điểm (dù code UI và logic xác nhận đã sẵn sàng).

**AI làm gì, mình làm gì:**

- *AI (Claude Code/Assistant):* Hỗ trợ viết nhanh cấu trúc giao diện Streamlit, gợi ý biểu thức chính quy (regex) để quét và redact các định dạng khóa nhạy cảm, sinh scaffold code cho các test case trong `test_ui_app.py`.
- *Mình làm:* 
  - Trực tiếp kiểm thử, tìm ra các ca lỗi thực tế khi model tự bịa tin lúc thiếu API key và truyền nhầm handle `SamAltman`.
  - Quyết định ranh giới bảo mật cho UI: chỉ người dùng mới có quyền bấm xác nhận gửi thật; tool định dạng không được coi là bằng chứng có nguồn; siêu dữ liệu từ bên ngoài không được tin cậy trực tiếp.
  - Tự rà soát, chỉnh sửa mã nguồn để vượt qua các tiêu chí review khắt khe của nhóm trưởng tại PR #22.
  - Chạy và kiểm tra toàn bộ suite `pytest` ở môi trường local trước khi push commit.

**Những câu hỏi kỹ thuật mình tự giải thích được và sẵn sàng trả lời khi vấn đáp:**

1. *Vì sao UI không cho phép model tự xác nhận gửi qua tham số `confirmed=true`?* Model có thể bị ảo giác hoặc chịu ảnh hưởng từ prompt của người dùng mà tự truyền `confirmed=true`. Việc chặn ở tầng code và buộc phải có thao tác bấm nút vật lý trên giao diện bảo đảm an toàn tuyệt đối cho hệ thống bên ngoài.
2. *Vì sao `format` và `rank` không được tính là nguồn dữ liệu (`RETRIEVAL_TOOLS`)?* Vì hai công cụ này chỉ xử lý trên dữ liệu đầu vào có sẵn. Nếu model tự bịa thông tin rồi đưa vào `rank` hoặc `format`, bản tin vẫn hoàn toàn không có căn cứ từ thế giới thực.
3. *Cơ chế theo dõi nguồn qua các lượt hoạt động ra sao?* UI lưu trữ tập từ vựng (`terms`) của các dữ liệu đã thu thập ở các lượt trước. Khi người dùng yêu cầu tóm tắt lại hoặc định dạng ở lượt sau, UI kiểm tra tỷ lệ từ vựng trùng khớp ($\ge 30\%$) để nhận biết model đang làm việc trên dữ liệu đã được kiểm chứng thay vì bịa đặt mới.
4. *Tại sao cần `safe_link_url` và `escape_markdown` cho dữ liệu nguồn?* Siêu dữ liệu từ web hoặc API bên thứ ba là không đáng tin cậy. Nếu không escape hoặc kiểm tra schema URL, kẻ tấn công có thể chèn markdown inject link phishing giả dạng kết quả tìm kiếm hoặc phá vỡ cấu trúc trang web.
5. *Tại sao việc ẩn câu trả lời không có nguồn lại quan trọng hơn việc đưa ra một câu trả lời trôi chảy?* Mục tiêu của research agent là cung cấp thông tin trung thực, có bằng chứng. Một câu trả lời mượt mà nhưng dựa trên dữ liệu ảo giác gây rủi ro thông tin nghiêm trọng hơn nhiều so với việc thông báo thẳng thắn rằng hệ thống chưa lấy được dữ liệu nguồn.
