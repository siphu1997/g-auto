# Architecture

## High-level architecture

```text
+-----------------------------+
| Dashboard UI                |
| - status                    |
| - logs                      |
| - current screenshot        |
| - task control              |
+-------------+---------------+
              |
              v
+-----------------------------+
| Local API / Controller      |
| - start/stop bot            |
| - expose status             |
| - serve screenshots/logs    |
+-------------+---------------+
              |
              v
+-----------------------------+
| Bot Engine                  |
| - state machine             |
| - task runner               |
| - retry policy              |
| - watchdog                  |
+------+------+---------------+
       |      |
       |      v
       |   +------------------+
       |   | Vision Layer     |
       |   | - template match |
       |   | - anchor detect  |
       |   | - OCR fallback   |
       |   +------------------+
       |
       v
+-----------------------------+
| Device Layer                |
| - adb connect               |
| - screenshot                |
| - tap/swipe/input           |
| - launch/stop app           |
+-----------------------------+
```

## Module boundaries

### Device layer
Nhiệm vụ:
- giao tiếp trực tiếp với ADB
- cung cấp abstraction cho tap/swipe/screenshot/app lifecycle

### Vision layer
Nhiệm vụ:
- detect anchors
- classify screen
- OCR fallback
- trả về result có confidence và metadata

### State machine
Nhiệm vụ:
- xác định state hiện tại
- transition sang state tiếp theo
- gọi recovery khi cần

### Task engine
Nhiệm vụ:
- thực thi flow business
- định nghĩa precondition/postcondition
- tích hợp retry policy

### Watchdog
Nhiệm vụ:
- phát hiện stuck state
- phát hiện screenshot không đổi đáng kể
- escalates recovery

### Local API / dashboard
Nhiệm vụ:
- điều khiển worker
- hiển thị trạng thái, logs, screenshots
- trigger task và reload config

## Recommended stack
- Python cho core automation
- OpenCV + NumPy cho recognition
- OCR engine chỉ làm fallback
- FastAPI cho local API
- HTML đơn giản hoặc React/Vite cho dashboard

## Repository structure

```text
tlbb-auto/
├─ README.md
├─ apps/
│  ├─ api/
│  └─ worker/
├─ src/
│  ├─ core/
│  │  ├─ bot_engine/
│  │  ├─ state_machine/
│  │  ├─ task_engine/
│  │  ├─ device/
│  │  ├─ vision/
│  │  ├─ logging/
│  │  ├─ config/
│  │  └─ utils/
│  ├─ games/
│  │  └─ tlbb/
│  │     ├─ screens/
│  │     ├─ flows/
│  │     ├─ templates/
│  │     ├─ profiles/
│  │     └─ rules/
│  └─ dashboard/
├─ config/
├─ data/
├─ docs/
├─ scripts/
└─ tests/
```

## Design rules
- Không hard-code game rule vào core engine
- Rule theo game phải nằm trong `games/tlbb`
- Template phải versioned theo resolution profile
- Action quan trọng phải verify hậu quả
- Tất cả failure path phải log
