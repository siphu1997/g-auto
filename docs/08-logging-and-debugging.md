# Logging and Debugging

## Goals
- Dễ trace vì sao bot fail
- Dễ reproduce issue sau update UI
- Có artifact đủ để fix nhanh

## Log categories
- system
- device
- vision
- state_machine
- task
- recovery
- api
- dashboard

## Structured log example
```json
{
  "timestamp": "2026-04-08T10:00:00Z",
  "level": "INFO",
  "module": "state_machine",
  "event": "state_changed",
  "from_state": "LOADING_SCREEN",
  "to_state": "HOME_SCREEN",
  "task": "launch",
  "run_id": "run_001"
}
```

## Screenshot policy
Phải chụp screenshot khi:
- state unknown
- action fail
- recovery start
- recovery fail
- task finish
- user trigger manual capture

## Naming convention
```text
data/screenshots/{date}/{run_id}/{timestamp}_{state}_{event}.png
```

## Debug modes
### Normal mode
- log vừa đủ
- screenshot khi lỗi

### Debug mode
- log chi tiết
- lưu detection overlay
- screenshot thường xuyên hơn

## Recommended debug artifacts
- full screenshot
- cropped regions cho detector
- overlay đánh dấu anchors detect được
- OCR text output
- state snapshot trước và sau action

## Failure analysis checklist
1. Bot đang ở state nào trước khi fail
2. Detector có confidence bao nhiêu
3. Action nào vừa chạy
4. UI có thay đổi như kỳ vọng không
5. Recovery có được kích hoạt không
6. Có cần recapture template hay chỉnh threshold không
