from datetime import date
from pathlib import Path
from uuid import uuid4

import streamlit as st

import database


ADMIN_PASSWORD = "1"
BASE_DIR = Path(__file__).parents[1]
IMAGE_DIR = BASE_DIR / "assets" / "images"
ALLOWED_IMAGE_TYPES = {"jpg", "jpeg", "png", "webp"}


def format_price(price):
    return f"{price:,.0f}đ".replace(",", ".")


def save_uploaded_image(uploaded_image):
    if uploaded_image is None:
        return ""
    extension = Path(uploaded_image.name).suffix.lower().lstrip(".")
    if extension not in ALLOWED_IMAGE_TYPES:
        raise ValueError("Chỉ hỗ trợ ảnh JPG, JPEG, PNG hoặc WEBP.")
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    file_name = f"{uuid4().hex}.{extension}"
    file_path = IMAGE_DIR / file_name
    file_path.write_bytes(uploaded_image.getbuffer())
    return f"assets/images/{file_name}"


def render():
    st.markdown("## Bảng điều hành quán")
    menu_tab, orders_tab = st.tabs(["Quản lý menu", "Lịch sử đơn hàng"])
    with menu_tab:
        st.markdown("### Thêm món mới")
        with st.form("add_menu_form"):
            name = st.text_input("Tên món")
            price = st.number_input("Giá", min_value=0.0, step=1000.0)
            category = st.text_input("Danh mục")
            uploaded_image = st.file_uploader("Chọn ảnh món từ máy", type=sorted(ALLOWED_IMAGE_TYPES))
            description = st.text_input("Mô tả")
            if st.form_submit_button("Thêm món", type="primary"):
                if name.strip() and category.strip() and price > 0:
                    try:
                        image_url = save_uploaded_image(uploaded_image)
                    except ValueError as error:
                        st.error(str(error))
                    else:
                        database.add_menu_item(name, price, category, image_url, description)
                        st.success("Đã thêm món vào menu.")
                        st.rerun()
                else:
                    st.error("Vui lòng nhập tên, danh mục và giá hợp lệ.")
        st.markdown("### Menu hiện tại")
        for item in database.list_menu():
            with st.expander(f"{item['name']} - {format_price(item['price'])}"):
                with st.form(f"edit_{item['id']}"):
                    edited_name = st.text_input("Tên món", value=item["name"])
                    edited_price = st.number_input("Giá", min_value=0.0, value=float(item["price"]), step=1000.0)
                    edited_category = st.text_input("Danh mục", value=item["category"])
                    edited_image = st.text_input("Đường dẫn ảnh", value=item["image_url"] or "")
                    edited_description = st.text_input("Mô tả", value=item["description"] or "")
                    save_col, delete_col = st.columns(2)
                    with save_col:
                        save = st.form_submit_button("Lưu thay đổi")
                    with delete_col:
                        delete = st.form_submit_button("Xóa món")
                    if save:
                        database.update_menu_item(item["id"], edited_name, edited_price, edited_category, edited_image, edited_description)
                        st.rerun()
                    if delete:
                        database.delete_menu_item(item["id"])
                        st.rerun()
    with orders_tab:
        filter_col, phone_col = st.columns(2)
        with filter_col:
            selected_date = st.date_input("Ngày nhận đơn", value=None)
        with phone_col:
            phone = st.text_input("Tra theo số điện thoại")
        date_value = selected_date.isoformat() if isinstance(selected_date, date) else ""
        orders = database.list_orders(date_value, phone)
        if not orders:
            st.info("Chưa có đơn hàng phù hợp.")
        for order in orders:
            with st.container(border=True):
                st.markdown(f"**Đơn #{order['id']}** · {order['customer_name']} · Bàn {order['table_num']}")
                st.caption(f"{order['created_at']} · {order['phone']} · Tổng {format_price(order['total_price'])}")
                st.write(", ".join(f"{item['name']} x{item['quantity']}" for item in order["items"]))
                statuses = ["Chờ pha chế", "Đã xong", "Đã hủy"]
                status = st.selectbox("Trạng thái", statuses, index=statuses.index(order["status"]), key=f"status_{order['id']}")
                if status != order["status"] and st.button("Cập nhật trạng thái", key=f"update_{order['id']}"):
                    database.update_order_status(order["id"], status)
                    st.rerun()


def is_authenticated():
    if st.session_state.get("admin_authenticated"):
        return True
    password = st.sidebar.text_input("Mật khẩu chủ quán", type="password")
    if password:
        if password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.rerun()
        st.sidebar.error("Mật khẩu không đúng.")
    return False