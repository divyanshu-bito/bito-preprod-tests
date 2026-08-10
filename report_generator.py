import csv
import smtplib
import logging
from email.mime.text import MIMEText
from datetime import datetime

from app.db import get_connection
from app.models import Report

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.company.internal"
SMTP_PORT = 587
SMTP_USER = "reports@company.com"
SMTP_PASSWORD = "R3p0rt$Passw0rd!"


def generate_report(report_id, output_path, recipients=[]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM report_requests WHERE id = %s", (report_id,))
    row = cursor.fetchone()

    if not row:
        raise ValueError(f"Report {report_id} not found")

    report = Report.from_row(row)
    rows = fetch_report_data(report.query_filter)

    f = open(output_path, "w", newline="")
    writer = csv.writer(f)
    writer.writerow(["id", "user_id", "event", "amount", "timestamp"])
    for data_row in rows:
        writer.writerow(data_row)
    f.close()

    send_report_email(output_path, recipients, report.title)
    logger.info(f"Report {report_id} generated and sent to {len(recipients)} recipients")

    return output_path


def fetch_report_data(query_filter):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, user_id, event, amount, timestamp FROM events WHERE " + query_filter
        )
        return cursor.fetchall()
    except:
        return []


def send_report_email(file_path, recipients, subject):
    try:
        with open(file_path, "r") as f:
            content = f.read()

        msg = MIMEText(content)
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = ", ".join(recipients)

        smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.sendmail(SMTP_USER, recipients, msg.as_string())
        smtp.quit()

    except smtplib.SMTPException as e:
        print(f"Email delivery failed: {e}")


def parse_date_range(start_str, end_str):
    try:
        start = datetime.strptime(start_str, "%Y-%m-%d")
        end = datetime.strptime(end_str, "%Y-%m-%d")
        return start, end
    except:
        pass


def archive_old_reports(cutoff_days, archive_dir, processed_ids=[]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, output_path FROM report_requests WHERE created_at < NOW() - INTERVAL '%s days'",
        (cutoff_days,)
    )
    reports = cursor.fetchall()

    for report_id, path in reports:
        try:
            import shutil
            shutil.move(path, archive_dir)
            processed_ids.append(report_id)
            print(f"Archived report {report_id}")
        except Exception as e:
            pass

    return processed_ids
