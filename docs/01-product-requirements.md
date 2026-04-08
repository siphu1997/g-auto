# Product Requirements

## Product summary
Xây dựng một framework automation chạy nền cho TLBB trên Android emulator, có khả năng nhận diện màn hình game, thực thi các thao tác định sẵn, phục hồi khi gặp trạng thái bất thường, và cung cấp dashboard local cho vận hành.

## Functional requirements

### Device control
- Kết nối emulator bằng ADB
- Chụp màn hình
- Tap, swipe, back, input text
- Launch/stop/restart app
- Kiểm tra emulator online/offline

### Vision
- Detect icon/button bằng template matching
- Detect screen qua multi-anchor signature
- OCR fallback cho vùng text hẹp
- Trả về confidence score và metadata

### Engine
- State machine rõ ràng theo state hiện tại
- Task runner cho các flow business
- Retry policy
- Watchdog chống treo
- Recovery flow nhiều cấp

### Business flows v1
- Launch flow: mở game và vào HOME_SCREEN
- Claim reward flow
- Claim mail flow
- Daily flow cơ bản
- Quest flow cơ bản
- Train flow cơ bản nếu state đủ rõ

### Dashboard
- Xem trạng thái hiện tại
- Xem task đang chạy
- Xem screenshot mới nhất
- Xem logs
- Start / stop / restart bot
- Trigger task thủ công
- Reload config

### Configuration
- Config emulator
- Config bot runtime
- Config task enable/disable
- Config timeout / retry / schedule
- Profile theo resolution

## Non-functional requirements
- Bot phải có log cấu trúc
- Chụp screenshot khi fail hoặc recovery
- Có khả năng restart app khi stuck
- Có unknown-state handling
- Hỗ trợ chạy ổn định trong thời gian dài
- Dễ thay template và chỉnh threshold sau update game

## Scope v1
- 1 account
- 1 instance
- LDPlayer 9
- Windows
- Python bot core
- Dashboard local
- Template matching + OCR fallback

## Out of scope v1
- Multi-account
- Tự động đổi account
- Multi-instance parallel orchestration
- Support nhiều emulator đồng thời
- Android phone thật
- iOS
- ML model riêng cho recognition
- Pathfinding nâng cao
- Cloud dashboard

## Success criteria
- Launch game và vào HOME_SCREEN ổn định
- Claim reward/mail thành công với tỉ lệ cao
- Handle popup phổ biến
- Recovery được khi loading lâu, unknown state, app crash
- Có dashboard local usable
- Có artifact debug đủ để sửa lỗi nhanh

## Constraints
- UI game có thể thay đổi sau update
- OCR tiếng Việt trong game có thể không ổn định
- Emulator lag ảnh hưởng timing
- Cần khóa độ phân giải và DPI để giảm biến động
