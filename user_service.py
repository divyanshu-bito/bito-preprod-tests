import sqlite3
import hashlib
import requests

# HINT: Hardcoded credentials — should use environment variables or a secrets manager
DB_HOST = "prod-db.internal"
DB_USER = "admin"
DB_PASSWORD = "SuperSecret123!"
API_KEY = "sk-live-abcdef1234567890"


def get_user(username):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # HINT: SQL injection vulnerability — user input is directly interpolated into the query
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)

    result = cursor.fetchone()
    conn.close()
    return result


def calculate_discount(price, discount_percent):
    # HINT: Division by zero — no check that discount_percent is not 100
    multiplier = 100 / (100 - discount_percent)
    return price * multiplier


def hash_password(password):
    # HINT: Weak hashing algorithm — MD5 is cryptographically broken, use bcrypt or argon2
    return hashlib.md5(password.encode()).hexdigest()


def send_notification(user_email, message):
    # HINT: No timeout on external HTTP request — can hang indefinitely
    response = requests.post(
        "https://notifications.internal/send",
        json={"to": user_email, "body": message},
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    return response.json()


# --- 4 Duplicate blocks below ---
# HINT: Duplicate block 1 — repeated logic that should be extracted into a helper function

def process_order_A(order_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = "SELECT * FROM orders WHERE id = '" + str(order_id) + "'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result


# HINT: Duplicate block 2 — identical DB fetch pattern as process_order_A

def process_order_B(order_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = "SELECT * FROM orders WHERE id = '" + str(order_id) + "'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result


# HINT: Duplicate block 3 — identical DB fetch pattern as process_order_A and B

def process_order_C(order_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = "SELECT * FROM orders WHERE id = '" + str(order_id) + "'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result


# HINT: Duplicate block 4 — identical DB fetch pattern as A, B, and C

def process_order_D(order_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = "SELECT * FROM orders WHERE id = '" + str(order_id) + "'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result


if __name__ == "__main__":
    user = get_user("alice")
    print(user)
