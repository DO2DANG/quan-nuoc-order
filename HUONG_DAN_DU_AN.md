# Hướng dẫn dự án Quan Nuoc Order

Tài liệu này giải thích cấu trúc, tác dụng và các thao tác có thể thực hiện trong dự án đặt nước bằng Streamlit.

## 1. Cấu trúc dự án

```text
quan-nuoc-order/
|
|-- .streamlit/
|   `-- config.toml
|
|-- assets/
|   `-- images/
|       |-- ca-phe-sua.jpg
|       |-- tra-dao.jpg
|       `-- logo.png
|
|-- data/
|   `-- menu.json
|
|-- app.py
|-- requirements.txt
|-- README.md
|-- HUONG_DAN_DU_AN.md
`-- .gitignore
```

Ngoài ra, sau khi tạo môi trường ảo sẽ có thêm thư mục `.venv/`. Thư mục này chứa môi trường Python riêng và không phải mã nguồn của ứng dụng.

## 2. Tác dụng của từng file và thư mục

### `app.py`

Đây là file mã nguồn chính của ứng dụng.

Đang phụ trách:

- Đọc danh sách món từ `data/menu.json`.
- Hiển thị tiêu đề và giao diện quán nước.
- Lọc menu theo danh mục.
- Hiển thị món uống, giá và mô tả.
- Thêm món vào giỏ hàng.
- Điều chỉnh số lượng món.
- Tính tổng tiền.
- Nhận tên, số điện thoại và ghi chú của khách.
- Hiển thị thông báo khi đặt hàng thành công.

Các thao tác có thể làm:

- Sửa giao diện, màu sắc và nội dung hiển thị.
- Thêm chức năng thanh toán hoặc lưu đơn hàng.
- Thêm lựa chọn size, đường, đá và topping.
- Kết nối cơ sở dữ liệu hoặc API.
- Thay đổi cách tính giá và phí giao hàng.

### `data/menu.json`

Lưu dữ liệu các món uống dưới dạng JSON. Mỗi món có các thông tin:

- `id`: mã duy nhất của món.
- `name`: tên món.
- `category`: danh mục.
- `description`: mô tả món.
- `price`: giá, dùng số nguyên theo đơn vị đồng.
- `image`: đường dẫn đến ảnh.
- `emoji`: hình thay thế nếu chưa có ảnh thật.

Các thao tác có thể làm:

- Sửa tên, giá, mô tả hoặc danh mục.
- Thêm món mới bằng cách sao chép một khối món hiện có.
- Xóa món không còn bán.
- Đổi đường dẫn ảnh trong trường `image`.

Ví dụ thêm món:

```json
{
  "id": "nuoc-chanh-tuoi",
  "name": "Nước chanh tươi",
  "category": "Nước giải khát",
  "description": "Chanh tươi pha mát lạnh.",
  "price": 25000,
  "image": "assets/images/tra-dao.jpg",
  "emoji": "🍋"
}
```

Lưu ý: `id` của mỗi món phải khác nhau. File JSON phải đúng dấu ngoặc, dấu phẩy và dùng dấu ngoặc kép quanh tên trường và nội dung.

### `assets/images/`

Chứa các hình ảnh minh họa cho món uống và logo.

Các thao tác có thể làm:

- Thay ảnh placeholder bằng ảnh thật.
- Thêm ảnh mới cho món mới.
- Đặt tên file không dấu, viết thường, không có khoảng trắng để dễ sử dụng.
- Cập nhật trường `image` trong `data/menu.json` khi đổi tên file.

Ví dụ:

```text
assets/images/nuoc-chanh-tuoi.jpg
```

Sau đó trong `menu.json` dùng:

```json
"image": "assets/images/nuoc-chanh-tuoi.jpg"
```

### `.streamlit/config.toml`

Cấu hình giao diện và cách Streamlit hoạt động.

Đang cấu hình:

- Màu chính của ứng dụng.
- Màu nền và màu chữ.
- Font chữ mặc định.
- Chế độ toolbar tối giản.
- Chế độ chạy server không mở cửa sổ phụ.

Các thao tác có thể làm:

- Đổi màu quán bằng cách sửa các mã màu HEX.
- Chọn giao diện sáng hoặc tối bằng trường `base`.
- Điều chỉnh cách hiển thị toolbar và thông báo lỗi.

### `requirements.txt`

Khai báo các thư viện Python cần cài. Hiện tại dự án sử dụng:

```text
streamlit
```

Các thao tác có thể làm:

- Thêm thư viện mới, mỗi thư viện một dòng.
- Ghim phiên bản, ví dụ `streamlit==1.38.0`.
- Cài lại thư viện sau khi chỉnh file:

```powershell
python -m pip install -r requirements.txt
```

### `README.md`

Hướng dẫn nhanh về cách cài đặt và chạy dự án.

Các thao tác có thể làm:

- Bổ sung hướng dẫn sử dụng.
- Ghi chú các tính năng mới.
- Thêm thông tin triển khai lên hosting.

### `HUONG_DAN_DU_AN.md`

File tài liệu này. Dùng để tra cứu cấu trúc và cách chỉnh sửa dự án.

Các thao tác có thể làm:

- Cập nhật tài liệu khi thêm file hoặc tính năng mới.
- Ghi lại quy ước đặt tên và cách vận hành riêng của quán.

### `.gitignore`

Liệt kê các file không nên đưa lên Git hoặc GitHub, ví dụ môi trường `.venv`, cache Python và file chứa thông tin bí mật.

Các thao tác có thể làm:

- Thêm các file riêng tư hoặc file sinh tự động cần bỏ qua.
- Không xóa dòng `.venv/` nếu muốn giữ môi trường ảo ngoài Git.

### `.venv/`

Môi trường Python riêng của project. Thư mục này được tạo bằng lệnh:

```powershell
python -m venv .venv
```

Các thao tác có thể làm:

- Kích hoạt môi trường:

```powershell
.\.venv\Scripts\Activate.ps1
```

- Thoát môi trường:

```powershell
deactivate
```

- Xóa và tạo lại nếu môi trường bị lỗi. Không sửa file bên trong `.venv` thủ công.

## 3. Các thao tác thường dùng

### Chạy ứng dụng

Mở PowerShell tại thư mục project:

```powershell
Set-Location E:\BTL-PYTHON\quan-nuoc-order
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

