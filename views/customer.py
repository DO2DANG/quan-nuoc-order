from pathlib import Path
import base64
from urllib.parse import quote

import streamlit as st

import database


# ============================================================
# CẤU HÌNH
# ============================================================

# customer.py nằm trong:
# views/customer.py
#
# parents[0] = views
# parents[1] = thư mục gốc của project
BASE_DIR = Path(__file__).parents[1]

DEFAULT_IMAGE_PATH = (
    BASE_DIR / "assets" / "images" / "no_image.jpg"
)

# Số lượng món hiển thị trên mỗi trang
MENU_PAGE_SIZE = 6


# ============================================================
# LẤY MENU
# ============================================================

@st.cache_data(ttl=60, show_spinner=False)
def get_cached_menu():
    """
    Lấy danh sách món từ database.

    database.py sử dụng:
        database.list_menu()
    """
    return database.list_menu()


# ============================================================
# XỬ LÝ HÌNH ẢNH
# ============================================================

@st.cache_data(
    max_entries=200,
    show_spinner=False
)
def get_image_data_uri(
    image_path_str,
    modified_time
):
    """
    Đọc file ảnh và chuyển thành Data URI
    để hiển thị trực tiếp bằng HTML.
    """

    path = Path(image_path_str)

    # Nếu ảnh không tồn tại thì dùng ảnh mặc định
    if not path.exists():
        path = DEFAULT_IMAGE_PATH

    # Nếu cả ảnh chính và ảnh mặc định đều không tồn tại
    if not path.exists():
        return None

    try:
        encoded = base64.b64encode(
            path.read_bytes()
        ).decode("utf-8")

        suffix = path.suffix.lower()

        mime_type = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }.get(
            suffix,
            "image/jpeg"
        )

        return (
            f"data:{mime_type};base64,{encoded}"
        )

    except Exception:
        return None


# ============================================================
# FORMAT GIÁ
# ============================================================

def format_price(price):
    """
    Ví dụ:
        25000 -> 25.000đ
        35000 -> 35.000đ
    """

    try:
        return (
            f"{float(price):,.0f}đ"
            .replace(",", ".")
        )
    except (
        TypeError,
        ValueError
    ):
        return "0đ"


# ============================================================
# HÓA ĐƠN
# ============================================================

