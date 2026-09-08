import json
from pathlib import Path
import streamlit as st

VALID_VOUCHERS = {
    "GIAM10K": 10000,
    "GIAM20K": 20000,
    "FREESHIP": 12000
} 

BASE_DIR = Path(__file__).parent
if "discount" not in st.session_state:
    st.session_state.discount = 0
if "applied_voucher" not in st.session_state:
    st.session_state.applied_voucher = ""
MENU_FILE = BASE_DIR / "data" / "menu.json"

st.set_page_config(
    page_title="Nhóm 27 coffee",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
)
dark_mode = st.toggle("🌙 Chế độ tối (Dark Mode)")

if dark_mode:
    bg_color = "#121212"
    card_bg = "#1e1e1e"
    text_color = "#f5f5f5"
    desc_color = "#b0b0b0"
    border_color = "#333333"
else:
    bg_color = "#fffaf5"
    card_bg = "#ffffff"
    text_color = "#2f241f"
    desc_color = "#806e63"
    border_color = "#eee1d7"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
    h1, h2, h3 {{ font-family: 'Playfair Display', serif; }}
    .stApp {{ background: {bg_color}; color: {text_color}; }}
    .hero {{
        padding: 2.4rem 2.6rem 2.2rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #2f241f 0%, #563d31 62%, #a95f3d 100%);
        color: #fffaf5;
        margin-bottom: 2rem;
    }}
    .hero h1 {{ color: #fffaf5; font-size: 3.1rem; margin: 0 0 .4rem; }}
    .hero p {{ color: #f5dfd0; margin: 0; font-size: 1.05rem; }}
    .eyebrow {{ color: #eab38f; letter-spacing: .14em; text-transform: uppercase; font-size: .75rem; font-weight: 700; }}
    .menu-card {{
        background: {card_bg}; border: 1px solid {border_color}; border-radius: 14px;
        padding: 1.1rem; min-height: 205px; box-shadow: 0 5px 18px rgba(0, 0, 0, .1);
    }}
    .drink-visual {{ background: #f4e8dc; border-radius: 10px; height: 92px; display: grid; place-items: center; font-size: 3.1rem; margin-bottom: .8rem; }}
    .drink-name {{ font-family: 'Playfair Display', serif; font-size: 1.22rem; color: {text_color}; font-weight: 700; }}
    .drink-desc {{ color: {desc_color}; font-size: .86rem; min-height: 42px; margin: .3rem 0 .55rem; }}
    .price {{ color: #b85f3a; font-weight: 700; }}
    div[data-testid="stButton"] > button {{ border-radius: 8px; border-color: #d97745; color: #a65332; }}
    div[data-testid="stButton"] > button[kind="primary"] {{ background: #d97745; color: white; }}
    .cart-title {{ font-family: 'Playfair Display', serif; font-size: 1.65rem; color: {text_color}; }}
    .total {{ border-top: 1px solid {border_color}; padding-top: .8rem; font-weight: 700; font-size: 1.1rem; color: {text_color}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

def load_menu():
    with MENU_FILE.open(encoding="utf-8") as menu_file:
        return json.load(menu_file)

def format_price(price):
    return f"{price:,.0f}đ".replace(",", ".")

def add_to_cart(item):
    cart = st.session_state.cart
    cart[item["id"]] = cart.get(item["id"], 0) + 1

def cart_total(menu):
    return sum(item["price"] * st.session_state.cart.get(item["id"], 0) for item in menu)

if "cart" not in st.session_state:
    st.session_state.cart = {}

menu = load_menu()
categories = ["Tất cả"] + sorted({item["category"] for item in menu})

st.markdown(
    '<section class="hero"><div class="eyebrow">Freshly brewed · Since 2024</div>'
    '<h1>Nhóm 27 coffee</h1><p>Một khoảng nghỉ nhỏ, một ly nước vừa vặn với ngày hôm nay.</p></section>',
    unsafe_allow_html=True,
)

menu_column, cart_column = st.columns([1.75, 1], gap="large")

with menu_column:
    heading_col, filter_col = st.columns([1.5, 1])
    with heading_col:
        st.markdown("## Menu hôm nay")
    with filter_col:
        selected_category = st.selectbox("Danh mục", categories, label_visibility="collapsed")

    filtered_menu = [
        item for item in menu
        if selected_category == "Tất cả" or item["category"] == selected_category
    ]
    product_columns = st.columns(2, gap="medium")
    for index, item in enumerate(filtered_menu):
        with product_columns[index % 2]:
            image_path = BASE_DIR / item["image"]
            visual = f'<img src="{image_path.as_uri()}" style="width:100%;height:92px;object-fit:cover;border-radius:10px;">' if image_path.exists() else ""
            st.markdown(
                f'<div class="menu-card"><div class="drink-visual">{visual}</div>'
                f'<div class="drink-name">{item["name"]}</div>'
                f'<div class="drink-desc">{item["description"]}</div>'
                f'<span class="price">{format_price(item["price"])}</span></div>',
                unsafe_allow_html=True,
            )
            if st.button("+ Thêm vào giỏ", key=f"add_{item['id']}", use_container_width=True):
                add_to_cart(item)
                st.toast(f"Đã thêm {item['name']}")

with cart_column:
    st.markdown('<div class="cart-title">Giỏ hàng</div>', unsafe_allow_html=True)
    selected_items = [item for item in menu if st.session_state.cart.get(item["id"], 0)]

    if not selected_items:
        st.info("Giỏ hàng đang trống. Chọn một món để bắt đầu nhé.")
    else:
        for item in selected_items:
            quantity = st.session_state.cart[item["id"]]
            item_col, quantity_col = st.columns([1.8, 1])
            with item_col:
                st.markdown(f"**{item['name']}**  \n{format_price(item['price'])}")
            with quantity_col:
                new_quantity = st.number_input("SL", 1, 20, quantity, key=f"qty_{item['id']}", label_visibility="collapsed")
                st.session_state.cart[item["id"]] = new_quantity

        st.markdown("---")
        voucher_input = st.text_input("Nhập mã giảm giá:", value=st.session_state.applied_voucher)

        if st.button("Áp dụng mã"):
            code = voucher_input.strip().upper()
            if code in VALID_VOUCHERS:
                st.session_state.discount = VALID_VOUCHERS[code]
                st.session_state.applied_voucher = code
                st.success(f"Đã áp dụng mã {code}!")
                st.rerun()
            else:
                st.error("Mã giảm giá không hợp lệ!")
                st.session_state.discount = 0
                st.session_state.applied_voucher = ""
                st.rerun()

        subtotal = cart_total(menu)
        final_total = max(0, subtotal - st.session_state.discount)

        if st.session_state.discount > 0:
            st.markdown(f"Giảm giá: **-{format_price(st.session_state.discount)}**")
            
        st.markdown(f'<div class="total">Tổng cộng: {format_price(final_total)}</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("### Thông tin nhận đồ")
        with st.form("order_form"):
            customer_name = st.text_input("Tên của bạn")
            customer_phone = st.text_input("Số điện thoại")
            customer_address = st.text_input("Địa chỉ nhận hàng")
            pickup_note = st.text_area("Ghi chú", placeholder="Ít đá, không đường...")
            submitted = st.form_submit_button("Xác nhận đặt hàng", type="primary", use_container_width=True)

        if submitted:
            if not customer_name.strip() or not customer_phone.strip() or not customer_address.strip():
                st.error("Vui lòng nhập tên, số điện thoại và địa chỉ đầy đủ.")
            else:
                st.success(f"Đã nhận đơn của {customer_name}! Quán sẽ gọi {customer_phone} để xác nhận.")
                st.session_state.cart = {}
                st.session_state.discount = 0
                st.session_state.applied_voucher = ""
                st.balloons()