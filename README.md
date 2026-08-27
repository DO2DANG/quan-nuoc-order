# Quan Nuoc Order

Ứng dụng đặt nước bằng Streamlit. Danh sách món được lưu trong `data/menu.json`.

## Tải dự án lần đầu

> Chỉ thực hiện các bước trong phần này một lần trên mỗi máy.

### 1. Cài phần mềm

Cài Python và Git. Khi cài Python trên Windows, nên chọn **Add Python to PATH**.

### 2. Tải mã nguồn từ GitHub

Mở PowerShell, chọn thư mục bất kỳ mà bạn muốn lưu project, rồi chạy:

```powershell
git clone https://github.com/DO2DANG/quan-nuoc-order.git
cd quan-nuoc-order
```

Bạn không cần lưu project tại ổ đĩa hoặc đường dẫn giống máy của người khác.

### 3. Tạo môi trường và cài thư viện

Các lệnh sau cần chạy trong thư mục `quan-nuoc-order`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Môi trường `.venv` chỉ cần tạo một lần. Nếu PowerShell hiện lỗi không cho chạy script, hãy chạy một lần:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Sau đó kích hoạt lại `.venv`.

## Chạy ứng dụng

Mỗi lần mở PowerShell mới, đi vào thư mục project và kích hoạt môi trường:

```powershell
cd ĐƯỜNG_DẪN_ĐẾN\quan-nuoc-order
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

Mở địa chỉ được hiển thị trong terminal, thường là `http://localhost:8501`. Dừng ứng dụng bằng `Ctrl + C`.

## Tùy chỉnh

- Sửa món, giá, mô tả và danh mục trong `data/menu.json`.
- Thay các file placeholder trong `assets/images/` bằng ảnh thật, giữ nguyên tên file hoặc cập nhật trường `image` trong JSON.
- Chỉnh màu sắc và giao diện Streamlit trong `.streamlit/config.toml`.

## Cập nhật và làm việc chung trên GitHub

Tất cả thành viên làm việc trực tiếp trên nhánh `main`, không cần tạo thêm nhánh.

### Trước khi sửa code

```powershell
cd ĐƯỜNG_DẪN_ĐẾN\quan-nuoc-order
git pull origin main
```

Hãy chạy lệnh này trước mỗi lần bắt đầu làm việc để tải thay đổi mới nhất của đồng đội.

### Sau khi sửa code

```powershell
git add .
git commit -m "Mo ta ngan gon thay doi"
git push origin main
```

Sau `git push`, thay đổi sẽ xuất hiện trên repository của tài khoản GitHub `DO2DANG`. Các thành viên khác dùng `git pull origin main` để tải về.

Nếu Git báo xung đột, mở file được báo, chọn nội dung đúng, lưu lại rồi chạy:

```powershell
git add .
git commit -m "Giai quyet xung dot"
git push origin main
```

Vì mọi người cùng sửa `main`, hãy báo cho đồng đội trước khi sửa cùng một file và luôn pull trước khi bắt đầu.

## Lưu ý

- Chỉ chạy `git clone` và tạo `.venv` một lần trên mỗi máy.
- Nếu chỉ muốn lấy thay đổi mới, dùng `git pull`; không clone lại project.
- Không commit mật khẩu, API key, file `.env` hoặc thư mục `.venv/`.
- `requirements.txt` và `app.py` phải được gọi khi PowerShell đang ở đúng thư mục project.
- Sửa món trong `data/menu.json`, ảnh trong `assets/images/`, giao diện trong `.streamlit/config.toml` và logic trong `app.py`.
