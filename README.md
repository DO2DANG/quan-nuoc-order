# Quan Nuoc Order

Ứng dụng đặt nước xây dựng bằng Streamlit, gồm giao diện khách hàng và khu vực quản trị đơn hàng, menu và thanh toán VietQR.

## Website

[Nhóm 27 Coffee · Streamlit](https://quan-nuoc-order-rsckzv8cw4dnd4s6offztv.streamlit.app/)

## Cài đặt và chạy chương trình

### Yêu cầu

- Python 3.10 trở lên.
- Git nếu cần tải mã nguồn từ GitHub.

### Cài đặt lần đầu

Mở PowerShell tại thư mục muốn lưu dự án và chạy:

```powershell
git clone https://github.com/DO2DANG/quan-nuoc-order.git
Set-Location quan-nuoc-order
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Nếu PowerShell không cho phép kích hoạt môi trường, có thể chạy lệnh sau một lần với quyền người dùng hiện tại:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Chạy ứng dụng

```powershell
Set-Location E:\BTL-PYTHON\quan-nuoc-order
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

Mở địa chỉ được Streamlit hiển thị: `http://localhost:8501`.
Dừng chương trình bằng `Ctrl + C`.

## Cấu trúc dự án

```text
quan-nuoc-order/
|-- .streamlit/
|   `-- config.toml
|-- assets/
|   `-- images/
|-- data/
|   `-- menu_mac_dinh.json
|-- views/
|   |-- admin.py
|   `-- customer.py
|-- app.py
|-- database.py
|-- requirements.txt
|-- README.md
`-- .gitignore
```

Sau lần chạy đầu tiên, chương trình có thể tạo `orders.db` để lưu dữ liệu SQLite. Thư mục `.venv/` là môi trường Python riêng và không phải mã nguồn.

### Lưu dữ liệu ổn định trên Streamlit Cloud

SQLite chỉ phù hợp khi chạy local vì filesystem của Streamlit Cloud có thể bị tạo lại. Để tất cả phiên truy cập dùng chung dữ liệu và không mất đơn sau khi app restart:

1. Tạo một project Supabase, mở SQL Editor và chạy toàn bộ file `supabase_schema.sql`.
2. Trong Streamlit Cloud, vào **Settings > Secrets** và thêm:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

3. Redeploy app. Khi hai Secret này tồn tại, ứng dụng dùng Supabase cho menu, đơn hàng, trạng thái và mã giảm giá; khi chạy local không có Secret, ứng dụng tự dùng `orders.db`.

Chính sách trong file SQL cho phép ứng dụng demo đọc/ghi bằng anon key. Với website thật, nên thêm đăng nhập và thu hẹp Row Level Security trước khi đưa vào sử dụng rộng rãi.

## Tác dụng của các file và thư mục

- `app.py`: điểm khởi động ứng dụng, điều hướng giữa giao diện khách hàng và chủ quán.
- `database.py`: khởi tạo cơ sở dữ liệu SQLite, nạp menu ban đầu và cung cấp thao tác với món, khách hàng và đơn hàng.
- `views/customer.py`: hiển thị menu, giỏ hàng, thông tin khách, thanh toán VietQR và tạo đơn hàng.
- `views/admin.py`: đăng nhập quản trị, thêm/sửa/xóa món, tra cứu đơn và cập nhật trạng thái đơn.
- `data/menu_mac_dinh.json`: dữ liệu menu ban đầu. Mỗi món gồm `id`, `name`, `category`, `description`, `price`, `image` và `emoji`.
- `assets/images/`: ảnh món uống và logo. Khi thêm món từ giao diện quản trị, chủ quán có thể chọn ảnh trực tiếp từ máy; ảnh được lưu tự động vào thư mục này.
- `.streamlit/config.toml`: cấu hình màu sắc, font chữ và giao diện Streamlit.
- `requirements.txt`: danh sách thư viện Python cần cài cho dự án.
- `.gitignore`: danh sách file không đưa lên Git, như `.venv/`, cache và dữ liệu cục bộ.
- `README.md`: tài liệu cài đặt, chạy và giới thiệu dự án.
- `orders.db`: cơ sở dữ liệu được tạo tự động khi chạy ứng dụng; không cần tạo thủ công.

## Cập nhật và phát triển

Lấy thay đổi mới nhất trước khi làm việc:

```powershell
git pull origin main
```

Sau khi kiểm tra thay đổi:

```powershell
git add .
git commit -m "Mo ta ngan gon thay doi"
git push origin main
```

Để thêm món mặc định, chỉnh `data/menu_mac_dinh.json` hoặc sử dụng giao diện quản trị. Khi thêm món trên web, chọn ảnh JPG, JPEG, PNG hoặc WEBP từ máy; ứng dụng sẽ tự lưu ảnh vào `assets/images/`. Có thể chỉnh màu và giao diện trong `.streamlit/config.toml`.

Khu vực **Chủ quán** hiện dùng mật khẩu demo `1`; cần đổi mật khẩu trong `views/admin.py` trước khi triển khai thật. Thông tin VietQR mặc định cũng chỉ dùng cho mục đích demo.
