from datetime import date
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4
from collections import Counter
import streamlit as st
import database


ADMIN_PASSWORD = "1"
BASE_DIR = Path(__file__).parents[1]
IMAGE_DIR = BASE_DIR / "assets" / "images"
ALLOWED_IMAGE_TYPES = {"jpg", "jpeg", "png", "webp"}

from datetime import datetime

from datetime import datetime, timedelta

def render_revenue_analytics():
    st.subheader("📊 Thống kê và Xu hướng Kinh doanh")
    
    orders = database.list_orders()
    
    if not orders:
        st.info("Chưa có dữ liệu đơn hàng để thống kê.")
        return

    view_mode = st.radio(
        "Xem thống kê theo:", 
        ["Khung giờ trong ngày", "Ngày trong tuần", "Theo tháng"], 
        horizontal=True
    )
    
    if view_mode == "Khung giờ trong ngày":
        hours_count = {f"{h:02d}:00": 0 for h in range(8, 23)}
        for order in orders:
            created_at = order.get("created_at")
            if created_at and isinstance(created_at, str):
                try:
                    dt_str = created_at.strip()
                    if len(dt_str) >= 19:
                        # Đọc thời gian gốc từ database và quy đổi sang giờ VN (+7 tiếng)
                        dt_utc = datetime.strptime(dt_str[:19], "%Y-%m-%d %H:%M:%S")
                        dt_vn = dt_utc + timedelta(hours=7)
                        
                        hour_str = f"{dt_vn.hour:02d}:00"
                        if hour_str in hours_count:
                            hours_count[hour_str] += 1
                except Exception:
                    pass
        st.markdown("### Lượng đơn hàng theo khung giờ")
        st.bar_chart(hours_count)
        
    elif view_mode == "Ngày trong tuần":
        weekday_map = {
            "Monday": "Thứ Hai", "Tuesday": "Thứ Ba", "Wednesday": "Thứ Tư", 
            "Thursday": "Thứ Năm", "Friday": "Thứ Sáu", "Saturday": "Thứ Bảy", "Sunday": "Chủ Nhật"
        }
        weekday_order = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        revenue_by_day = {day: 0.0 for day in weekday_order}
        
        for order in orders:
            created_at = order.get("created_at")
            raw_price = order.get("total_price", 0)
            
            try:
                total_price = float(raw_price) if raw_price is not None else 0.0
            except (ValueError, TypeError):
                total_price = 0.0
                
            if created_at and isinstance(created_at, str):
                try:
                    dt_str = created_at.strip()
                    if len(dt_str) >= 19:
                        dt_utc = datetime.strptime(dt_str[:19], "%Y-%m-%d %H:%M:%S")
                        dt_vn = dt_utc + timedelta(hours=7)
                        
                        en_day = dt_vn.strftime("%A")
                        vn_day = weekday_map.get(en_day, en_day)
                        if vn_day in revenue_by_day:
                            revenue_by_day[vn_day] += total_price
                except Exception:
                    pass
        st.markdown("### Doanh thu theo các ngày trong tuần (VNĐ)")
        st.bar_chart(revenue_by_day)
        
    elif view_mode == "Theo tháng":
        revenue_by_month = {}
        for order in orders:
            created_at = order.get("created_at")
            raw_price = order.get("total_price", 0)
            
            try:
                total_price = float(raw_price) if raw_price is not None else 0.0
            except (ValueError, TypeError):
                total_price = 0.0
                
            if created_at and isinstance(created_at, str):
                try:
                    dt_str = created_at.strip()
                    if len(dt_str) >= 19:
                        dt_utc = datetime.strptime(dt_str[:19], "%Y-%m-%d %H:%M:%S")
                        dt_vn = dt_utc + timedelta(hours=7)
                        
                        m_str = dt_vn.strftime("Tháng %m/%Y")
                        revenue_by_month[m_str] = revenue_by_month.get(m_str, 0.0) + total_price
                except Exception:
                    pass
                    
        st.markdown("### Doanh thu theo từng tháng (VNĐ)")
        if revenue_by_month:
            st.bar_chart(revenue_by_month)
        else:
            st.info("Chưa đủ dữ liệu thời gian hợp lệ để thống kê theo tháng.")
def analyze_frequently_bought_together():
    orders = database.list_orders()
    pair_counter = Counter()
    item_freq = Counter()
    suggestions = []

    for order in orders:
        items = order.get("items") or []
        item_names = list({item.get("name") for item in items if item.get("name")})

        for name in item_names:
            item_freq[name] += 1

        for i in range(len(item_names)):
            for j in range(i + 1, len(item_names)):
                pair = tuple(sorted([item_names[i], item_names[j]]))
                pair_counter[pair] += 1

    for (item_a, item_b), count in pair_counter.items():
        freq_a = item_freq[item_a]
        if freq_a > 0:
            percentage = (count / freq_a) * 100
            if percentage >= 20:
                suggestions.append({
                    "main": item_a,
                    "combo": item_b,
                    "percent": round(percentage)
                })
    suggestions.sort(key=lambda x: x["percent"], reverse=True)
    return suggestions

