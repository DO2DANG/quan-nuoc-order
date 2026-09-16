from pathlib import Path
from urllib.parse import quote

import streamlit as st

import database


BASE_DIR = Path(__file__).parents[1]


def format_price(price):
    return f"{price:,.0f}đ".replace(",", ".")


def render():
    menu = database.list_menu()
    st.markdown("## Đặt nước tại Nhóm 27 coffee")
    st.caption("Chọn món, xác nhận thông tin và thanh toán bằng VietQR.")
    if "cart" not in st.session_state:
        st.session_state.cart = {}
    if "customer_discount" not in st.session_state:
        st.session_state.customer_discount = 0
    categories = ["Tất cả"] + sorted({item["category"] for item in menu})
    selected_category = st.selectbox("Danh mục", categories)
    filtered_menu = [item for item in menu if selected_category == "Tất cả" or item["category"] == selected_category]
    menu_column, cart_column = st.columns([1.7, 1], gap="large")
    with menu_column:
        product_columns = st.columns(2)
        for index, item in enumerate(filtered_menu):
            with product_columns[index % 2]:
                image_path = BASE_DIR / item["image_url"] if item["image_url"] else None
                if image_path and image_path.exists():
                    st.image(str(image_path), use_container_width=True)
                st.markdown(f"### {item['name']}")
                st.caption(item["description"] or item["category"])
                st.markdown(f"**{format_price(item['price'])}**")
                if st.button("+ Thêm vào giỏ", key=f"add_{item['id']}", use_container_width=True):
                    st.session_state.cart[item["id"]] = st.session_state.cart.get(item["id"], 0) + 1
                    st.toast(f"Đã thêm {item['name']}")
    with cart_column:
        st.markdown("### Giỏ hàng")
        selected_items = [item for item in menu if st.session_state.cart.get(item["id"], 0) > 0]
        if not selected_items:
            st.info("Giỏ hàng đang trống.")
            return
        order_items = []
        subtotal = 0
        for item in selected_items:
            quantity = st.number_input(f"{item['name']} ({format_price(item['price'])})", min_value=1, max_value=20, value=st.session_state.cart[item["id"]], key=f"qty_{item['id']}")
            st.session_state.cart[item["id"]] = quantity
            subtotal += item["price"] * quantity
            order_items.append({"name": item["name"], "quantity": quantity, "price": item["price"]})
        voucher = st.text_input("Mã giảm giá (nếu có)").strip()
        if st.button("Áp dụng mã"):
          if voucher:
            # Gọi hàm lấy % giảm từ database do chủ quán tạo
            discount_percent = database.get_discount_percent(voucher)
            if discount_percent > 0:
              st.session_state.customer_discount_percent = discount_percent
              st.success(
                  f"Đã áp dụng mã thành công! Giảm {discount_percent}%"
              )
            else:
              st.session_state.customer_discount_percent = 0
              st.error("Mã giảm giá không hợp lệ hoặc đã hết hạn.")
          else:
            st.session_state.customer_discount_percent = 0
            st.warning("Vui lòng nhập mã giảm giá.")

        # Lấy % giảm giá từ session (mặc định là 0 nếu chưa có)
        current_discount_percent = st.session_state.get(
            "customer_discount_percent", 0
        )

        # Tính tiền giảm theo phần trăm (%) thay vì trừ tiền cố định
        discount_amount = subtotal * (current_discount_percent / 100)
        total = max(0, subtotal - discount_amount)

        st.markdown(f"Tạm tính: **{format_price(subtotal)}**")
        if current_discount_percent > 0:
          st.markdown(
              f"Giảm giá ({current_discount_percent}%):"
              f" **-{format_price(discount_amount)}**"
          )
        st.markdown(f"Tổng thanh toán: **{format_price(total)}**")
        with st.form("customer_order_form"):
            st.markdown("#### Xác nhận đơn hàng")
            customer_name = st.text_input("Tên khách hàng")
            customer_phone = st.text_input("Số điện thoại")
            table_num = st.text_input("Số bàn")
            submitted = st.form_submit_button("Tiếp tục thanh toán", type="primary", use_container_width=True)
        if submitted:
            if not customer_name.strip() or not customer_phone.strip() or not table_num.strip():
                st.error("Vui lòng nhập đủ tên, số điện thoại và số bàn.")
            else:
                st.session_state.pending_order = {"name": customer_name, "phone": customer_phone, "table_num": table_num, "items": order_items, "total": total}
        pending_order = st.session_state.get("pending_order")
        if pending_order:
            st.divider()
            st.markdown("#### Thanh toán VietQR")
            st.write(f"Đơn của **{pending_order['name']}** - {format_price(pending_order['total'])}")
            bank_code = st.text_input("Mã ngân hàng nhận tiền", value="VCB", key="bank_code")
            account_number = st.text_input("Số tài khoản nhận tiền", value="0123456789", key="account_number")
            qr_url = f"https://img.vietqr.io/image/{quote(bank_code)}-{quote(account_number)}-compact2.png?amount={int(pending_order['total'])}&addInfo={quote('Thanh toan don ' + pending_order['name'])}"
            st.image(qr_url, caption="Quét mã để thanh toán", width=260)
            if st.button("Đã hoàn thành thanh toán", type="primary", use_container_width=True):
                order_id = database.save_order(pending_order["name"], pending_order["phone"], pending_order["table_num"], pending_order["items"], pending_order["total"])
                st.session_state.cart = {}
                st.session_state.customer_discount_percent = ()
                del st.session_state.pending_order
                st.success(f"Đã nhận đơn #{order_id}. Trạng thái: Chờ pha chế.")