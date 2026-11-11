# Bàn giao artifact CP2 — TV3 / TV4

Artifact đã đo: `v4-integration+p9ea16ca1d5c6+tf96eb98fa99f`.
Provider/model: Groq / openai/gpt-oss-20b. Nền dev: `c57ee1960b918dcec256d76a5b0fb30ac601ad25`.

| Artifact | SHA-256 |
|---|---|
| system_prompt.md | `9ea16ca1d5c61eeaf3ca7a1abf559bfebb9644a2d70bd6971a4b2c25a48849e6` |
| tools.yaml | `f96eb98fa99f9b1b091efd99714215a490be755b0ff49aedfa3fd36fc19142b2` |

Runtime code được khóa trong [cp2_handoff.json](../starter_v0/analysis/cp2_handoff.json). Snapshot: [prompt](../starter_v0/artifacts/versions/v4-integration/system_prompt.md), [tools](../starter_v0/artifacts/versions/v4-integration/tools.yaml). Run: [base tích hợp](../starter_v0/runs/v4-integration_B_base_groq_20261111T001019800451.json). Kết quả 18/20, 0 provider errors; 7 lỗi tool RapidAPI HTTP 403, hai case R12/R13 còn FAIL. Xem [phân tích](CP2-STATUS.md).

## Trước khi chạy

Từ starter_v0, cấu hình .env cục bộ theo TOOL-SETUP, cài requirements và chạy `python scripts/verify_cp2_evidence.py`. Nếu hash/runtime khác thì dừng dùng nhãn đã đo; thay đổi code/prompt/schema cần nhãn/run mới. Không ghi đè snapshot hoặc run hiện có.

## TV3 — group eval (#13/#14)

Giữ nguyên prompt/tools đã khóa. Hoàn thiện bộ group theo yêu cầu 10 case (5 single, 5 multi, có case route tool mới); kiểm tra registry/contract và ghi rõ file case dùng đo. Chạy:

```powershell
python run_eval.py --provider groq --model openai/gpt-oss-20b --version v4-integration --suite group --eval-cases data/eval_group.json
```

Giữ cả run lỗi provider và lỗi tool; chỉ dùng run measured=total, provider_error_cases=0 làm bằng chứng. Eval không cấp phép gửi Telegram; nếu thêm case gọi send phải chặn thực thi gửi. Chưa có group eval mới trong phần việc #10 này.

## TV4 — UI/demo (#15/#16)

```powershell
python -m streamlit run app.py
```

Trong sidebar chọn provider **groq**, model **openai/gpt-oss-20b**, Version **v4-integration**. Kiểm tra caption artifact đúng nhãn/hash phía trên. UI đọc artifacts hiện hành, không đổi file giữa session. Transcript phải ghi cùng hash, gồm yêu cầu thường, thiếu thông tin rồi bổ sung và yêu cầu gửi/đăng. Việc demo vẫn phải chờ người dùng duyệt đúng nội dung trước gửi; không coi đề bài hoặc eval là xác nhận gửi thật.

CLI tương đương để thu transcript:

```powershell
python chat.py --provider groq --model openai/gpt-oss-20b --version v4-integration
```

Tài liệu này chốt đầu vào bàn giao; chưa tuyên bố TV3/TV4 đã chạy hoặc nhận tin nhắn. Sau khi publish nhánh/PR, dùng đúng commit chứa handoff và xác minh lại hash.

## Profile live bổ sung 11/11/2026

Theo quyết định justcoffeee sau lỗi quota 20b, group và CLI chat dùng Groq `openai/gpt-oss-120b`, nhãn `v4-integration-groq120b+p9ea16ca1d5c6+tf96eb98fa99f`. Prompt/tools giữ nguyên hash ở trên; không sửa profile20b hay số lịch sử. [Profile/evidence mới](../starter_v0/analysis/final_evidence_profile.json), [B3/B4](../report/team/group_report.md). Public UI cần smoke lại đúng model/version này khi URL hoạt động.
