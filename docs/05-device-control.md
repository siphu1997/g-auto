# Device Control

## Device strategy
Thiết kế v1 chỉ hỗ trợ Android emulator qua ADB, ưu tiên LDPlayer 9.

## Core capabilities
- connect/disconnect
- screenshot
- tap
- swipe
- input_text
- key_back
- launch_app
- stop_app
- restart_app

## Recommended interface

```python
class DeviceController:
    def connect(self) -> bool: ...
    def is_online(self) -> bool: ...
    def screenshot(self): ...
    def tap(self, x: int, y: int) -> None: ...
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int) -> None: ...
    def input_text(self, text: str) -> None: ...
    def key_back(self) -> None: ...
    def launch_app(self, package_name: str) -> None: ...
    def stop_app(self, package_name: str) -> None: ...
    def restart_app(self, package_name: str) -> None: ...
```

## Emulator profile
Nên chuẩn hóa:
- emulator = LDPlayer 9
- fixed resolution
- fixed DPI
- fixed window size
- ADB serial cố định

Ví dụ:
- resolution: 1280x720
- dpi: 240

## Reliability rules
- Mỗi action nên có delay cấu hình được
- Sau action quan trọng phải verify
- Nếu screenshot fail thì retry
- Nếu ADB timeout liên tục thì escalate recovery

## Coordinate strategy
- Ưu tiên anchor-based tap
- Chỉ dùng tọa độ cứng khi UI cực kỳ ổn định
- Nếu dùng tọa độ cứng, phải relative theo profile

## App lifecycle
- Launch app khi boot flow bắt đầu
- Stop app khi recovery cần reset sạch
- Restart app khi stuck hoặc unknown quá nhiều