Mở địa chỉ được hiển thị, thường là `http://localhost:8501`.

### Dừng ứng dụng

Trong cửa sổ PowerShell đang chạy Streamlit, nhấn:

```text
Ctrl + C
```

### Cài thư viện lần đầu

```powershell
Set-Location E:\BTL-PYTHON\quan-nuoc-order
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Thêm một món mới

1. Mở `data/menu.json`.
2. Thêm một khối món mới trước dấu `]` cuối cùng.
3. Kiểm tra `id` không trùng món khác.
4. Lưu file.
5. Làm mới trang Streamlit.

### Thay ảnh món

1. Chép ảnh vào `assets/images/`.
2. Mở `data/menu.json`.
3. Sửa trường `image` cho đúng tên file.
4. Lưu file và làm mới ứng dụng.

### Thay đổi màu giao diện

1. Mở `.streamlit/config.toml`.
2. Sửa các giá trị như `primaryColor`, `backgroundColor` hoặc `textColor`.
3. Dừng và chạy lại Streamlit nếu giao diện chưa tự cập nhật.

## 4. Quy trình làm việc đề xuất

1. Kích hoạt `.venv`.
2. Sửa `menu.json` nếu chỉ thay đổi món và giá.
3. Sửa ảnh trong `assets/images/` nếu cần.
4. Sửa `app.py` nếu thay đổi logic hoặc thêm tính năng.
5. Chạy ứng dụng và thử thêm món, đổi số lượng, đặt hàng.
6. Kiểm tra lại JSON nếu ứng dụng báo lỗi khi đọc menu.
7. Cập nhật tài liệu này khi cấu trúc project thay đổi.
