# CP2 — Tối ưu và chốt artifact tích hợp (#10)

Lịch sử tối ưu cũ v1–v5 đã được xóa theo yêu cầu; baseline v0 giữ nguyên. Ba vòng chạy mới v1–v3 đã hoàn tất. Sau lần kiểm tra thiếu yêu cầu #10, người dùng cho phép hoàn thiện thêm: chốt prompt nhiều bước, tích hợp code/schema mới nhất từ dev và đo riêng bằng nhãn v4-integration. Không sửa bằng chứng v1–v3.

## Kết quả thật

| Version | PASS | Case accuracy | Routing | Arguments | Multiturn | Tool errors |
|---|---:|---:|---:|---:|---:|---:|
| v0 | 9/20 | 45% | 70% | 45% | 33.33% | 7 |
| v1 | 15/20 | 75% | 90% | 75% | 66.67% | 6 |
| v2 | 14/20 | 70% | 95% | 70% | 66.67% | 7 |
| v3 | 16/20 | 80% | 90% | 80% | 83.33% | 6 |
| v4-integration | 18/20 | 90% | 95% | 90% | 100% | 7 |

Mỗi run trong version_log đủ 20 measured / 20 total và 0 provider errors. Provider/model: Groq / openai/gpt-oss-20b. Không sửa nội dung base/extension hoặc expectation. Không gửi Telegram. Điểm không cần đạt 100% để chứng minh các vòng tối ưu; lỗi và giới hạn được giữ nguyên bên dưới.

## Thay đổi và nhận xét

- v1 chỉ sửa prompt: hỏi account/URL khi thiếu dữ kiện, không đoán. 45% → 75%; R10/R11/M01/M04 PASS, M03 hồi quy.
- v2 chỉ sửa prompt: chờ xác nhận rõ nội dung/đích nhận trước send. 75% → 70%; R12 vẫn bị chấm FAIL vì hỏi nội dung bằng text, expect yes_no. Không có bằng chứng giả thuyết giúp tăng điểm; không suy ra đã gửi trái phép.
- v3 chỉ sửa description của 10 tool: ranh giới khi dùng/không dùng, handle không @, query giữ chủ đề, topic=news, timeframe, Top/Latest. Prompt/schema/default giữ nguyên. 70% → 80%; sửa R01/M02/M06, M03 hồi quy.
- v4-integration là vòng kiểm tra tích hợp, không gọi là phép đo cô lập một giả thuyết: bỏ ép một tool/một bước, giữ trạng thái yêu cầu/correction, retrieval độc lập, chờ dữ liệu thật trước analyze/rank/format; thêm ranh giới nội dung không đáng tin và trả lời không tool khi phù hợp. Tích hợp hai declaration analyze_text/rank nguyên schema đã review trên dev, giữ code/registry upstream. 80% → 90%; sửa R03/M03, không có case hồi quy so với v3. Một lần đo chưa xác lập quan hệ nhân quả.

## Hai case còn FAIL và tool live

- R12: clarify(response_type=text) xin nội dung bản tin còn thiếu; harness đòi yes_no. Review ngữ nghĩa theo ngữ cảnh; không đổi đáp án hoặc bịa nội dung để tăng điểm.
- R13: chỉ lookup(query=AI, topic=news, timeframe=day), thiếu social_search. Prompt đã cho phép nhiều nguồn nhưng lần đo này model chưa tuân thủ; không tuyên bố đã sửa dứt điểm. Hướng tiếp theo: giả thuyết riêng về điều phối retrieval độc lập.
- V4 có 7 lỗi RapidAPI HTTP 403. Routing/args PASS không chứng minh đã lấy tweet thành công. Không đổi API/case hoặc mua gói. Các URL cố định có thể trả nội dung trang 404.
- Harness base gọi model một lần/case, nên chưa chứng minh workflow nhiều vòng retrieval → analyze/rank → format hoặc xác nhận → send. Chat/UI của dev có tool loop; TV3/TV4 kiểm tra riêng theo handoff.

## Kiểm tra và nguồn code

