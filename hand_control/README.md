# Hand Control

Ứng dụng điều khiển một số thao tác trên máy tính bằng cử chỉ bàn tay trước camera. Ứng dụng dùng OpenCV để đọc camera, MediaPipe để nhận diện bàn tay và PyAutoGUI để điều khiển chuột, phím và chụp ảnh màn hình.

## Tính năng

- Điều khiển con trỏ, nhấp chuột và cuộn trang.
- Điều chỉnh âm lượng bằng khoảng cách giữa ngón cái và ngón trỏ.
- Điều chỉnh độ sáng bằng vị trí ngón trỏ (cần cài `screen-brightness-control`).
- Chụp ảnh màn hình bằng cử chỉ chữ V.
- Hiển thị chế độ, trạng thái và FPS trên hình ảnh camera.

## Yêu cầu

- Python 3.9 trở lên.
- Camera được kết nối và quyền truy cập camera.
- Các thư viện Python:

```bash
python -m pip install opencv-python mediapipe numpy pyautogui
```

Tùy chọn:

```bash
python -m pip install screen-brightness-control
```

Trên Windows, để điều khiển âm lượng trực tiếp thay vì mô phỏng phím volume, cài thêm:

```bash
python -m pip install pycaw comtypes
```

Nếu không có `pycaw`, ứng dụng sẽ thử điều chỉnh âm lượng bằng phím volume. Nếu không có `screen-brightness-control`, các chế độ khác vẫn dùng được nhưng không thể thay đổi độ sáng.

## Chạy ứng dụng

Từ thư mục gốc của repository:

```bash
python -m hand_control.app
```

Khi chạy lần đầu, ứng dụng tự tải model `hand_landmarker.task` nếu chưa tìm thấy file trong thư mục làm việc hiện tại. Cần có kết nối Internet để tải model. Nhấn `q` khi cửa sổ camera đang hoạt động để thoát.

## Chọn chế độ

Nhấn phím `1`–`4`, hoặc nắm tay khoảng 0,8 giây để vào chế độ chọn. Sau đó giơ số ngón tương ứng và giữ khoảng 0,6 giây:

| Phím / số ngón | Chế độ |
|---|---|
| `1` | Chuột |
| `2` | Âm lượng |
| `3` | Độ sáng |
| `4` | Chụp màn hình |

Khi chọn bằng cử chỉ, số ngón được đếm là các ngón trỏ, giữa, áp út và út; ngón cái không được tính. Có thể chọn trong vòng 6 giây.

## Cử chỉ

### Chuột

- Giơ riêng ngón trỏ: di chuyển con trỏ.
- Chụm ngón cái với ngón giữa: nhấp chuột trái.
- Chụm ngón trỏ với ngón út: nhấp chuột phải.
- Giơ riêng ngón giữa: cuộn lên.
- Giơ riêng ngón út: cuộn xuống.

### Âm lượng

Giữ các ngón giữa, áp út và út co xuống; thay đổi khoảng cách giữa đầu ngón cái và ngón trỏ để chỉnh âm lượng.

### Độ sáng

Giơ riêng ngón trỏ và di chuyển lên/xuống trong khung camera. Ngón trỏ càng cao thì độ sáng mục tiêu càng lớn.

### Chụp ảnh màn hình

Giữ ngón trỏ và ngón giữa thành chữ V khoảng 0,4 giây. Ảnh được lưu trong thư mục `screenshots` ở thư mục gốc repository; thời gian chờ giữa hai lần chụp là 2 giây.

## Cấu trúc mã nguồn

- `app.py`: vòng lặp chính, đọc camera và điều phối chế độ.
- `camera.py`: khởi tạo camera và MediaPipe Hand Landmarker.
- `config.py`: cấu hình và các ngưỡng cử chỉ.
- `hand_utils.py`: tính toán cử chỉ, kích thước bàn tay và vẽ landmark.
- `mode_selection.py`: chọn chế độ bằng cử chỉ.
- `media_controls.py`: điều khiển âm lượng và độ sáng.
- `state.py`: trạng thái dùng chung của ứng dụng.
- `ui.py`: vẽ thông tin trạng thái lên cửa sổ camera.
- `modes/`: các bộ xử lý riêng cho chuột, âm lượng, độ sáng và chụp ảnh.

## Khắc phục sự cố

- **Không mở được camera:** kiểm tra camera đang kết nối, quyền truy cập và thử đóng ứng dụng khác đang sử dụng camera.
- **Không tải được model:** kiểm tra kết nối Internet hoặc đặt `hand_landmarker.task` trong thư mục làm việc trước khi chạy.
- **Không thay đổi được độ sáng:** cài `screen-brightness-control`; khả năng hỗ trợ còn phụ thuộc phần cứng và hệ điều hành.
- **Nhận diện chưa ổn định:** giữ bàn tay trong khung hình, đủ sáng và tránh che khuất các ngón.
