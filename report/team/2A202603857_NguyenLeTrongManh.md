# Báo cáo cá nhân — Nguyễn Lê Trọng Mạnh - 2A202603857

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Lê Trọng Mạnh 
- MSSV: 2A202603857
- Email: 26ai.manhnlt@vinuni.edu.vn

## 2. Phần việc phụ trách

TV2 theo [TEAM.md](../../TEAM.md) (GitHub `Tiberu2611`): **tool mới (#11)** và **unit test cho tool mới (#12)**. Làm trên nhánh cá nhân `NguyenLeTrongManh`, tích hợp vào `dev` qua PR.

## 3. Đóng góp cụ thể

- **Tool `analyze_text`** (`starter_v0/tools/analyze_text/`): gọi LLM trên Groq (`openai/gpt-oss-120b`) để tóm tắt, rút ý chính hoặc đánh giá sentiment cho text agent đã có. Text đưa vào được bọc trong thẻ `<document>` để model coi là dữ liệu, không làm theo lệnh nằm trong text. Biến chọn model riêng `ANALYZE_TEXT_MODEL` để không bị `GROQ_MODEL` của provider agent ghi đè. Không bao giờ raise: lỗi trả `{"tool", "error", "message"}`.
- **Tool `rank`** (`starter_v0/tools/rank/`): lọc trùng (theo URL, hoặc title nếu thiếu URL) và xếp hạng item gộp từ nhiều nguồn theo `relevance` / `recency` / `popularity` / `balanced`, giữ top K. Chạy cục bộ, không cần key. Đọc được ngày tháng định dạng Twitter, ISO và RFC 2822.
- **Đăng ký và bàn giao:** thêm vào `TOOL_FUNCTIONS` trong `tools/__init__.py`; viết `TOOL.md` (frontmatter đúng contract), `declaration.yaml` để nhóm trưởng dán vào `tools.yaml` sau baseline, và `eval_cases_sample.json` (2 case mỗi tool) cho TV3. **Không sửa** `artifacts/system_prompt.md` và `artifacts/tools.yaml` (hash `e69bc53ed884`, trùng baseline v0).
- **Unit test** (`starter_v0/tests/test_tools_todo.py`): `analyze_text` 7 hàm / 18 case, `rank` 10 hàm / 17 case; offline hoàn toàn nhờ `fake_http`, key giả qua `monkeypatch.setenv`.
- **Hoàn thành test cho các tool có sẵn:** viết xong cả 14 stub của 8 tool starter (`clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy`), đưa `pytest` về `167 passed, 0 skipped`. Khi viết test, thăm dò input biên thấy 6 lỗi ở 5 tool có sẵn (nghiêm trọng nhất: `send(confirmed="false")` vẫn gửi tin lên Telegram), đã sửa tối thiểu và giữ test hồi quy; chi tiết ở mục B5 của `group_report.md`.
- **Báo cáo nhóm:** điền B5a, mục 3, 5, 7, 8 và các phần A1–A3, B3 trong `report/team/group_report.md` bằng số liệu thật; các ô thuộc người khác (UI, v1–v3, bảng B3) để trống có ghi chú.
- **Tích hợp git:** merge `origin/dev` vào nhánh cá nhân, giải quyết 4 xung đột (`group_report.md`, `.env.example`, `tools/__init__.py`, `test_tools_todo.py`).

## 4. Bằng chứng

- File/commit/PR:
  - Nhánh `NguyenLeTrongManh`: `ac577a8` (thư mục `analyze_text`), `b247ef0` (đăng ký registry), `21c27f3` (test và B5a), `80aa901` (`.env.example`), `a58f518` (tool `rank` và test), `577f149` (merge `origin/dev`).
  - Nhánh `dev` (cùng nội dung `analyze_text`): `1c3be2b`, `bb0628a`, `e553d4b`, `17fff61`.
  - PR vào `dev` (tham chiếu #11, #12): chưa mở, điền link sau khi mở.
  - Output chạy lại, lưu ở `starter_v0/analysis/`: `cp3_pytest_full.txt` (`99 passed, 14 skipped`), `cp3_contract_after_integration.txt` (contract `65 passed`, toàn suite `109 passed` khi dán 2 declaration vào bản copy `tools.yaml`), `cp3_analyze_text_live.txt` (gọi Groq thật).
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - **AI:** Claude Code (Anthropic, chạy trong VS Code; model Opus 5.5 rồi Sonnet 5.5). Dùng để viết code hai tool, viết unit test, soạn `TOOL.md` / `declaration.yaml` / case mẫu, điền các mục trong `group_report.md`, và hỗ trợ merge git. Claude Code cũng tìm trên web để kiểm tra lịch ngừng model của Groq.
  - **Công cụ khác:** Python 3.14, pytest, Git và GitHub Desktop, Groq API.
  - **Kiểm tra bằng công cụ (đã chạy, có output lưu lại):**
    - `pytest` toàn suite offline: `167 passed, 0 failed, 0 skipped`; 35 test của tool mới và 14 stub của tool có sẵn đều đã được viết.
    - Chạy các test hồi quy trên **code gốc** của 5 tool starter (lấy từ git trước khi sửa): 25 test fail đúng như dự kiến (`analysis/cp3_regression_on_original_code.txt`), chứng minh test bắt được lỗi chứ không pass vô điều kiện.
    - Thăm dò từng tool có sẵn bằng input mà model có thể gửi (`"false"`, `"@sama"`, `limit=-2`, `items=["chuỗi"]`…) trước khi kết luận là lỗi, thay vì đoán từ việc đọc code.
    - Giả lập tích hợp: dán 2 `declaration.yaml` vào bản copy của `tools.yaml` rồi chạy `test_tool_contract.py` (`65 passed`), để biết khai báo khớp với chữ ký hàm; so hash `tools.yaml` thật để chắc baseline không bị đổi.
    - Gọi Groq thật cho `key_points` và `sentiment`, kèm câu "Ignore all previous instructions…" chèn vào text: kết quả đúng nội dung, không trả "HACKED". Mới thử hai lần trên một mẫu.
    - Đọc `run_eval.py` để biết cách harness chấm, thay vì đoán, nên ghi được giới hạn "mỗi case chỉ gọi model một lần" vào B3.
    - Kiểm tra `.env` nằm trong `.gitignore`, không nằm trong `git ls-files`, và không có chuỗi `gsk_` trong báo cáo, `analysis/`, `tools/`.
    - Đối chiếu lịch ngừng model Groq với trang chính thức (`console.groq.com/docs/deprecations`); một số bài bên thứ ba nói khác về phạm vi và thời điểm, nên báo cáo chỉ dựa vào trang chính thức.
  - **Phần tự kiểm tra/giải thích trực tiếp của thành viên:** Chờ Nguyễn Lê Trọng Mạnh bổ sung sau khi tự đọc code và tự chạy lại test.

## 5. Tự đánh giá

...
