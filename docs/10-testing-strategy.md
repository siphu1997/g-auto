# Testing Strategy

## Testing goals
- Đảm bảo detector đủ ổn định
- Đảm bảo state machine không loop vô hạn
- Đảm bảo recovery hoạt động khi gặp lỗi phổ biến
- Đảm bảo thay template/profile không phá vỡ toàn hệ thống

## Unit tests
Test các phần:
- config loader
- retry policy
- timeout policy
- transition rules
- detector threshold logic
- OCR wrapper normalization

## Integration tests
- ADB client mock
- screenshot pipeline
- screen classification từ fixtures
- state machine flow cơ bản
- launch flow / reward flow / mail flow

## Golden-image tests
- Lưu bộ ảnh chuẩn cho từng screen
- Chạy matcher định kỳ trên dataset
- So sánh tỉ lệ detect đúng qua các phiên bản

## Manual test matrix
Nên test:
- app launch
- loading lâu
- popup bất thường
- disconnect
- unknown state
- reward flow
- mail flow
- daily flow
- quest flow
- train flow

## Metrics nên theo dõi
- detect success rate
- task success rate
- recovery success rate
- unknown state frequency
- restart frequency
- average task duration

## Regression workflow
1. Sau khi game update UI, recapture dataset
2. Re-run golden image tests
3. Chỉnh threshold/template nếu cần
4. Smoke test các flow chính
