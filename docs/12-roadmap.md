# Roadmap

## Phase 0 — Discovery
- Chốt emulator
- Chốt resolution/DPI
- Capture dataset ban đầu
- Xác định screen chính và popup phổ biến

## Phase 1 — Core framework
- ADB wrapper
- screenshot pipeline
- input controller
- logger
- config loader

## Phase 2 — Vision MVP
- template matcher
- anchor detector
- screen classifier
- OCR fallback cơ bản

## Phase 3 — State machine & recovery
- state registry
- transitions
- watchdog
- unknown-state policy
- app restart recovery

## Phase 4 — Business flows
- launch flow
- reward flow
- mail flow
- daily flow

## Phase 5 — Advanced v1
- quest flow
- basic train flow
- dashboard local
- metrics + better debug artifacts

## Suggested sprints

### Sprint 1
- repo skeleton
- device layer
- config + logger
- worker bootstrap

### Sprint 2
- vision MVP
- baseline templates
- screen classification

### Sprint 3
- state machine
- recovery
- unknown-state handling

### Sprint 4
- launch / reward / mail

### Sprint 5
- daily / quest / dashboard

### Sprint 6
- basic train / stability tuning / regression pack

## Future expansion
### v1.1
- detector accuracy improvements
- stronger recovery
- config editing on dashboard

### v1.2
- multi-instance
- schedule system mạnh hơn
- SQLite run history

### v2
- multi-account
- nhiều emulator profiles
- orchestration nâng cao

### v3
- plugin architecture cho nhiều game
- remote monitoring
