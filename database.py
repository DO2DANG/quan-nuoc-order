import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

try:
    import streamlit as st
except ImportError:
    st = None

try:
    from supabase import create_client
except ImportError:
    create_client = None


BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "orders.db"
MENU_FILE = BASE_DIR / "data" / "menu_mac_dinh.json"
_supabase_client = None


def _secret(name):
    value = os.getenv(name, "").strip()
    if value or st is None:
        return value
    try:
        return str(st.secrets.get(name, "")).strip()
    except (FileNotFoundError, KeyError, AttributeError):
        return ""


SUPABASE_URL = _secret("SUPABASE_URL")
SUPABASE_KEY = _secret("SUPABASE_KEY")


def _remote_client():
    global _supabase_client
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    if _supabase_client is None:
        if create_client is None:
            raise RuntimeError("Cài đặt supabase bằng requirements.txt trước khi dùng database từ xa.")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


def using_remote_database():
    return _remote_client() is not None


@contextmanager
def get_connection():
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
    finally:
        connection.commit()
        connection.close()


def init_db():
    if using_remote_database():
        client = _remote_client()
        if not client.table("menu").select("id").limit(1).execute().data and MENU_FILE.exists():
            menu_items = json.loads(MENU_FILE.read_text(encoding="utf-8"))
            client.table("menu").upsert([
                {
                    "id": item["id"],
                    "name": item["name"],
                    "price": item["price"],
                    "category": item["category"],
                    "image_url": item.get("image", ""),
                    "description": item.get("description", ""),
                }
                for item in menu_items
            ]).execute()
        return
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS menu (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                category TEXT NOT NULL,
                image_url TEXT,
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS discounts (
                code TEXT PRIMARY KEY,
                discount_percent INTEGER NOT NULL CHECK(discount_percent > 0 AND discount_percent <= 100),
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                table_num TEXT NOT NULL,
                UNIQUE(name, phone, table_num)
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                items TEXT NOT NULL,
                total_price REAL NOT NULL CHECK(total_price >= 0),
                status TEXT NOT NULL DEFAULT 'Chờ pha chế',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            );
            """
        )

        if MENU_FILE.exists():
            menu_items = json.loads(
                MENU_FILE.read_text(encoding="utf-8")
            )

            for item in menu_items:
                connection.execute(
                    """
                    INSERT INTO menu
                    (id, name, price, category, image_url, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        name = excluded.name,
                        price = excluded.price,
                        category = excluded.category,
                        image_url = excluded.image_url,
                        description = excluded.description
                    """,
                    (
                        item["id"],
                        item["name"],
                        item["price"],
                        item["category"],
                        item.get("image", ""),
                        item.get("description", "")
                    )
                )

def list_menu():
    client = _remote_client()
    if client:
        return client.table("menu").select("*").order("category").order("name").execute().data
    with get_connection() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM menu ORDER BY category, name")]


def add_menu_item(name, price, category, image_url, description=""):
    item_id = f"item-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    client = _remote_client()
    if client:
        client.table("menu").insert({"id": item_id, "name": name.strip(), "price": price, "category": category.strip(), "image_url": image_url.strip(), "description": description.strip()}).execute()
        return
    with get_connection() as connection:
        connection.execute("INSERT INTO menu (id, name, price, category, image_url, description) VALUES (?, ?, ?, ?, ?, ?)", (item_id, name.strip(), price, category.strip(), image_url.strip(), description.strip()))


def update_menu_item(item_id, name, price, category, image_url, description=""):
    client = _remote_client()
    if client:
        client.table("menu").update({"name": name.strip(), "price": price, "category": category.strip(), "image_url": image_url.strip(), "description": description.strip()}).eq("id", item_id).execute()
        return
    with get_connection() as connection:
        connection.execute("UPDATE menu SET name = ?, price = ?, category = ?, image_url = ?, description = ? WHERE id = ?", (name.strip(), price, category.strip(), image_url.strip(), description.strip(), item_id))


def delete_menu_item(item_id):
    client = _remote_client()
    if client:
        client.table("menu").delete().eq("id", item_id).execute()
        return
    with get_connection() as connection:
        connection.execute("DELETE FROM menu WHERE id = ?", (item_id,))


def save_order(name, phone, table_num, items, total_price):
    client = _remote_client()
    if client:
        customer_response = client.table("customers").select("id").eq("name", name.strip()).eq("phone", phone.strip()).eq("table_num", table_num.strip()).limit(1).execute()
        if customer_response.data:
            customer_id = customer_response.data[0]["id"]
        else:
            customer_response = client.table("customers").insert({"name": name.strip(), "phone": phone.strip(), "table_num": table_num.strip()}).execute()
            customer_id = customer_response.data[0]["id"]
        return client.table("orders").insert({"customer_id": customer_id, "items": items, "total_price": total_price}).execute().data[0]["id"]
    with get_connection() as connection:
        customer = connection.execute("SELECT id FROM customers WHERE name = ? AND phone = ? AND table_num = ?", (name.strip(), phone.strip(), table_num.strip())).fetchone()
        if customer is None:
            customer_id = connection.execute("INSERT INTO customers (name, phone, table_num) VALUES (?, ?, ?)", (name.strip(), phone.strip(), table_num.strip())).lastrowid
        else:
            customer_id = customer["id"]
        return connection.execute("INSERT INTO orders (customer_id, items, total_price) VALUES (?, ?, ?)", (customer_id, json.dumps(items, ensure_ascii=False), total_price)).lastrowid


def list_orders(date_value="", phone=""):
    client = _remote_client()
    if client:
        query = client.table("orders").select("*, customers(name, phone, table_num)").order("created_at", desc=True)
        if date_value:
            query = query.gte("created_at", f"{date_value}T00:00:00").lt("created_at", f"{date_value}T23:59:59.999999")
        rows = []
        for order in query.execute().data:
            customer = order.pop("customers", {}) or {}
            order.update({"customer_name": customer.get("name", ""), "phone": customer.get("phone", ""), "table_num": customer.get("table_num", "")})
            if not phone.strip() or phone.strip() in order["phone"]:
                rows.append(order)
        return rows
    query = "SELECT orders.*, customers.name AS customer_name, customers.phone, customers.table_num FROM orders JOIN customers ON customers.id = orders.customer_id WHERE 1 = 1"
    params = []
    if date_value:
        query += " AND date(orders.created_at) = ?"
        params.append(date_value)
    if phone.strip():
        query += " AND customers.phone LIKE ?"
        params.append(f"%{phone.strip()}%")
    query += " ORDER BY orders.created_at DESC"
    with get_connection() as connection:
        rows = [dict(row) for row in connection.execute(query, params)]
    for row in rows:
        row["items"] = json.loads(row["items"])
    return rows


def update_order_status(order_id, status):
    client = _remote_client()
    if client:
        client.table("orders").update({"status": status}).eq("id", order_id).execute()
        return
    with get_connection() as connection:
        connection.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
def list_discounts():
    client = _remote_client()
    if client:
        return client.table("discounts").select("*").order("created_at", desc=True).execute().data
    with get_connection() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM discounts ORDER BY created_at DESC")]

def add_discount(code, percent):
    client = _remote_client()
    if client:
        client.table("discounts").upsert({"code": code.strip().upper(), "discount_percent": percent, "active": True}).execute()
        return
    with get_connection() as connection:
        connection.execute(
            "INSERT OR REPLACE INTO discounts (code, discount_percent, active) VALUES (?, ?, 1)",
            (code.strip().upper(), percent)
        )

def delete_discount(code):
    client = _remote_client()
    if client:
        client.table("discounts").delete().eq("code", code).execute()
        return
    with get_connection() as connection:
        connection.execute("DELETE FROM discounts WHERE code = ?", (code,))

def get_discount_percent(code):
    client = _remote_client()
    if client:
        response = client.table("discounts").select("discount_percent").eq("code", code.strip().upper()).eq("active", True).limit(1).execute()
        return response.data[0]["discount_percent"] if response.data else 0
    with get_connection() as connection:
        row = connection.execute(
            "SELECT discount_percent FROM discounts WHERE code = ? AND active = 1",
            (code.strip().upper(),)
        ).fetchone()
        return row["discount_percent"] if row else 0
def get_dashboard():
  """Thống kê doanh thu và đơn hàng theo ngày dùng hoàn toàn Python thuần """
  orders = list_orders() 
  
  total_revenue = sum(o["total_price"] for o in orders)
  total_orders = len(orders)
  total_items_sold = 0

  daily_revenue = {}
  daily_order_count = {}

  for o in orders:
    # Tính tổng số món đã bán
    for item in o["items"]:
      total_items_sold += item.get("quantity", 1)

    # Lấy ngày tạo đơn (cắt chuỗi lấy phần YYYY-MM-DD)
    date_str = o["created_at"].split()[0] if "created_at" in o else "Khác"

    # Cộng dồn doanh thu và số đơn theo ngày
    daily_revenue[date_str] = daily_revenue.get(date_str, 0) + o["total_price"]
    daily_order_count[date_str] = daily_order_count.get(date_str, 0) + 1

  # Sắp xếp danh sách các ngày theo thứ tự mới nhất lên đầu
  sorted_dates = sorted(daily_revenue.keys(), reverse=True)
  
  daily_stats = []
  for d in sorted_dates:
    daily_stats.append({
        "order_date": d,
        "order_count": daily_order_count[d],
        "daily_revenue": daily_revenue[d]
    })

  return total_revenue, total_orders, total_items_sold, daily_stats
def get_order_by_id(order_id):
    client = _remote_client()

    # Nếu đang sử dụng Supabase
    if client:
        response = (
            client.table("orders")
            .select("*, customers(name, phone, table_num)")
            .eq("id", order_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        order = response.data[0]

        # Lấy thông tin khách hàng
        customer = order.pop("customers", {}) or {}

        order["name"] = customer.get("name", "")
        order["phone"] = customer.get("phone", "")
        order["table_num"] = customer.get("table_num", "")

        # Xử lý items
        if isinstance(order["items"], str):
            order["items"] = json.loads(order["items"])

        return order

    # Nếu đang sử dụng SQLite
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                orders.id,
                customers.name,
                customers.phone,
                customers.table_num,
                orders.items,
                orders.total_price,
                orders.status,
                orders.created_at
            FROM orders
            JOIN customers
                ON orders.customer_id = customers.id
            WHERE orders.id = ?
            """,
            (order_id,)
        ).fetchone()

        if row is None:
            return None

        order = dict(row)

        if isinstance(order["items"], str):
            order["items"] = json.loads(order["items"])

        return order