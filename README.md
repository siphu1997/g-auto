# TLBB Automation Framework

Framework automation cho game mobile trên Android emulator, thiết kế theo hướng ổn định, dễ debug, dễ mở rộng.

## Scope v1
- Emulator: LDPlayer 9
- Platform: Windows
- Mode: 1 account / 1 instance
- Recognition: template matching + OCR fallback
- Runtime: background worker + local dashboard
- Flows: launch, reward, mail, daily, quest, basic train

## Core principles
- Stability first
- Image recognition first, OCR second
- Deterministic state machine
- Retry + timeout + recovery everywhere
- Rich logs + screenshots for debugging

## Suggested repository structure
```text
tlbb-auto/
├─ README.md
├─ apps/
├─ src/
├─ config/
├─ data/
├─ docs/
├─ scripts/
└─ tests/
```

## Documentation
- [docs/00-overview.md](docs/00-overview.md)
- [docs/01-product-requirements.md](docs/01-product-requirements.md)
- [docs/02-architecture.md](docs/02-architecture.md)
- [docs/03-state-machine.md](docs/03-state-machine.md)
- [docs/04-vision-system.md](docs/04-vision-system.md)
- [docs/05-device-control.md](docs/05-device-control.md)
- [docs/06-task-flows.md](docs/06-task-flows.md)
- [docs/07-config-schema.md](docs/07-config-schema.md)
- [docs/08-logging-and-debugging.md](docs/08-logging-and-debugging.md)
- [docs/09-dashboard.md](docs/09-dashboard.md)
- [docs/10-testing-strategy.md](docs/10-testing-strategy.md)
- [docs/11-deployment-and-ops.md](docs/11-deployment-and-ops.md)
- [docs/12-roadmap.md](docs/12-roadmap.md)

## Suggested next steps
1. Khởi tạo repo skeleton theo cấu trúc tài liệu
2. Implement device layer trước
3. Capture dataset cho recognition
4. Build screen classifier
5. Build state machine + recovery
6. Implement launch/reward/mail trước rồi mới mở rộng

## Notes
- Nên khóa resolution và DPI ngay từ đầu
- Không nên hỗ trợ nhiều emulator ở phase đầu
- Không nên dựa hoàn toàn vào OCR