def render_combo_suggestions():
    st.subheader("🛒 Phân tích món thường mua cùng nhau")

    suggestions = analyze_frequently_bought_together()

    if suggestions:
        for item in suggestions:
            st.info(
                f"🔥 {item['percent']}% khách mua "
                f"{item['main']} thường mua thêm {item['combo']}"
            )
    else:
        st.info("Chưa đủ dữ liệu để phân tích.")

    st.divider()

    st.subheader("🎁 Tạo combo theo ý chủ quán")

    menu = database.list_menu()
    names = [item["name"] for item in menu]

    if len(names) >= 2:

        name = st.text_input("Tên combo")

        so_mon = st.number_input(
            "Số món trong combo",
            min_value=2,
            max_value=len(names),
            value=2,
            step=1
        )

        with st.form("create_combo"):

            mon_da_chon = []

            for i in range(so_mon):
                mon = st.selectbox(
                    f"Món {i + 1}",
                    names,
                    key=f"combo_mon_{i}"
                )
                mon_da_chon.append(mon)

            price = st.number_input(
                "Giá combo (VNĐ)",
                min_value=0,
                step=1000
            )

            if st.form_submit_button("🎁 Tạo combo"):

                if len(set(mon_da_chon)) < so_mon:
                    st.error("Không được chọn trùng món.")

                elif not name.strip() or price <= 0:
                    st.error("Vui lòng nhập đủ thông tin.")

                else:
                    st.success(f"Đã tạo combo: {name}")

    else:
        st.warning("Cần có ít nhất 2 món trong menu.")

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
    menu_tab, orders_tab, combo_tab , traffic_tab, discount_tab, dashboard_tab = st.tabs(["Quản lý menu", "Lịch sử đơn hàng", "Phân tích combo","Khung giờ cao điểm","Mã giảm giá","Doanh thu"])
    with menu_tab:
        st.markdown("### Thêm món mới")
        with st.form("add_menu_form"):
            name = st.text_input("Tên món")
            price = st.number_input("Giá (VNĐ)", min_value=0, step=1000, value=0)
            if price > 0:
                st.caption(f"👉 Giá đã chọn: **{price:,.0f} đ**".replace(",", "."))
            category = st.selectbox("Danh mục",options=["Cà phê", "Trà trái cây", "Soda", "Đá xay", "Đồ ăn nhẹ"],)
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
    with combo_tab:
        st.markdown("### Gợi ý món thường mua cùng nhau")
        render_combo_suggestions()            
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
    with traffic_tab:
       render_revenue_analytics()
    with discount_tab:
        st.markdown("### Quản lý mã giảm giá")
        with st.form("add_discount_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                discount_code = st.text_input("Mã giảm giá (VD: GIAM20, FREESHIP...)").upper()
            with col2:
                discount_percent = st.number_input("Phần trăm giảm (%)", min_value=1, max_value=100, value=10, step=1)
                
            if st.form_submit_button("Tạo/Cập nhật mã", type="primary"):
                if discount_code.strip():
                    database.add_discount(discount_code, discount_percent)
                    st.success(f"Đã lưu mã giảm giá: **{discount_code}** ({discount_percent}%)")
                    st.rerun()
                else:
                    st.error("Vui lòng nhập mã giảm giá.")
        with dashboard_tab:
            render_revenue_dashboard()

        st.markdown("---")
        st.markdown("### Danh sách mã đang có")
        discounts = database.list_discounts()
        if discounts:
            for d in discounts:
                col_a, col_b, col_c = st.columns([2, 2, 1])
                with col_a:
                    st.text(f"Mã: {d['code']}")
                with col_b:
                    st.text(f"Giảm: {d['discount_percent']}%")
                with col_c:
                    if st.button("Xóa", key=f"del_disc_{d['code']}"):
                        database.delete_discount(d['code'])
                        st.rerun()
        else:
            st.info("Chưa có mã giảm giá nào.")   

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
def render_revenue_dashboard():
  st.markdown("### 📊 Thống kê tổng quan")

  # Lấy dữ liệu xử lý thuần Python
  total_rev, total_ord, total_items, daily_stats = database.get_dashboard()

  # 1. Hiển thị 3 chỉ số tổng quan ở đầu trang
  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric(label="💰 Tổng doanh thu", value=f"{total_rev:,.0f}đ".replace(",", "."))
  with col2:
    st.metric(label="📄 Tổng đơn hàng", value=f"{total_ord} đơn")
  with col3:
    st.metric(label="🥤 Tổng món đã bán", value=f"{total_items} món")

  st.markdown("---")

  # 2. Vẽ biểu đồ cột doanh thu qua st.bar_chart (truyền dạng dictionary trực tiếp)
  st.markdown("### 📈 Biểu đồ doanh thu theo ngày")
  if daily_stats:
    # Gom lại thành dictionary {"Ngày": doanh_thu} để Streamlit vẽ biểu đồ
    chart_data = {item["order_date"]: item["daily_revenue"] for item in daily_stats}
    st.bar_chart(chart_data)
  else:
    st.info("Chưa có dữ liệu đơn hàng để hiển thị biểu đồ.")

  st.markdown("---")

  # 3. Hiển thị danh sách chi tiết theo từng ngày
  st.markdown("### 📋 Bảng số liệu chi tiết từng ngày")
  if daily_stats:
    for row in daily_stats:
      formatted_rev = f"{row['daily_revenue']:,.0f}đ".replace(",", ".")
      st.info(
          f"📅 **Ngày {row['order_date']}** | 📦 Số đơn: **{row['order_count']}**"
          f" đơn | 💰 Doanh thu: **{formatted_rev}**"
      )
  else:
    st.info("Chưa có dữ liệu đơn hàng.")