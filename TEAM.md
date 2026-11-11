# Team

## Thông tin nhóm

- Tên nhóm: VibeCoder
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-VibeCoder-ResearchAgentToolEval`
- URL repo: https://github.com/justcoffeee/K5-L3B-DAY03-VibeCoder-ResearchAgentToolEval
- Nhánh tích hợp: `dev`; mỗi thành viên làm nhánh cá nhân và mở PR vào `dev`.
- Nhánh nộp, commit chốt: Chưa chốt; điền khi hoàn thành kiểm tra bài nộp.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Phạm Hoàng Huy | 2A202603836 | huyclaynun@gmail.com | justcoffeee | Nhóm trưởng: setup/baseline #9, tối ưu v1–v3 #10, tích hợp và chốt bài #17 |
|   2 | Nguyễn Lê Trọng Mạnh | 2A202603857 | manh025011@gmail.com | Tiberu2611 | TV2: tool mới #11 và unit test #12 |
|   3 | Vũ Văn Chủ | 2A202603873 | vuvanchu3012@gmail.com | chur04 | TV3: 10 eval case #13, group eval và phân tích #14 |
|   4 | Vũ Duy Khánh | 2A202603865 | khanhduy1609@gmail.com | khanhduyvu1 | TV4: UI #15, demo/transcript và Phần A báo cáo #16 |

Mỗi thành viên tự bổ sung thông tin thật còn thiếu, viết báo cáo cá nhân và có commit kỹ thuật.
Danh sách công việc: [GitHub Issues](https://github.com/justcoffeee/K5-L3B-DAY03-VibeCoder-ResearchAgentToolEval/issues).
Quy trình phát triển và setup: [docs/TEAM-WORKFLOW.md](docs/TEAM-WORKFLOW.md).

## Báo cáo cá nhân và bằng chứng kỹ thuật

| Thành viên | Báo cáo | Ví dụ commit/PR có trong dev |
|---|---|---|
| Phạm Hoàng Huy | [2A202603836](report/team/2A202603836_PhamHoangHuy.md) | 5952984: kiểm tra API45; PR #30: CP2/run/hash/handoff |
| Nguyễn Lê Trọng Mạnh | [2A202603857](report/team/2A202603857_NguyenLeTrongManh.md) | a58f518 và các commit tool/test; PR #28/#31 |
| Vũ Văn Chủ | [2A202603873](report/team/2A202603873_VuVanChu.md) | b45aaf5/a2f59de: eval nhóm; PR #29/#32 |
| Vũ Duy Khánh | [2A202603865](report/team/2A202603865_VuDuyKhanh.md) | 007e176/ee94c41/e4462bc: UI và sửa review; PR #22 |

Các liên kết/commit trên chứng minh phần đã tích hợp, không thay phần tự đánh giá hoặc giải thích kỹ thuật của từng người. Nhánh/commit nộp và trạng thái LMS chưa chốt; xem [các mục còn thiếu](docs/SUBMISSION-READINESS.md).

## Bổ sung theo yêu cầu justcoffeee — 11/11/2026

justcoffeee yêu cầu hoàn thiện #14–#16, cung cấp URL và quyết định đổi sang Groq `openai/gpt-oss-120b` khi 20b hết quota. Codex thực hiện API runs, script chặn gửi/thu bằng chứng, kiểm thử và tổng hợp tài liệu; không ghi là thành viên tự thao tác. Group mới 6/10 PASS, 10/10 measured; 3 HTTP400 chứa text model được giữ và chấm FAIL thiếu tool. Transcript CLI thật 6 lượt, lỗi X403 hiển thị trung thực, không gửi Telegram. Full suite 175 passed, 14 skipped. [B3/B4 và evidence](report/team/group_report.md), [phần còn chờ](docs/SUBMISSION-READINESS.md).

URL demo lỗi DNS; người dùng sẽ bổ sung xác nhận người thật. Chưa coi public UI/người ngoài nhóm thử hoặc tự đánh giá cá nhân là hoàn thành.
