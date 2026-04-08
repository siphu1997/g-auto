# Dashboard

## Purpose
Dashboard là công cụ local cho vận hành, không phải sản phẩm web hoàn chỉnh.

## Core features
- xem bot status
- xem emulator status
- xem current task
- xem current state
- xem latest screenshot
- xem logs gần nhất
- start / stop / restart bot
- trigger task thủ công
- reload config

## Suggested pages

### Home
- Bot status
- Emulator status
- Current task
- Current state
- Uptime
- Last action

### Logs
- Filter theo module
- Filter theo level
- Tail log realtime

### Screenshots
- Latest screenshot
- Latest error screenshot
- Gallery theo run

### Tasks
- Danh sách task enabled
- Trigger task
- Pause/resume

### Config
- Hiển thị config hiện tại
- Reload config

## Suggested API endpoints
```text
GET    /health
GET    /status
GET    /logs
GET    /screenshots/latest
POST   /bot/start
POST   /bot/stop
POST   /bot/restart
POST   /tasks/run
POST   /config/reload
```

## Implementation options
### Option A
- FastAPI + Jinja/HTML
- Nhanh và đơn giản

### Option B
- FastAPI + React/Vite
- UI đẹp hơn, linh hoạt hơn

Khuyến nghị v1:
- FastAPI + dashboard local nhẹ, tập trung vào usability hơn design
