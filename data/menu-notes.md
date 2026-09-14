# Lưu ý về `menu_mac_dinh.json`

## Công dụng

`menu_mac_dinh.json` lưu danh sách món ăn và đồ uống ban đầu của quán dưới dạng JSON. Khi ứng dụng chạy lần đầu, `database.py` đọc file này và nạp dữ liệu vào bảng `menu` trong cơ sở dữ liệu `orders.db`.

## Lưu ý khi chỉnh sửa

- Không xóa dấu `[` ở đầu hoặc dấu `]` ở cuối file.
- Mỗi món phải được viết trong một cặp dấu `{}` và các món phải được ngăn cách bằng dấu phẩy.
- `id` của mỗi món phải khác nhau.
- `price` phải là số và không đặt trong dấu ngoặc kép.
- Các trường thường dùng gồm `id`, `name`, `category`, `description`, `price`, `image` và `emoji`.
- Đường dẫn trong trường `image` phải trỏ đến file ảnh tồn tại trong thư mục `assets/images/`.
- Khi thêm món bằng giao diện quản trị, có thể chọn ảnh trực tiếp từ máy; ứng dụng sẽ tự lưu ảnh vào `assets/images/`.
- Không thêm chú thích bằng `//` hoặc `/* ... */` vì JSON không hỗ trợ chú thích.
- Sau khi chỉnh sửa, cần kiểm tra file vẫn đúng cú pháp JSON.

## Quan hệ với website

- File này là dữ liệu menu ban đầu, không phải nơi lưu dữ liệu quản trị trực tiếp.
- Thêm, sửa hoặc xóa món trong giao diện quản trị sẽ cập nhật `orders.db`, không tự động cập nhật `menu_mac_dinh.json`.
- Nếu `orders.db` đã có menu, thay đổi trong `menu_mac_dinh.json` sẽ không tự động xuất hiện trên website.
- Muốn nạp lại `menu_mac_dinh.json`, cần xử lý hoặc cập nhật lại dữ liệu trong `orders.db` một cách cẩn thận để không làm mất đơn hàng.
