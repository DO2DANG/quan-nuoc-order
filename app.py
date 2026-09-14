import streamlit as st

import database
from views import admin, customer

database.init_db()

st.set_page_config(
    page_title="Nhóm 27 coffee",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; }
    .stApp { background: #fffaf5; }
    div[data-testid="stSidebar"], div[data-testid="stSidebarCollapsedControl"] { display: none; }
    div[data-testid="stButton"] > button { border-radius: 8px; }
    .cafe-banner {
        background: linear-gradient(110deg, #30231e, #a75d3b);
        border-radius: 20px;
        color: #fffaf5;
        margin: 0 0 28px;
        padding: 42px 48px 40px;
    }
    .cafe-banner__eyebrow {
        color: #f6b184;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }
    .cafe-banner h1 {
        color: #fffaf5;
        font-family: 'DM Sans', sans-serif;
        font-size: clamp(2.2rem, 5vw, 3.6rem);
        margin: 24px 0 14px;
    }
    .cafe-banner p {
        color: #fceee5;
        font-size: 1.05rem;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="cafe-banner">
        <div class="cafe-banner__eyebrow">Freshly brewed · Since 2024</div>
        <h1>Nhóm 27 coffee</h1>
        <p>Một khoảng nghỉ nhỏ, một ly nước vừa vặn với ngày hôm nay.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

role = st.session_state.get("role", "Khách hàng")

header_spacer, manager_column = st.columns([8, 1])
with manager_column:
    if role == "Chủ quán":
        if st.button("khách hàng", use_container_width=True):
            st.session_state.role = "Khách hàng"
            st.rerun()
    else:
        with st.popover("Quản lý", use_container_width=True):
            st.markdown("#### Đăng nhập chủ quán")
            manager_password = st.text_input("Mật khẩu", type="password", key="manager_password")
            if st.button("Vào giao diện chủ quán", type="primary", use_container_width=True):
                if manager_password == admin.ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.session_state.role = "Chủ quán"
                    st.rerun()
                else:
                    st.error("Mật khẩu không đúng.")

if role == "Khách hàng":
    customer.render()
else:
    if admin.is_authenticated():
        admin.render()
    else:
        st.title("Đăng nhập quản lý")
        st.info("Nhập mật khẩu ở thanh bên để mở giao diện chủ quán.")