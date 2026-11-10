# Bảo vệ nhánh dev

## Quy trình làm việc

1. Tạo nhánh cá nhân từ dev; commit và push vào nhánh cá nhân.
2. Mở PR có base là dev; chờ job `offline-tests` pass.
3. Với PR của thành viên khác, `justcoffeee` review và approve phiên bản hiện tại; xử lý hết review conversation.
4. Nếu có thay đổi mới làm approval bị stale, cần review/approve lại; cập nhật nhánh nếu dev đã đổi.
5. Chỉ merge khi GitHub xác nhận đủ mọi yêu cầu. Không push trực tiếp, force-push hoặc xóa dev.
   PR do `justcoffeee` tạo có thể tự merge sau khi `offline-tests` pass.

## Cấu hình mục tiêu

- Ruleset active, chỉ áp dụng `refs/heads/dev`, không áp dụng nhánh cá nhân.
- Ruleset review: ít nhất 1 approval, bắt buộc Code Owner review, dismiss stale approvals,
  bắt buộc giải quyết review threads. `justcoffeee` có bypass actor ở chế độ PR-only;
  các yêu cầu review này vẫn áp dụng cho thành viên khác.
- `.github/CODEOWNERS` chỉ định `justcoffeee` cho mọi file và cả `.github/`.
  Không thêm rule phía dưới làm thay thế owner.
- Required status check: `offline-tests`, nguồn GitHub Actions; nhánh phải cập nhật với dev.
  Check được áp dụng thêm bởi ruleset riêng không có bypass, nên `justcoffeee` cũng phải chờ CI pass.
- Chặn non-fast-forward (force-push) và xóa dev.
- `justcoffeee` chỉ có bypass qua PR; không được bypass bằng push trực tiếp.
- Không bật thêm last-push approval: stale-approval dismissal đã yêu cầu duyệt lại khi diff đổi.

## PR do justcoffeee tạo

GitHub không cho tác giả tự approve PR. Vì vậy, tài khoản `justcoffeee` được thêm làm bypass
actor ở chế độ `pull_request` cho ruleset review; tài khoản có thể merge PR mà không tự approve.
GitHub gắn bypass với người merge, không kiểm tra PR có do người đó tạo hay không: `justcoffeee`
có thể bỏ qua yêu cầu review khi merge bất kỳ PR nào. Ruleset CI riêng không có bypass và vẫn
bắt buộc `offline-tests` pass. Bypass PR-only không cho phép push trực tiếp lên `dev`.

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
