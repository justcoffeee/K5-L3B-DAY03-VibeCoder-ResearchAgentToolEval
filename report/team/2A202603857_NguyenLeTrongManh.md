# Báo cáo cá nhân — Nguyễn Lê Trọng Mạnh - 2A202603857

## 1. Thông tin thành viên

- Họ tên: Nguyễn Lê Trọng Mạnh 
- MSSV: 2A202603857
- Email: 26ai.manhnlt@vinuni.edu.vn

## 2. Phần việc phụ trách

TV2 theo [TEAM.md](../../TEAM.md) (GitHub `Tiberu2611`): **tool mới (#11)** và **unit test cho tool mới (#12)**. Làm trên nhánh cá nhân `NguyenLeTrongManh`, tích hợp vào `dev` qua PR.

## 3. Đóng góp cụ thể

- **Tool `analyze_text`** (`starter_v0/tools/analyze_text/`): gọi LLM trên Groq (`openai/gpt-oss-120b`) để tóm tắt, rút ý chính hoặc đánh giá sentiment cho text agent đã có. Text đưa vào được bọc trong thẻ `<document>` để model coi là dữ liệu, không làm theo lệnh nằm trong text. Biến chọn model riêng `ANALYZE_TEXT_MODEL` để không bị `GROQ_MODEL` của provider agent ghi đè. Không bao giờ raise: lỗi trả `{"tool", "error", "message"}`.
- **Tool `rank`** (`starter_v0/tools/rank/`): lọc trùng (theo URL, hoặc title nếu thiếu URL) và xếp hạng item gộp từ nhiều nguồn theo `relevance` / `recency` / `popularity` / `balanced`, giữ top K. Chạy cục bộ, không cần key. Đọc được ngày tháng định dạng Twitter, ISO và RFC 2822.
- **Đăng ký và bàn giao:** thêm vào `TOOL_FUNCTIONS` trong `tools/__init__.py`; viết `TOOL.md` (frontmatter đúng contract), `declaration.yaml` và `eval_cases_sample.json` (2 case mỗi tool) cho TV3. Sau baseline v0 đã dán khối khai báo của 2 tool vào cuối `artifacts/tools.yaml` (hash `e69bc53ed884` → `54ed7f4a1216`); **không sửa** `system_prompt.md` và không đổi `description` của tool có sẵn. Chưa chạy eval cho bản này nên chưa có số đo.
- **Unit test** (`starter_v0/tests/test_tools_todo.py`): `analyze_text` 7 hàm / 18 case, `rank` 11 hàm / 26 case (44 case cho 2 tool mới); offline hoàn toàn nhờ `fake_http`, key giả qua `monkeypatch.setenv`.
- **Kiểm tra tool mới và sửa lỗi (làm cùng Claude Code):** thử "phá" `analyze_text` và `rank` bằng input lạ, tìm ra lỗi ở `rank` (số đếm `inf`/`nan` cho điểm NaN, `10**400` làm cả lời gọi trả `OverflowError`), sửa hàm `_num` và thêm test hồi quy. **Phạm vi:** chỉ làm phần tool mới; không sửa code và không viết test cho tool có sẵn (14 stub của tool starter vẫn skip, được phép).
- **Báo cáo nhóm:** điền B5a, mục 3, 5, 7, 8 và các phần A1–A3, B3 trong `report/team/group_report.md` bằng số liệu thật; các ô thuộc người khác (UI, v1–v3, bảng B3) để trống có ghi chú.
- **Tích hợp git:** merge `origin/dev` vào nhánh cá nhân, giải quyết 4 xung đột (Claude Code xử lý theo yêu cầu của mình) (`group_report.md`, `.env.example`, `tools/__init__.py`, `test_tools_todo.py`).

## 4. Bằng chứng

- File/commit/PR:
  - Nhánh `NguyenLeTrongManh`: `ac577a8` (thư mục `analyze_text`), `b247ef0` (đăng ký registry), `21c27f3` (test và B5a), `80aa901` (`.env.example`), `a58f518` (tool `rank` và test), `577f149` (merge `origin/dev`).
  - Nhánh `dev` (cùng nội dung `analyze_text`): `1c3be2b`, `bb0628a`, `e553d4b`, `17fff61`.
  - PR vào `dev` (tham chiếu #11, #12): [#28](https://github.com/justcoffeee/K5-L3B-DAY03-VibeCoder-ResearchAgentToolEval/pull/28).
  - Output chạy lại, lưu ở `starter_v0/analysis/`: `cp3_pytest_full.txt` (`119 passed, 14 skipped`), `cp3_contract_after_integration.txt` (`test_tool_contract.py` `66 passed` trên `tools.yaml` thật đã khai báo 2 tool), `cp3_analyze_text_live.txt` (gọi Groq thật), `cp3_rank_regression_on_original_code.txt` (test hồi quy của `rank` fail trên code gốc), `cp3_new_tool_audit.txt` (kết quả `scripts/audit_new_tools.py`).
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - **Công cụ AI:** Claude Code (Anthropic, chạy trong VS Code; model Opus 5.5 rồi Sonnet 5.5), dùng làm trợ lý lập trình.
  - **Phần mình quyết định và làm:** chọn hướng hai tool (một tool gọi API Groq để tóm tắt và phân tích text, một tool lọc trùng và xếp hạng kết quả); quyết định giữ nguyên tool có sẵn và chỉ làm phần tool mới; yêu cầu khai báo hai tool vào `artifacts/tools.yaml` sau baseline v0; yêu cầu rà soát các file liên quan CP3; cung cấp key Groq để gọi thử thật; tự commit, push và xử lý merge qua GitHub Desktop.
  - **Phần Claude Code làm:** thiết kế chi tiết hai tool (tham số, enum, cách xử lý input xấu, quy ước error dict), viết code hai tool và unit test, soạn `TOOL.md` / `declaration.yaml` / case mẫu, điền các mục trong `group_report.md`, giải quyết xung đột git theo yêu cầu của mình, và tra trang tài liệu Groq về lịch ngừng model.
  - **Sửa sau review bằng Codex:** bổ sung schema item/metrics cho Gemini và test contract; thêm 9 case hồi quy `rank`, script audit và script chứng minh lỗi trên parser cũ; chạy lại offline với socket bị chặn và cập nhật log/báo cáo. Chưa gọi Gemini live hoặc chạy eval routing ở bước này.
  - **AI:** Claude Code (Anthropic, chạy trong VS Code; model Opus 5.5 rồi Sonnet 5.5). Dùng để viết code hai tool, viết unit test, soạn `TOOL.md` / `declaration.yaml` / case mẫu, điền các mục trong `group_report.md`, và hỗ trợ merge git. Claude Code cũng tìm trên web để kiểm tra lịch ngừng model của Groq.
  - **Công cụ khác:** Python 3.14, pytest, Git và GitHub Desktop, Groq API.
  - **Kiểm tra bằng công cụ (đã chạy, có output lưu lại):**
    - `pytest` toàn suite offline: `119 passed, 0 failed, 14 skipped`; 44 test case của tool mới đều không skip (14 skip là stub của tool có sẵn, được phép).
    - Chạy test hồi quy của `rank` trên **code `_num` gốc** (lấy từ git trước khi sửa): 3 case fail (`inf`, `"inf"`, `10**400`) và pass sau khi sửa (`analysis/cp3_rank_regression_on_original_code.txt`), chứng minh test bắt được lỗi chứ không pass vô điều kiện.
    - Chạy `scripts/audit_new_tools.py`: kiểm tra metadata `TOOL.md`, registry/declaration và 216 lời gọi `rank` (9 giá trị lỗi × 6 trường engagement × 4 criteria), không trả lỗi và mọi điểm số hữu hạn (`analysis/cp3_new_tool_audit.txt`).
    - Chạy lại đúng bước test của `.github/workflows/offline-ci.yml` ở máy (mạng chặn ở mức socket, xoá mọi key): `119 passed, 14 skipped`, nên CI của nhóm sẽ xanh.
    - Dán 2 khối khai báo vào `tools.yaml` thật rồi chạy `test_tool_contract.py`: `66 passed` (10 dòng ứng với 2 tool mới), để biết khai báo khớp với chữ ký hàm.
    - Gọi Groq thật cho `key_points` và `sentiment`, kèm câu "Ignore all previous instructions…" chèn vào text: kết quả đúng nội dung, không trả "HACKED". Mới thử hai lần trên một mẫu.
    - Đọc `run_eval.py` để biết cách harness chấm, thay vì đoán, nên ghi được giới hạn "mỗi case chỉ gọi model một lần" vào B3.
    - Kiểm tra `.env` nằm trong `.gitignore`, không nằm trong `git ls-files`, và không có chuỗi `gsk_` trong báo cáo, `analysis/`, `tools/`.
    - Đối chiếu lịch ngừng model Groq với trang chính thức (`console.groq.com/docs/deprecations`); một số bài bên thứ ba nói khác về phạm vi và thời điểm, nên báo cáo chỉ dựa vào trang chính thức.
  

## 5. Tự đánh giá

**Mình làm được:**

- Hai tool mới nhóm bổ sung (chức năng mới, không phải đổi tên tool có sẵn): `analyze_text` (tóm tắt, rút ý chính, đánh giá sentiment bằng Groq) và `rank` (lọc trùng và xếp hạng item). Cả hai có `TOOL.md` đúng contract, đã đăng ký trong `TOOL_FUNCTIONS` và khai báo trong `artifacts/tools.yaml`.
- 44 test case cho hai tool (7 + 11 hàm), chạy offline, mỗi tool đủ happy path, input xấu và nhánh lỗi. Kết quả CP3 đã lưu trong `analysis/cp3_pytest_full.txt` là `119 passed, 0 failed, 14 skipped`; `analysis/cp3_contract_after_integration.txt` ghi contract `66 passed` (gồm test schema Gemini). Đây là số liệu tại mốc CP3; các lần kiểm tra sau tích hợp được ghi riêng trong báo cáo nhóm.
- Phát hiện và sửa một lỗi thật ở `rank` (số đếm `inf`/`nan` cho điểm NaN, `10**400` làm cả lời gọi trả lỗi). Lỗi này được tìm ra khi chạy script audit do Claude Code viết trên tool của mình; đã sửa và có test hồi quy fail trên code gốc.
- Mình quyết định chỉ làm phần tool mới và không sửa tool có sẵn. Vì vậy 14 stub test của tool có sẵn vẫn skip, và mình không lấy điểm bonus "Test challenge".

**Cập nhật bằng chứng nhóm ngày 11/11/2026:** PR #28/#30/#31 đã merge. Artifact cuối có base run 18/20, 0 lỗi provider; eval_group.json đã có 10 case, gồm 5 case route rank. [kết quả CP2](group_report.md#cp1-cp2), [case nhóm](../../starter_v0/data/eval_group.json). Group run cuối trên Groq120b đạt 6/10 PASS; kết quả và khác biệt cấu hình so với base20b nằm tại [B3](group_report.md#b3-team-eval-cases). Phần tự đọc/giải thích dưới đây vẫn cần thành viên tự ghi.

**Mình chưa làm hoặc chưa chắc (ghi tại mốc CP3, giữ làm lịch sử):**

- Chưa chạy eval, nên **chưa biết** model có route đúng tới hai tool mới không, và việc thêm hai tool có làm xấu routing của các case base không. `tools_hash` đã đổi từ `e69bc53ed884` sang `54ed7f4a1216` nhưng chưa có dòng nào trong `version_log.csv`.
- Chưa có case nào cho tool mới trong `eval_group.json` (việc của TV3). Mình mới chuẩn bị 4 case mẫu.
- `analyze_text` mới gọi Groq thật hai lần trên một mẫu, và chống prompt injection mới thử một câu. Trọng số xếp hạng của `rank` (0.5 / 0.25 / 0.25) là lựa chọn của mình, chưa đo trên dữ liệu thật; toàn bộ test dùng dữ liệu giả.
- Mới có 2 trong 4 tool cần cho bonus "hơn 3 tool mới", nên chưa lấy bonus này.
- PR #28 đã được review; hai vấn đề schema Gemini và bằng chứng test được sửa trong commit bổ sung trước merge.

**AI làm gì, mình làm gì:** phần lớn code hai tool, unit test và các mục báo cáo do Claude Code viết theo yêu cầu của mình (chi tiết ở mục 4). Phần mình làm là chọn hướng tool, đặt phạm vi (chỉ tool mới, giữ nguyên tool có sẵn), yêu cầu khai báo vào `tools.yaml` và rà soát file CP3, cung cấp key Groq, và quản lý git. Mình chưa tự viết phần code nào của hai tool này, nên mình cần đọc kỹ và tự giải thích được chúng (các câu hỏi bên dưới) trước khi nộp.

**Những câu mình cần tự trả lời được trước khi nộp** (chưa ghi câu trả lời ở đây vì mình sẽ tự luyện):

- Vì sao `analyze_text` bọc text trong thẻ `<document>`, cách này chống được gì và không chống được gì?
- Vì sao tool trả error dict thay vì raise?
- Vì sao `ANALYZE_TEXT_MODEL` tách khỏi `GROQ_MODEL`?
- `rank` chấm điểm thế nào? Vì sao popularity dùng log, vì sao item không có ngày được 0 còn item cũ nhất được 0.1?
- Vì sao `tools_hash` đổi và vì sao phải đo lại bằng eval?
- Test nào bắt được lỗi mà eval không thấy (ví dụ điểm NaN của `rank`)?
