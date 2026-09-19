from pathlib import Path
from urllib.parse import quote

import streamlit as st

import database


BASE_DIR = Path(__file__).parents[1]


def format_price(price):
    return f"{price:,.0f}đ".replace(",", ".")


def render():
    menu = database.list_menu()

    # ==============================
    # HIỂN THỊ HÓA ĐƠN SAU KHI ĐẶT HÀNG
    # ==============================
    if "last_order_id" in st.session_state:
        order_id = st.session_state.last_order_id
        order = database.get_order_by_id(order_id)

        if order:
            st.divider()
            st.subheader(f"🧾 Hóa đơn đơn hàng #{order['id']}")

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Tên khách hàng:** {order['name']}")
                st.write(f"**Số điện thoại:** {order['phone']}")
                st.write(f"**Số bàn:** {order['table_num']}")

            with col2:
                st.write(f"**Thời gian:** {order['created_at']}")
                st.write(f"**Trạng thái:** {order['status']}")

            st.markdown("### Chi tiết món hàng")

            for item in order["items"]:
                name = item["name"]
                quantity = item["quantity"]
                price = item["price"]
                amount = quantity * price

                st.write(
                    f"- **{name}** × {quantity}: "
                    f"{format_price(amount)}"
                )

            st.divider()

            st.markdown(
                f"## Tổng tiền: {format_price(order['total_price'])}"
            )

            if st.button("Ẩn hóa đơn"):
                del st.session_state.last_order_id
                st.rerun()

    # ==============================
    # GIAO DIỆN ĐẶT NƯỚC
    # ==============================
    st.markdown("## Đặt nước tại Nhóm 27 coffee")
    st.caption("Chọn món, xác nhận thông tin và thanh toán bằng VietQR.")

    # Khởi tạo giỏ hàng
    if "cart" not in st.session_state:
        st.session_state.cart = {}

    # Khởi tạo phần trăm giảm giá
    if "customer_discount_percent" not in st.session_state:
        st.session_state.customer_discount_percent = 0

    # ==============================
    # LỌC DANH MỤC
    # ==============================
    categories = ["Tất cả"] + sorted(
        {item["category"] for item in menu}
    )

    selected_category = st.selectbox(
        "Danh mục",
        categories
    )

    filtered_menu = [
        item
        for item in menu
        if selected_category == "Tất cả"
        or item["category"] == selected_category
    ]

    menu_column, cart_column = st.columns(
        [1.7, 1],
        gap="large"
    )

    # ==============================
    # HIỂN THỊ MENU
    # ==============================
    with menu_column:
        product_columns = st.columns(2)

        for index, item in enumerate(filtered_menu):
            with product_columns[index % 2]:

                image_path = (
                    BASE_DIR / item["image_url"]
                    if item["image_url"]
                    else None
                )

                if image_path and image_path.exists():
                    st.image(
                        str(image_path),
                        use_container_width=True
                    )

                st.markdown(f"### {item['name']}")

                st.caption(
                    item["description"] or item["category"]
                )

                st.markdown(
                    f"**{format_price(item['price'])}**"
                )

                if st.button(
                    "+ Thêm vào giỏ",
                    key=f"add_{item['id']}",
                    use_container_width=True
                ):
                    st.session_state.cart[item["id"]] = (
                        st.session_state.cart.get(item["id"], 0) + 1
                    )

                    st.toast(f"Đã thêm {item['name']}")

    # ==============================
    # GIỎ HÀNG
    # ==============================
    with cart_column:
        st.markdown("### Giỏ hàng")

        selected_items = [
            item
            for item in menu
            if st.session_state.cart.get(item["id"], 0) > 0
        ]

        if not selected_items:
            st.info("Giỏ hàng đang trống.")

        else:
            order_items = []
            subtotal = 0

            # ==============================
            # CHI TIẾT GIỎ HÀNG
            # ==============================
            for item in selected_items:
                quantity = st.number_input(
                    f"{item['name']} ({format_price(item['price'])})",
                    min_value=1,
                    max_value=20,
                    value=st.session_state.cart[item["id"]],
                    key=f"qty_{item['id']}"
                )

                st.session_state.cart[item["id"]] = quantity

                subtotal += item["price"] * quantity

                order_items.append({
                    "name": item["name"],
                    "quantity": quantity,
                    "price": item["price"]
                })

            # ==============================
            # MÃ GIẢM GIÁ
            # ==============================
            voucher = st.text_input(
                "Mã giảm giá (nếu có)"
            ).strip()

            if st.button("Áp dụng mã"):
                if voucher:
                    discount_percent = database.get_discount_percent(
                        voucher
                    )

                    if discount_percent > 0:
                        st.session_state.customer_discount_percent = (
                            discount_percent
                        )

                        st.success(
                            f"Đã áp dụng mã thành công! "
                            f"Giảm {discount_percent}%"
                        )
                    else:
                        st.session_state.customer_discount_percent = 0

                        st.error(
                            "Mã giảm giá không hợp lệ hoặc đã hết hạn."
                        )
                else:
                    st.session_state.customer_discount_percent = 0

                    st.warning(
                        "Vui lòng nhập mã giảm giá."
                    )

            # ==============================
            # TÍNH TIỀN
            # ==============================
            current_discount_percent = st.session_state.get(
                "customer_discount_percent",
                0
            )

            discount_amount = (
                subtotal * current_discount_percent / 100
            )

            total = max(
                0,
                subtotal - discount_amount
            )

            st.markdown(
                f"Tạm tính: **{format_price(subtotal)}**"
            )

            if current_discount_percent > 0:
                st.markdown(
                    f"Giảm giá ({current_discount_percent}%): "
                    f"**-{format_price(discount_amount)}**"
                )

            st.markdown(
                f"Tổng thanh toán: **{format_price(total)}**"
            )

            # ==============================
            # NHẬP THÔNG TIN KHÁCH HÀNG
            # ==============================
            with st.form("customer_order_form"):
                st.markdown("#### Xác nhận đơn hàng")

                customer_name = st.text_input(
                    "Tên khách hàng"
                )

                customer_phone = st.text_input(
                    "Số điện thoại"
                )

                table_num = st.text_input(
                    "Số bàn"
                )

                submitted = st.form_submit_button(
                    "Tiếp tục thanh toán",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                if (
                    not customer_name.strip()
                    or not customer_phone.strip()
                    or not table_num.strip()
                ):
                    st.error(
                        "Vui lòng nhập đủ tên, số điện thoại và số bàn."
                    )
                else:
                    st.session_state.pending_order = {
                        "name": customer_name,
                        "phone": customer_phone,
                        "table_num": table_num,
                        "items": order_items,
                        "total": total
                    }

                    st.rerun()

            # ==============================
            # THANH TOÁN VIETQR
            # ==============================
            pending_order = st.session_state.get(
                "pending_order"
            )

            if pending_order:
                st.divider()

                st.markdown("#### Thanh toán VietQR")

                st.write(
                    f"Đơn của **{pending_order['name']}** - "
                    f"{format_price(pending_order['total'])}"
                )

                bank_code = st.text_input(
                    "Mã ngân hàng nhận tiền",
                    value="VCB",
                    key="bank_code"
                )

                account_number = st.text_input(
                    "Số tài khoản nhận tiền",
                    value="0123456789",
                    key="account_number"
                )

                qr_url = (
                    f"https://img.vietqr.io/image/"
                    f"{quote(bank_code)}-"
                    f"{quote(account_number)}-"
                    f"compact2.png?"
                    f"amount={int(pending_order['total'])}"
                    f"&addInfo={quote('Thanh toan don ' + pending_order['name'])}"
                )

                st.image(
                    qr_url,
                    caption="Quét mã để thanh toán",
                    width=260
                )

                # ==============================
                # XÁC NHẬN ĐÃ THANH TOÁN
                # ==============================
                if st.button("Đã hoàn thành thanh toán"):

                    order_id = database.save_order(
                        pending_order["name"],
                        pending_order["phone"],
                        pending_order["table_num"],
                        pending_order["items"],
                        pending_order["total"]
                    )

                    # Lưu mã đơn hàng để hiển thị hóa đơn
                    st.session_state.last_order_id = order_id

                    # Xóa giỏ hàng
                    st.session_state.cart = {}

                    # Xóa mã giảm giá
                    st.session_state.customer_discount_percent = 0

                    # Xóa đơn hàng đang chờ thanh toán
                    del st.session_state.pending_order

                    st.success(
                        f"Đã nhận đơn hàng #{order_id}"
                    )

                    st.rerun()