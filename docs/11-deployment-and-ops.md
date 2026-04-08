# Deployment and Operations

## Target environment v1
- Windows PC
- LDPlayer 9
- 1 instance game
- fixed resolution
- fixed DPI
- ADB hoạt động ổn định

## Bootstrap steps
1. cài LDPlayer 9
2. cài game
3. khóa resolution và DPI
4. bật ADB
5. xác nhận adb serial
6. capture baseline screenshots
7. validate template profile
8. start worker
9. start dashboard

## Runtime checklist
- Emulator online
- Đúng package game
- Đúng adb serial
- Đúng profile template theo resolution
- Log path writable
- Screenshot path writable
- Dashboard kết nối được worker

## Ops procedures

### Khi bot treo
1. xem current screenshot
2. xem current state
3. xem log recovery
4. restart bot
5. nếu lặp lại -> kiểm tra template/profile

### Khi game update UI
1. recapture dataset
2. cắt lại template cần thiết
3. chỉnh threshold
4. rerun regression tests
5. smoke test các flow chính

## Safety recommendations
- Không test bằng tài khoản chính
- Tách môi trường dev và môi trường chạy thực
- Backup config và template dataset
- Lưu run history để trace lỗi sau này
