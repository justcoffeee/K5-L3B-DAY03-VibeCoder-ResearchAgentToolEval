# Bảo vệ nhánh dev

## Quy trình làm việc

1. Tạo nhánh cá nhân từ dev; commit và push vào nhánh cá nhân.
2. Mở PR có base là dev; chờ job `offline-tests` pass.
3. `justcoffeee` review và approve phiên bản hiện tại; xử lý hết review conversation.
4. Nếu có thay đổi mới làm approval bị stale, cần review/approve lại; cập nhật nhánh nếu dev đã đổi.
5. Chỉ merge khi GitHub xác nhận đủ mọi yêu cầu. Không push trực tiếp, force-push hoặc xóa dev.

## Cấu hình mục tiêu

- Ruleset active, chỉ áp dụng `refs/heads/dev`, không áp dụng nhánh cá nhân.
- Required PR: ít nhất 1 approval, bắt buộc Code Owner review, dismiss stale approvals,
  bắt buộc giải quyết review threads.
- `.github/CODEOWNERS` chỉ định `justcoffeee` cho mọi file và cả `.github/`.
  Không thêm rule phía dưới làm thay thế owner.
- Required status check: `offline-tests`, nguồn GitHub Actions; nhánh phải cập nhật với dev.
- Chặn non-fast-forward (force-push) và xóa dev.
- Bypass list rỗng; không có ngoại lệ cho admin hoặc PR do nhóm trưởng tạo.
- Không bật thêm last-push approval: stale-approval dismissal đã yêu cầu duyệt lại khi diff đổi.

## PR do justcoffeee tạo

Nhóm đã chọn chính sách nghiêm ngặt: không bypass yêu cầu review của justcoffeee.
GitHub không cho tác giả tự approve PR, nên PR do chính justcoffeee tạo không có đường
tự phê duyệt/ngoại lệ theo chính sách này. Không bỏ Code Owner rule, không tạm tắt ruleset
để tự merge. Nếu muốn cho phép các PR đó sau này, nhóm phải quyết định lại chính sách review.
Một admin vẫn có thể chỉnh/xóa cài đặt repo; danh sách bypass rỗng không tước quyền quản trị đó.

## CI an toàn

CI cài dependency rồi chạy unit/contract tests, không chạy eval/provider preflight hay chat live.
Không truyền API key hoặc Telegram token. Khi chạy test, credential liên quan được loại khỏi
environment; kết nối socket và DNS bị chặn. HTTP trong test phải được mock.
Job dùng token contents:read, checkout không lưu credential, action được pin theo commit SHA.
Các stub TODO của starter được phép skip; bất kỳ test failed nào đều làm job fail.

## Khởi tạo

PR bootstrap đưa CODEOWNERS và workflow vào dev trước khi bật ruleset để tránh yêu cầu
status check chưa tồn tại. Chỉ bật required check sau khi job thật đã chạy thành công.
Bootstrap là bước thiết lập ban đầu được người dùng yêu cầu, không phải bypass ruleset đang active.