def show_invoice(order):
    """
    Hiển thị hóa đơn trong hộp thoại ở giữa màn hình,
    kèm mã VietQR.
    """

    @st.dialog("🧾 HÓA ĐƠN THANH TOÁN")
    def invoice_dialog():

        # ====================================================
        # THÔNG BÁO
        # ====================================================

        st.success(
            "✅ Đặt hàng thành công!"
        )

        st.markdown(
            dedent("""
            <div style="text-align: center;">
                <h3>☕ NHÓM 27 COFFEE</h3>
                <p>Cảm ơn quý khách đã sử dụng dịch vụ!</p>
            </div>
            """),
            unsafe_allow_html=True,
        )

        # ====================================================
        # THÔNG TIN ĐƠN HÀNG
        # ====================================================

        st.write(
            f"**Mã hóa đơn:** "
            f"#{order.get('id', '')}"
        )

        st.write(
            f"**Tên khách hàng:** "
            f"{order.get('name', '')}"
        )

        st.write(
            f"**Số điện thoại:** "
            f"{order.get('phone', '')}"
        )

        st.write(
            f"**Số bàn:** "
            f"{order.get('table_num', '')}"
        )

        st.write(
            f"**Thời gian:** "
            f"{order.get('created_at', '')}"
        )

        st.write(
            f"**Trạng thái:** "
            f"{order.get('status', '')}"
        )

        st.divider()

        # ====================================================
        # CHI TIẾT MÓN HÀNG
        # ====================================================

        st.markdown(
            "### Chi tiết món hàng"
        )

        order_items = order.get(
            "items",
            []
        )

        if order_items:

            for item in order_items:

                item_name = item.get(
                    "name",
                    "Món không tên"
                )

                quantity = int(
                    item.get(
                        "quantity",
                        0
                    )
                )

                price = item.get(
                    "price",
                    0
                )

                amount = (
                    quantity * price
                )

                st.write(
                    f"**{item_name}** × "
                    f"{quantity} — "
                    f"{format_price(amount)}"
                )

        else:

            st.info(
                "Không có chi tiết món hàng."
            )

        st.divider()

        # ====================================================
        # TỔNG TIỀN
        # ====================================================

        total_price = order.get(
            "total_price",
            0
        )

        st.markdown(
            "## Tổng tiền: "
            f"{format_price(total_price)}"
        )

        # ====================================================
        # VIETQR
        # ====================================================

        # ----------------------------------------------------
        # TODO:
        # Thay thông tin bên dưới bằng tài khoản ngân hàng
        # thật của quán.
        # ----------------------------------------------------

        bank_code = "VCB"

        account_number = (
            "0123456789"
        )

        order_id = order.get(
            "id",
            ""
        )

        payment_content = (
            f"Thanh toan don {order_id}"
        )

        qr_url = (
            "https://img.vietqr.io/image/"
            f"{quote(bank_code)}-"
            f"{quote(account_number)}-"
            "compact2.png?"
            f"amount={int(total_price)}"
            f"&addInfo="
            f"{quote(payment_content)}"
        )

        st.markdown(
            "### 📱 Quét mã VietQR để thanh toán"
        )

        st.image(
            qr_url,
            caption="Quét mã để thanh toán",
            width=260
        )

        st.caption(
            "Vui lòng kiểm tra đúng số tiền "
            "trước khi chuyển khoản."
        )

        # ====================================================
        # ĐÓNG HÓA ĐƠN
        # ====================================================

        if st.button(
            "Đóng hóa đơn",
            use_container_width=True
        ):

            st.session_state.show_invoice = (
                False
            )

            st.session_state.pop(
                "last_order_id",
                None
            )

            st.rerun()

    invoice_dialog()


# ============================================================
# MÀN HÌNH CHÀO MỪNG
# ============================================================

