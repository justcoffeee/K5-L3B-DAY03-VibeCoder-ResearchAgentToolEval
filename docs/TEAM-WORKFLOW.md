# Quy trình nhóm và setup CP1

## Phân công

| GitHub | Công việc | Issue |
|---|---|---|
| justcoffeee | Nhóm trưởng; setup/baseline, tối ưu, tích hợp/nộp | #9, #10, #17 |
| Tiberu2611 | Tool mới và unit test | #11, #12 |
| chur04 | Case eval nhóm, chạy và phân tích | #13, #14 |
| khanhduyvu1 | UI, demo, transcript, Phần A | #15, #16 |

Thông tin cá nhân và đóng góp điền trong TEAM.md; không tự suy đoán họ tên/MSSV/email.

## Git và tích hợp

- Nhánh tích hợp phát triển: `dev`. Nhóm trưởng hiện làm trên `phamhoanghuy`.
- Các thành viên tách nhánh cá nhân từ `dev`, commit phần việc, push rồi mở PR vào `dev`.
- Nhóm trưởng review code/evidence, chạy kiểm tra và xử lý xung đột trước khi merge.
- Không force-push hoặc xóa lịch sử. Mỗi người phải có commit kỹ thuật trên nhánh nộp.
- Chỉ chốt nhánh nộp và commit cuối sau khi kiểm tra đầy đủ SUBMISSION.md.

## Setup Windows PowerShell

Chạy từ `starter_v0/`. Dùng executable Python trực tiếp để không cần đổi execution policy:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu chưa có `.env`, sao chép `.env.example` thành `.env` (không ghi đè file đã điền).
Điền key trực tiếp trong file cục bộ, không gửi qua chat hay commit lên GitHub:

- GROQ_API_KEY
- TAVILY_API_KEY
- FIRECRAWL_API_KEY
- RAPIDAPI_KEY (cho timeline và social_search)
- RAPIDAPI_TWITTER_HOST=twitter-api45.p.rapidapi.com

Provider đã chọn theo nhóm trưởng: `groq`; model mặc định `openai/gpt-oss-20b`.
Có thể đặt GROQ_MODEL trong .env hoặc truyền --model; dùng cùng model cho các vòng so sánh.
Đã bổ sung adapter Groq, không sửa prompt/tool declaration hoặc logic chấm điểm baseline.
Adapter dùng endpoint cố định https://api.groq.com/openai/v1 qua SDK đã có trong requirements.txt.
Tham khảo: [Groq compatibility](https://console.groq.com/docs/openai),
[tool calling](https://console.groq.com/docs/tool-use/overview).
Môi trường máy setup hiện tại: Python 3.14.8; phiên bản dependency thực tế được lưu trong evidence CP1.

## Thứ tự chốt baseline

1. Giữ nguyên `artifacts/system_prompt.md` và `artifacts/tools.yaml` của starter.
2. Chạy unit test offline, rồi preflight với key thật:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts/preflight_provider.py --provider groq
```

3. Preflight pass mới chạy baseline:

```powershell
.\.venv\Scripts\python.exe run_eval.py --provider groq --version v0 --suite base --eval-cases data/eval_base.json
```

4. Kiểm tra run JSON có `summary.provider_error_cases == 0` và
   `summary.measured_cases == summary.total_cases`. Đọc cả tool_results để thấy lỗi tool thật nếu có.
5. Lấy hash/metric/run_file từ JSON thật để điền version_log.csv và B1/B2 của group_report.
6. Chỉ thông báo baseline đã chốt khi đủ điều kiện trên; sau đó bắt đầu tối ưu v1–v3.

TV2/TV4 có thể viết tool/UI trên nhánh riêng trong khi chờ baseline. Chưa tích hợp thay đổi
vào artifact dùng đo. Nhóm trưởng phối hợp TV2 khi sửa tools.yaml, tránh trộn thay đổi không liên quan
vào một vòng kiểm chứng giả thuyết.

Không sửa nội dung eval_base.json/eval_research_extension.json. Không commit .env, .venv,
key/token/cache/arxiv_papers hoặc evidence có secret. Không dùng sample mock làm run thật.

## Trạng thái key và bằng chứng live

Nhóm trưởng đã bổ sung thông tin RapidAPI sau khi chọn Groq. Cấu hình cần đủ 4 key
trực tiếp trong .env: GROQ_API_KEY, TAVILY_API_KEY, FIRECRAWL_API_KEY, RAPIDAPI_KEY.
Giữ nguyên timeline/social_search và case base; không thay bằng kết quả mock hoặc bỏ case để tăng điểm.
Đánh giá routing/args và khả năng lấy dữ liệu thật là hai kết quả khác nhau; báo cáo phải nêu rõ
lỗi tool_results, kể cả khi metric routing pass. Kiểm tra key và đăng ký API Twitter API45
trên RapidAPI trước khi chốt khả năng chạy live của hai tool này.

Các key từng được gửi qua chat cần thu hồi và thay mới trực tiếp trong .env trước khi gọi API,
theo RULES.md và company_policy/data-privacy-policy.md. Không lưu lại key đã gửi vào tài liệu/log.
