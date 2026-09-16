import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "orders.db"
MENU_FILE = BASE_DIR / "data" / "menu_mac_dinh.json"


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
    with get_connection() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM menu ORDER BY category, name")]


def add_menu_item(name, price, category, image_url, description=""):
    item_id = f"item-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    with get_connection() as connection:
        connection.execute("INSERT INTO menu (id, name, price, category, image_url, description) VALUES (?, ?, ?, ?, ?, ?)", (item_id, name.strip(), price, category.strip(), image_url.strip(), description.strip()))


def update_menu_item(item_id, name, price, category, image_url, description=""):
    with get_connection() as connection:
        connection.execute("UPDATE menu SET name = ?, price = ?, category = ?, image_url = ?, description = ? WHERE id = ?", (name.strip(), price, category.strip(), image_url.strip(), description.strip(), item_id))


def delete_menu_item(item_id):
    with get_connection() as connection:
        connection.execute("DELETE FROM menu WHERE id = ?", (item_id,))


def save_order(name, phone, table_num, items, total_price):
    with get_connection() as connection:
        customer = connection.execute("SELECT id FROM customers WHERE name = ? AND phone = ? AND table_num = ?", (name.strip(), phone.strip(), table_num.strip())).fetchone()
        if customer is None:
            customer_id = connection.execute("INSERT INTO customers (name, phone, table_num) VALUES (?, ?, ?)", (name.strip(), phone.strip(), table_num.strip())).lastrowid
        else:
            customer_id = customer["id"]
        return connection.execute("INSERT INTO orders (customer_id, items, total_price) VALUES (?, ?, ?)", (customer_id, json.dumps(items, ensure_ascii=False), total_price)).lastrowid


def list_orders(date_value="", phone=""):
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
    with get_connection() as connection:
        connection.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
def list_discounts():
    with get_connection() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM discounts ORDER BY created_at DESC")]

def add_discount(code, percent):
    with get_connection() as connection:
        connection.execute(
            "INSERT OR REPLACE INTO discounts (code, discount_percent, active) VALUES (?, ?, 1)",
            (code.strip().upper(), percent)
        )

def delete_discount(code):
    with get_connection() as connection:
        connection.execute("DELETE FROM discounts WHERE code = ?", (code,))

def get_discount_percent(code):
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