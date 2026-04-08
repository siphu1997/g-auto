# Task Flows

## Launch flow
### Goal
Đưa bot từ trạng thái chưa chạy đến `HOME_SCREEN`

### Steps
1. kiểm tra emulator online
2. launch app
3. detect loading/login/select nếu có
4. chờ vào game
5. detect HOME_SCREEN
6. nếu fail -> recovery

## Claim reward flow
### Goal
Mở màn reward và nhận toàn bộ reward có thể claim

### Steps
1. precondition: HOME_SCREEN
2. tap entry reward
3. wait REWARD_SCREEN
4. detect các nút claim
5. claim theo rule
6. verify trạng thái đổi
7. quay về HOME_SCREEN

## Claim mail flow
### Goal
Nhận mail và reward liên quan

### Steps
1. precondition: HOME_SCREEN
2. vào mail screen
3. detect danh sách mail
4. claim all hoặc claim theo rule
5. verify xong
6. back về HOME_SCREEN

## Daily flow
### Goal
Thực hiện chuỗi daily đơn giản, ổn định

### Steps
1. đảm bảo HOME_SCREEN
2. đóng popup nếu có
3. đi qua từng module daily đã enable
4. claim và verify từng phần
5. log kết quả
6. return home

## Quest flow
### Goal
Tự thao tác nhiệm vụ ở mức UI-based

### Steps
1. detect quest panel hoặc quest button
2. tap quest/go/continue
3. chờ state change
4. handle popup nếu có
5. loop đến điều kiện dừng
6. recovery nếu stuck

## Train flow
### Goal
Train ở mức cơ bản khi có state đủ rõ

### Steps
1. vào train mode / screen tương ứng
2. bật action train
3. định kỳ monitor state
4. nếu interrupted -> resolve rồi resume
5. nếu timeout hoặc bất thường -> return home, log, stop flow

## Flow guard rails
- Flow chỉ chạy khi precondition hợp lệ
- Mỗi bước phải có timeout
- Mỗi bước quan trọng phải verify
- Không loop vô hạn