- Contract trên artifact cuối: 66 passed. Full suite gồm UI và test retry: 164 passed, 14 skipped, 0 failed. [Output](../starter_v0/analysis/cp2_pytest_final.txt).
- Runner offline loại key, chặn DNS và kết nối ngoài; chỉ cho phép socketpair nội bộ của asyncio trên Windows. Lệnh tái kiểm tra: `python scripts/run_offline_tests.py` từ starter_v0.
- [Verifier offline](../starter_v0/scripts/verify_cp2_evidence.py) tính lại từng case/summary, kiểm tra hash/manifest/version log/input/expect và runtime cuối. [Output](../starter_v0/analysis/cp2_verification.txt).
- Đã kiểm tra lại verifier trên bản xuất sạch từ Git index. `.gitattributes` giữ nguyên byte của artifact/kế hoạch/harness lịch sử và cố định EOL các input đã hash, tránh core.autocrlf làm sai hash khi checkout trên máy khác.
- Nền tích hợp: dev `c57ee1960b918dcec256d76a5b0fb30ac601ad25`. PR #28 đã sửa normalize_value để sort list object bằng JSON canonical. Bản harness cũ/hash được lưu trong analysis/cp2_harness, provenance trong [integration context](../starter_v0/analysis/cp2_integration_context.json); chạy lại scorer hiện tại trên v0–v3 cho cùng điểm. Không hoàn nguyên sửa lỗi upstream để giữ hash cũ.
- V4 trung gian dùng declaration baseline bị contract chặn vì case nhóm mới cần rank: không chạy eval, không có dòng version log; giữ kế hoạch/snapshot/log dưới nhãn v4 để audit. Sau đó lập kế hoạch mới v4-integration trước khi đổi hai artifact.
- V2 lượt đầu HTTP 400, v3 lượt đầu HTTP 429 được giữ riêng và loại khỏi version_log. V4-integration có 1 lần retry HTTP 429; chỉ retry request chưa có model response, giữ nguyên tham số và ghi sự kiện. HTTP 400 hoặc kết quả model đã có không được retry bên trong case. Bốn unit test xác minh quy tắc này.

## Artifact bàn giao

- Nhãn cuối: `v4-integration+p9ea16ca1d5c6+tf96eb98fa99f`.
- [Hướng dẫn TV3/TV4](CP2-HANDOFF.md); [hash đầy đủ/runtime lock](../starter_v0/analysis/cp2_handoff.json).
- [Version log](../starter_v0/artifacts/version_log.csv), [summary](../starter_v0/analysis/cp2_summary.json), [điều kiện](../starter_v0/analysis/cp2_conditions.md).

- v0: [run](../starter_v0/runs/v0_B_base_groq_20261110T175003235889.json); `v0+peb1c8179815b+te69bc53ed884`.
- v1: [run](../starter_v0/runs/v1_B_base_groq_20261110T234054699020.json); `v1+p11a492d87f35+te69bc53ed884`.
- v2: [run](../starter_v0/runs/v2_B_base_groq_20261110T234621926396.json); `v2+p6b593bb9bae0+te69bc53ed884`.
- v3: [run](../starter_v0/runs/v3_B_base_groq_20261110T235639856548.json); `v3+p6b593bb9bae0+t6180659c52a7`.
- v4-integration: [run](../starter_v0/runs/v4-integration_B_base_groq_20261111T001019800451.json); `v4-integration+p9ea16ca1d5c6+tf96eb98fa99f`.

## Đối chiếu checklist #10

- Đủ v0 và ba vòng tối ưu v1–v3, mỗi vòng một giả thuyết/đổi hash; có kế hoạch trước sửa, snapshot và run hợp lệ.
- Version log đủ trường; B1/giải pháp/reflection ghi cả vòng giảm điểm.
- Prompt bỏ đoán, chờ clarification/confirmation, cho phép nhiều bước; declaration 12 tool có quy ước rõ, contract xanh.
- Hai tool đã có code/registry/test trên dev; schema mới được giữ khi tích hợp; artifact đổi sau v3 được đo bằng nhãn riêng.
- Nhãn/hash/lệnh chạy cho TV3 và TV4 nằm trong handoff, được commit cùng bằng chứng. Bàn giao qua tài liệu; chưa gửi tin nhắn, push hoặc đóng issue từ phiên này.
