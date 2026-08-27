## Website

[Đăng Coffee · Streamlit]
https://quan-nuoc-order-rsckzv8cw4dnd4s6offztv.streamlit.app/

## 1. Tải dự án lần đầu và cài thư viện

> Chỉ thực hiện các bước này một lần trên mỗi máy.

Cài Git. Nếu muốn chạy thử project trên máy, cài thêm Python. Mở PowerShell, chọn thư mục bất kỳ mà bạn muốn lưu project, rồi chạy:

```powershell
git clone https://github.com/DO2DANG/quan-nuoc-order.git
cd quan-nuoc-order
python -m pip install -r requirements.txt
```

## 2. Các thao tác lấy code về và đẩy code lên

Trước khi sửa code, lấy thay đổi mới nhất của đồng đội:

```powershell
cd ĐƯỜNG_DẪN_ĐẾN\quan-nuoc-order
git pull origin main
```

Sau khi sửa và kiểm tra code, đẩy thay đổi lên GitHub:

```powershell
git add .
git commit -m "Mo ta ngan gon thay doi"
git push origin main
```

Mọi người cùng làm việc trực tiếp trên nhánh `main`, không cần tạo nhánh mới. Nếu Git báo xung đột, mở file được báo, chọn nội dung đúng, lưu lại rồi chạy lại các lệnh `git add`, `git commit` và `git push`.

## 3. Tùy chỉnh

- Sửa món, giá, mô tả và danh mục trong `data/menu.json`.
- Thay các file placeholder trong `assets/images/` bằng ảnh thật, giữ nguyên tên file hoặc cập nhật trường `image` trong JSON.
- Chỉnh màu sắc và giao diện Streamlit trong `.streamlit/config.toml`.

## 4. Lưu ý

- Chỉ chạy `git clone` một lần trên mỗi máy; những lần sau dùng `git pull` để cập nhật.
- Nếu chỉ muốn lấy thay đổi mới, dùng `git pull`; không clone lại project.
- Không commit mật khẩu, API key hoặc file `.env`.
- `requirements.txt` và `app.py` phải được gọi khi PowerShell đang ở đúng thư mục project.
- Sửa món trong `data/menu.json`, ảnh trong `assets/images/`, giao diện trong `.streamlit/config.toml` và logic trong `app.py`.
- Sau khi `git push origin main`, Streamlit Cloud sẽ tự triển khai phiên bản mới nếu đã bật kết nối và tự động deploy.
