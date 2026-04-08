# TLBB Automation Framework

## Overview
TLBB Automation Framework là bộ khung automation cho game mobile chạy trên Android emulator, được thiết kế để ưu tiên độ ổn định, khả năng debug, và khả năng mở rộng. Phiên bản v1 nhắm tới việc vận hành một account trên một instance LDPlayer 9, với các flow chính gồm launch game, claim reward, claim mail, daily flow, quest flow cơ bản, và train flow cơ bản.

## Project goals
- Điều khiển emulator và game ổn định qua ADB
- Nhận diện trạng thái UI bằng image recognition là chính, OCR là phụ
- Thực thi workflow bằng state machine rõ ràng, có retry, timeout, recovery
- Cung cấp dashboard local để theo dõi và điều khiển
- Dễ mở rộng về sau sang multi-instance, multi-account, plugin nhiều game

## Target v1
- Emulator: LDPlayer 9
- Platform: Windows PC
- Mode: 1 account / 1 instance
- Runtime: background worker + local dashboard
- Recognition: template matching + OCR fallback
- Tasks: launch, reward, mail, daily, quest, basic train

## Principles
- Ưu tiên stability hơn “thông minh”
- Ưu tiên deterministic rules hơn heuristic mơ hồ
- Ưu tiên một emulator chuẩn hơn hỗ trợ nhiều emulator cùng lúc
- Ưu tiên image recognition hơn OCR toàn màn hình
- Mọi action quan trọng đều cần verify
- Mọi failure path đều cần recovery plan

## Deliverables
- README.md cho repo
- Bộ docs trong `/docs/*.md`
- Cấu trúc module đề xuất
- State machine và task flow v1
- Chiến lược test, logging, deployment và roadmap
