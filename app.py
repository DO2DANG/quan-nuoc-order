import base64
import io
import streamlit as st
import textwrap
import qrcode
import database
from views import admin, customer


database.init_db()

st.set_page_config(
    page_title="Nhóm 27 coffee",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown(
    textwrap.dedent(
        """
        <style>

        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        h1, h2, h3 {
            font-family: 'Playfair Display', serif;
        }

        .stApp {
            background: #fffaf5;
        }

        div[data-testid="stSidebar"] {
            display: none;
        }

        div[data-testid="stButton"] > button {
            border-radius: 10px;
        }

        div[data-testid="stPopover"] {
            width: 100%;
            margin-bottom: 25px;
        }

        button[data-testid="stPopoverButton"],
        div.st-key-customer-nav button {
            width: 100%;
            height: 40px;
            min-height: 40px;
            padding: 0.5rem 1rem;
            border: 1px solid #6f4030 !important;
            border-radius: 10px;
            background: linear-gradient(110deg, #30231e, #a75d3b) !important;
            color: #fffaf5 !important;
        }

        button[data-testid="stPopoverButton"]:hover,
        div.st-key-customer-nav button:hover {
            border-color: #30231e !important;
            color: #fffaf5 !important;
            background: linear-gradient(110deg, #3b2922, #b56a46) !important;
        }

        .cafe-banner {
            background: linear-gradient(110deg, #30231e, #a75d3b);
            border-radius: 20px;
            padding: 32px 40px;
            margin-top: 55px;
            margin-bottom: 50px;
        }

        .banner-layout {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1.5rem;
            min-height: 260px;
        }

        .banner-left {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-width: 0;
        }

        .banner-qr {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 190px;
            min-width: 190px;
            padding: 8px 12px;
        }

        .banner-qr img {
            width: 150px;
            height: 150px;
            object-fit: contain;
            border-radius: 18px;
            background: #fffaf5;
            padding: 10px;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);
        }

        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 2rem !important;
        }

        .banner-small {
            color: #f6b184;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 3px;
            margin-bottom: 18px;
        }

        .banner-title {
            color: #fffaf5;
            font-family: 'DM Sans', sans-serif;
            font-size: 52px;
            font-weight: 700;
            margin-bottom: 12px;
            line-height: 0.95;
            letter-spacing: -1px;
        }

        .banner-text {
            color: #fceee5;
            font-size: 17px;
            line-height: 1.5;
            max-width: 620px;
        }

        @media (max-width: 768px) {
            .cafe-banner {
                padding: 22px 20px;
            }

            .banner-layout {
                display: block;
                min-height: auto;
            }

            .banner-left {
                width: 100%;
                margin-bottom: 18px;
            }

            .banner-title {
                font-size: 42px;
                line-height: 0.95;
            }

            .banner-small {
                font-size: 11px;
                letter-spacing: 2px;
                margin-bottom: 12px;
            }

            .banner-text {
                font-size: 15px;
            }

            .banner-qr {
                width: 100%;
                min-width: 100%;
                padding: 0;
                margin-top: 10px;
            }

            .banner-qr img {
                width: 110px;
                height: 110px;
            }
        }

        .info-box {
            background: #f6eadf;
            border: 1px solid #ead8ca;
            border-radius: 10px;
            padding: 13px 10px;
            text-align: center;
            color: #5a4034;
            font-size: 15px;
            margin-bottom: 25px;
        }

        </style>
        """
    ),
    unsafe_allow_html=True
)


def generate_qr_code(url: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#30231e", back_color="#fffaf5")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


role = st.session_state.get("role", "Khách hàng")


if role == "Khách hàng":

    fixed_url = "https://quan-nuoc-order-rsckzv8cw4dnd4s6offztv.streamlit.app/"
    qr_image = generate_qr_code(fixed_url)
    qr_base64 = base64.b64encode(qr_image).decode("utf-8")
    qr_html = f'<img src="data:image/png;base64,{qr_base64}" alt="QR Code" />'

    st.markdown(
        f"""
        <div class="cafe-banner">
            <div class="banner-layout">
                <div class="banner-left">
                    <div class="banner-small">FRESHLY BREWED · SINCE 2024</div>
                    <div class="banner-title">Nhóm 27 coffee</div>
                    <div class="banner-text">Một khoảng nghỉ nhỏ, một ly nước vừa vặn với ngày hôm nay.</div>
                </div>
                <div class="banner-qr">
                    {qr_html}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    info1, info2, info3, info4, management = st.columns(5)


    with info1:

        st.markdown(
            textwrap.dedent(
                """
                <div class="info-box">
                    ☕ Cà phê pha mới
                </div>
                """
            ),
            unsafe_allow_html=True
        )


    with info2:

        st.markdown(
            textwrap.dedent(
                """
                <div class="info-box">
                    🧋 Đồ uống đa dạng
                </div>
                """
            ),
            unsafe_allow_html=True
        )


    with info3:

        st.markdown(
            textwrap.dedent(
                """
                <div class="info-box">
                    🍰 Đồ ăn nhẹ
                </div>
                """
            ),
            unsafe_allow_html=True
        )


    with info4:

        st.markdown(
            textwrap.dedent(
                """
                <div class="info-box">
                    💳 Thanh toán VietQR
                </div>
                """
            ),
            unsafe_allow_html=True
        )


    with management:

        with st.container(key="management-nav"):
            with st.popover(
                "Quản lý",
                type="primary",
                use_container_width=True
            ):

                st.markdown("### Đăng nhập chủ quán")

                manager_password = st.text_input(
                    "Mật khẩu",
                    type="password",
                    key="manager_password"
                )

                if st.button(
                    "Vào giao diện chủ quán",
                    type="primary",
                    use_container_width=True
                ):

                    if manager_password == admin.ADMIN_PASSWORD:

                        st.session_state.admin_authenticated = True
                        st.session_state.role = "Chủ quán"
                        st.rerun()

                    else:

                        st.error("Mật khẩu không đúng.")

    customer.render()


else:

    if admin.is_authenticated():

        st.markdown(
            """
            <div class="cafe-banner">
                <div class="banner-small">MANAGEMENT · NHÓM 27 COFFEE</div>
                <div class="banner-title">Trang quản lý</div>
                <div class="banner-text">Quản lý đơn hàng, món uống và hoạt động của quán.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        _, _, _, _, customer_nav = st.columns(5)
        with customer_nav:
            with st.container(key="customer-nav"):
                if st.button(
                    "Khách hàng",
                    type="primary",
                    use_container_width=True
                ):
                    st.session_state.role = "Khách hàng"
                    st.session_state.admin_authenticated = False
                    st.rerun()

        admin.render()

    else:

        st.title("Đăng nhập quản lý")

        st.info(
            "Vui lòng sử dụng nút Quản lý ở phía trên "
            "để đăng nhập vào giao diện chủ quán."
        )

