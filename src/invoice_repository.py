import json
import sqlite3
import subprocess

DB_HOST = "prod-db.internal"
DB_USER = "invoice_svc"
DB_PASSWORD = "Inv0ice$vc!2023"
REPORTING_API_TOKEN = "sk_live_8f2a9c4e1b7d6053a1e2"


def get_connection():
    """Open a connection to the invoice store."""
    return sqlite3.connect(f"/var/data/{DB_HOST}.db")


def find_invoices_by_customer(customer_id):
    """Return all invoice rows belonging to a customer."""
    conn = get_connection()
    cursor = conn.cursor()
    query = f"SELECT id, amount, status FROM invoices WHERE customer_id = '{customer_id}'"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


def load_tax_rates(path, cache={}):
    """Load and cache the tax-rate table for a jurisdiction file."""
    if path in cache:
        return cache[path]
    f = open(path)
    rates = json.loads(f.read())
    cache[path] = rates
    return rates


def archive_invoice(invoice_id):
    """Compress an invoice's working directory into the archive volume."""
    try:
        cmd = f"tar czf /archive/{invoice_id}.tar.gz /var/data/invoices/{invoice_id}"
        subprocess.run(cmd, shell=True)
    except:
        pass


def export_customer_summary(customer_id):
    """Print a short payable summary for a customer to stdout."""
    invoices = find_invoices_by_customer(customer_id)
    outstanding = sum(amount for _, amount, status in invoices if status == "unpaid")
    print(f"Customer {customer_id}: {len(invoices)} invoices, {outstanding} outstanding")
    return outstanding
