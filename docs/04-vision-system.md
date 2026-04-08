# Vision System

## Strategy
v1 dùng hybrid strategy:
- 80–90%: template matching / icon detection
- 10–20%: OCR fallback cho text ngắn ở vùng hẹp

## Why template matching first
- Ổn định hơn OCR trong môi trường game
- Nhanh hơn
- Dễ debug hơn
- Ít false positive hơn nếu đã khóa resolution/DPI

## Recognition layers

### Layer 1: Anchor detection
Dùng để detect các icon/nút như:
- close
- quest
- reward
- mail
- minimap
- bag
- confirm/cancel
- loading indicator

### Layer 2: Screen signature
Mỗi screen được định nghĩa bằng tổ hợp anchor:
- HOME_SCREEN có minimap + quest panel + menu icon
- POPUP_SCREEN có overlay + popup box + confirm/cancel
- LOADING_SCREEN có loading indicator và thiếu home anchors

### Layer 3: OCR fallback
Chỉ dùng khi:
- popup khó phân biệt
- cần đọc timer/số lượng
- cần confirm text ngắn ở vùng cố định

## Confidence policy
- `>= 0.90`: high confidence
- `0.80–0.89`: medium confidence, cần verify thêm
- `< 0.80`: không dùng trực tiếp cho action

## Template management
Mỗi template nên có:
- name
- screen
- threshold
- search_region
- profile
- version

Ví dụ metadata:

```yaml
name: reward_claim_button
screen: reward_screen
threshold: 0.87
search_region: [900, 500, 1250, 700]
profile: ldplayer_1280x720
version: 1
```

## Dataset strategy
Thu thập:
- ảnh full-screen cho các screen chính
- ảnh popup phổ biến
- ảnh loading
- ảnh disconnect / lỗi / stuck

Quy tắc:
- mỗi screen tối thiểu 20–50 ảnh
- mỗi popup phổ biến tối thiểu 10 ảnh
- lưu theo emulator profile và resolution profile

## OCR guidance
Nên OCR:
- text ngắn
- số lượng
- timer
- popup title/subtitle

Không nên OCR:
- chat dài
- toàn màn hình
- text nhỏ có hiệu ứng nặng
- screen classification chính

## Best practices
- Chỉ search ở region có ý nghĩa
- Không template match toàn màn hình nếu không cần
- Verify sau click
- Lưu overlay debug khi detect fail
