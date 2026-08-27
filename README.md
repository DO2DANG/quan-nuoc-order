# Quan Nuoc Order

Ứng dụng đặt nước đơn giản xây dựng bằng Streamlit. Menu được tách riêng trong `data/menu.json` để dễ chỉnh sửa.

## Chạy dự án

Mở PowerShell và chạy từ bất kỳ thư mục nào:

1. Đi vào đúng thư mục dự án:

   ```powershell
   Set-Location E:\BTL-PYTHON\quan-nuoc-order
   ```

2. Tạo và kích hoạt môi trường ảo:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Cài thư viện:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Khởi chạy ứng dụng:

   ```powershell
   python -m streamlit run app.py
   ```

Sau đó mở địa chỉ Streamlit hiển thị trong terminal, thường là `http://localhost:8501`.

### Nếu `.venv` đã tạo lỗi

Nếu trước đó bạn đã chạy lệnh tại `E:\BTL-PYTHON` và thấy lỗi `Unable to copy ... venvlauncher.exe`, hãy đóng terminal đang kích hoạt môi trường lỗi, xóa môi trường đó rồi tạo lại trong thư mục dự án:

```powershell
deactivate
Set-Location E:\BTL-PYTHON
Remove-Item -Recurse -Force .venv
Set-Location .\quan-nuoc-order
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Tùy chỉnh

- Sửa món, giá, mô tả và danh mục trong `data/menu.json`.
- Thay các file placeholder trong `assets/images/` bằng ảnh thật, giữ nguyên tên file hoặc cập nhật trường `image` trong JSON.
- Chỉnh màu sắc và giao diện Streamlit trong `.streamlit/config.toml`.