def show_welcome_screen():
    st.markdown(
        dedent("""
        <style>
        .welcome-box {
            text-align: center;
            padding: 60px 25px;
            border-radius: 22px;
            background: linear-gradient(135deg, #fff8ed, #f7e3c5);
            margin: 35px auto;
            max-width: 850px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        }

        .welcome-title {
            font-size: 38px;
            font-weight: 700;
            margin-bottom: 18px;
            color: #4b2e1f;
        }

        .welcome-subtitle {
            font-size: 20px;
            line-height: 1.7;
            color: #5f4638;
        }
        </style>

        <div class="welcome-box">
            <div class="welcome-title">
                ☕ KÍNH CHÀO QUÝ KHÁCH
            </div>

            <div class="welcome-subtitle">
                Chào mừng bạn đến với <b>Nhóm 27 Coffee</b><br>
                Hãy chọn món yêu thích và tận hưởng<br>
                thức uống của bạn!
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 2, 1])

    with center:
        if st.button(
            "🛒 ĐẶT MÓN NGAY",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.started_ordering = True
            st.rerun()
# ============================================================
# RENDER CHÍNH
# ============================================================

def render():

    # ========================================================
    # KHỞI TẠO SESSION STATE
    # ========================================================

    if "started_ordering" not in st.session_state:
        st.session_state.started_ordering = False

    if "cart" not in st.session_state:
        st.session_state.cart = {}

    if "customer_discount_percent" not in st.session_state:
        st.session_state.customer_discount_percent = 0

    if "menu_page" not in st.session_state:
        st.session_state.menu_page = 1

    if "last_menu_category" not in st.session_state:
        st.session_state.last_menu_category = None

    if "show_invoice" not in st.session_state:
        st.session_state.show_invoice = False

    # ========================================================
    # MÀN HÌNH CHÀO MỪNG
    # ========================================================

    if not st.session_state.started_ordering:

        show_welcome_screen()

        return

    # ========================================================
    # LẤY MENU
    # ========================================================

    menu = get_cached_menu()

    if menu is None:
        menu = []

    if not menu:

        st.error(
            "Không có dữ liệu menu. "
            "Vui lòng kiểm tra dữ liệu món ăn "
            "trong database."
        )

        return

    # ========================================================
    # HIỂN THỊ HÓA ĐƠN
    # ========================================================

    if st.session_state.get(
        "show_invoice",
        False
    ):

        order_id = st.session_state.get(
            "last_order_id"
        )

        if order_id is not None:

            try:

                order = (
                    database.get_order_by_id(
                        order_id
                    )
                )

                if order:

                    show_invoice(order)

            except Exception as exc:

                st.error(
                    "Không thể lấy thông tin "
                    f"hóa đơn: {exc}"
                )

    # ========================================================
    # TIÊU ĐỀ
    # ========================================================

    st.markdown(
        "## Đặt nước tại Nhóm 27 Coffee"
    )

    st.caption(
        "Chọn món, xác nhận thông tin "
        "và thanh toán bằng VietQR."
    )

    # ========================================================
    # DANH MỤC
    # ========================================================

    categories = sorted(
        {
            item.get(
                "category",
                "Khác"
            )
            for item in menu
        }
    )

    categories = [
        "Tất cả",
        *categories
    ]

    selected_category = st.selectbox(
        "Danh mục",
        categories
    )

    # ========================================================
    # LỌC MENU
    # ========================================================

    filtered_menu = [
        item
        for item in menu
        if (
            selected_category == "Tất cả"
            or item.get("category")
            == selected_category
        )
    ]

    # ========================================================
    # RESET TRANG KHI ĐỔI DANH MỤC
    # ========================================================

    if (
        st.session_state.get(
            "last_menu_category"
        )
        != selected_category
    ):

        st.session_state.last_menu_category = (
            selected_category
        )

        st.session_state.menu_page = 1

    # ========================================================
    # PHÂN TRANG
    # ========================================================

    total_pages = max(
        1,
        (
            len(filtered_menu)
            + MENU_PAGE_SIZE
            - 1
        )
        // MENU_PAGE_SIZE
    )

    current_page = min(
        st.session_state.get(
            "menu_page",
            1
        ),
        total_pages
    )

    start_index = (
        current_page - 1
    ) * MENU_PAGE_SIZE

    end_index = (
        start_index
        + MENU_PAGE_SIZE
    )

    visible_menu = filtered_menu[
        start_index:end_index
    ]

    # ========================================================
    # MENU + GIỎ HÀNG
    # ========================================================

    menu_column, cart_column = st.columns(
        [1.7, 1],
        gap="large"
    )

    # ========================================================
    # HIỂN THỊ MENU
    # ========================================================

    with menu_column:

        product_columns = st.columns(2)

        for index, item in enumerate(
            visible_menu
        ):

            with product_columns[
                index % 2
            ]:

                # ============================================
                # ID MÓN
                # ============================================

                item_id = item.get("id")

                if item_id is None:
                    continue

                # ============================================
                # ẢNH MÓN
                # ============================================

                image_url = item.get(
                    "image_url",
                    ""
                )

                if image_url:

                    image_path = (
                        BASE_DIR
                        / image_url
                    )

                else:

                    image_path = (
                        DEFAULT_IMAGE_PATH
                    )

                if not image_path.exists():

                    image_path = (
                        DEFAULT_IMAGE_PATH
                    )

                image_uri = None

                if image_path.exists():

                    image_uri = (
                        get_image_data_uri(
                            str(image_path),
                            image_path.stat().st_mtime_ns
                        )
                    )

                if image_uri:

                    st.markdown(
                        f"""
                        <div
                            style="
                                width:100%;
                                aspect-ratio:4/3;
                                overflow:hidden;
                                border-radius:12px;
                                margin-bottom:10px;
                                background:#f5f5f5;
                            "
                        >
                            <img
                                src="{image_uri}"
                                loading="lazy"
                                decoding="async"
                                style="
                                    width:100%;
                                    height:100%;
                                    object-fit:cover;
                                    display:block;
                                "
                            >
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # ============================================
                # TÊN MÓN
                # ============================================

                item_name = item.get(
                    "name",
                    "Món không tên"
                )

                st.markdown(
                    f"### {item_name}"
                )

                # ============================================
                # MÔ TẢ
                # ============================================

                description = (
                    item.get(
                        "description"
                    )
                    or item.get(
                        "category"
                    )
                    or ""
                )

                st.caption(
                    description
                )

                # ============================================
                # GIÁ
                # ============================================

                item_price = item.get(
                    "price",
                    0
                )

                st.markdown(
                    f"**{format_price(item_price)}**"
                )

                # ============================================
                # THÊM VÀO GIỎ
                # ============================================

                if st.button(
                    "+ Thêm vào giỏ",
                    key=f"add_{item_id}",
                    use_container_width=True
                ):

                    current_quantity = (
                        st.session_state.cart.get(
                            item_id,
                            0
                        )
                    )

                    st.session_state.cart[
                        item_id
                    ] = (
                        current_quantity + 1
                    )

                    st.toast(
                        f"Đã thêm {item_name}"
                    )

        # ====================================================
        # NÚT CHUYỂN TRANG
        # ====================================================

        if total_pages > 1:

            prev_col, page_col, next_col = (
                st.columns([1, 2, 1])
            )

            with prev_col:

                if st.button(
                    "← Trước",
                    disabled=(
                        current_page <= 1
                    ),
                    use_container_width=True
                ):

                    st.session_state.menu_page = (
                        current_page - 1
                    )

                    st.rerun()

            with page_col:

                st.markdown(
                    f"""
                    <div
                        style="
                            text-align:center;
                            padding-top:7px;
                        "
                    >
                        Trang
                        <b>{current_page}</b>
                        /
                        {total_pages}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with next_col:

                if st.button(
                    "Sau →",
                    disabled=(
                        current_page
                        >= total_pages
                    ),
                    use_container_width=True
                ):

                    st.session_state.menu_page = (
                        current_page + 1
                    )

                    st.rerun()

    # ========================================================
    # GIỎ HÀNG
    # ========================================================

    with cart_column:

        st.markdown(
            "### 🛒 Giỏ hàng"
        )

        selected_items = [
            item
            for item in menu
            if (
                st.session_state.cart.get(
                    item.get("id"),
                    0
                ) > 0
            )
        ]

        # ====================================================
        # GIỎ TRỐNG
        # ====================================================

        if not selected_items:

            st.info(
                "Giỏ hàng đang trống."
            )

            return

        # ====================================================
        # DANH SÁCH MÓN TRONG GIỎ
        # ====================================================

        order_items = []

        subtotal = 0

        for item in selected_items:

            item_id = item.get("id")

            item_name = item.get(
                "name",
                "Món không tên"
            )

            item_price = item.get(
                "price",
                0
            )

            current_quantity = (
                st.session_state.cart.get(
                    item_id,
                    1
                )
            )

            # Đảm bảo quantity nằm trong 1-20
            current_quantity = max(
                1,
                min(
                    int(current_quantity),
                    20
                )
            )

            quantity = st.number_input(
                (
                    f"{item_name} "
                    f"({format_price(item_price)})"
                ),
                min_value=1,
                max_value=20,
                value=current_quantity,
                key=f"qty_{item_id}"
            )

            st.session_state.cart[
                item_id
            ] = quantity

            subtotal += (
                item_price * quantity
            )

            order_items.append(
                {
                    "name": item_name,
                    "quantity": quantity,
                    "price": item_price,
                }
            )

        # ====================================================
        # MÃ GIẢM GIÁ
        # ====================================================

        st.markdown(
            "#### 🎟️ Mã giảm giá"
        )

        voucher = st.text_input(
            "Mã giảm giá (nếu có)",
            key="voucher_input"
        ).strip()

        if st.button(
            "Áp dụng mã",
            use_container_width=True
        ):

            if voucher:

                try:

                    discount_percent = (
                        database.get_discount_percent(
                            voucher
                        )
                    )

                    if discount_percent > 0:

                        st.session_state.customer_discount_percent = (
                            discount_percent
                        )

                        st.success(
                            "Đã áp dụng mã thành công! "
                            f"Giảm {discount_percent}%"
                        )

                    else:

                        st.session_state.customer_discount_percent = (
                            0
                        )

                        st.error(
                            "Mã giảm giá không hợp lệ "
                            "hoặc đã hết hạn."
                        )

                except Exception as exc:

                    st.session_state.customer_discount_percent = (
                        0
                    )

                    st.error(
                        "Không thể kiểm tra "
                        f"mã giảm giá: {exc}"
                    )

            else:

                st.session_state.customer_discount_percent = (
                    0
                )

                st.warning(
                    "Vui lòng nhập mã giảm giá."
                )

        # ====================================================
        # TÍNH GIẢM GIÁ
        # ====================================================

        current_discount_percent = (
            st.session_state.get(
                "customer_discount_percent",
                0
            )
        )

        discount_amount = (
            subtotal
            * current_discount_percent
            / 100
        )

        total = max(
            0,
            subtotal - discount_amount
        )

        # ====================================================
        # HIỂN THỊ TỔNG TIỀN
        # ====================================================

        st.markdown(
            "Tạm tính: "
            f"**{format_price(subtotal)}**"
        )

        if current_discount_percent > 0:

            st.markdown(
                f"Giảm giá "
                f"({current_discount_percent}%): "
                f"**-{format_price(discount_amount)}**"
            )

        st.markdown(
            "### Tổng thanh toán: "
            f"**{format_price(total)}**"
        )

        # ====================================================
        # THÔNG TIN KHÁCH HÀNG
        # ====================================================

        with st.form(
            "customer_order_form"
        ):

            st.markdown(
                "#### Xác nhận đơn hàng"
            )

            customer_name = st.text_input(
                "Tên khách hàng"
            )

            customer_phone = st.text_input(
                "Số điện thoại"
            )

            table_num = st.text_input(
                "Số bàn"
            )

            submitted = (
                st.form_submit_button(
                    "Tiếp tục thanh toán",
                    type="primary",
                    use_container_width=True
                )
            )

        # ====================================================
        # XỬ LÝ ĐẶT HÀNG
        # ====================================================

        if submitted:

            customer_name = (
                customer_name.strip()
            )

            customer_phone = (
                customer_phone.strip()
            )

            table_num = (
                table_num.strip()
            )

            # ================================================
            # KIỂM TRA THÔNG TIN
            # ================================================

            if not customer_name:

                st.error(
                    "Vui lòng nhập tên khách hàng."
                )

                return

            if not customer_phone:

                st.error(
                    "Vui lòng nhập số điện thoại."
                )

                return

            if not table_num:

                st.error(
                    "Vui lòng nhập số bàn."
                )

                return

            if not order_items:

                st.error(
                    "Giỏ hàng đang trống."
                )

                return

            # ================================================
            # LƯU ĐƠN HÀNG
            # ================================================

            try:

                order_id = database.save_order(
                    customer_name,
                    customer_phone,
                    table_num,
                    order_items,
                    total
                )

            except Exception as exc:

                st.error(
                    "Không thể tạo đơn hàng: "
                    f"{exc}"
                )

                return

            # ================================================
            # LƯU ID ĐƠN HÀNG
            # ================================================

            st.session_state.last_order_id = (
                order_id
            )

            st.session_state.show_invoice = (
                True
            )

            # ================================================
            # XÓA GIỎ HÀNG
            # ================================================

            st.session_state.cart = {}

            # ================================================
            # RESET GIẢM GIÁ
            # ================================================

            st.session_state.customer_discount_percent = (
                0
            )

            # ================================================
            # RESET MÃ VOUCHER
            # ================================================

            if "voucher_input" in st.session_state:

                st.session_state.voucher_input = ""

            # ================================================
            # HIỂN THỊ HÓA ĐƠN
            # ================================================

            st.rerun()