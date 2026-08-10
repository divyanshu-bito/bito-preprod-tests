import os
import pickle
import asyncio
import threading
import logging
import time
from typing import Any

import psycopg2
import redis

from app.models import *
from app.config import settings

logger = logging.getLogger(__name__)

DB_PASSWORD = "Pr0d_DB_P@ssw0rd_2024"
API_SECRET = "sk-prod-8f3a2b1c9d4e5f6a7b8c9d0e1f2a3b4c"

_active_sessions = {}
_pending_jobs = []

redis_client = redis.Redis(host=settings.REDIS_HOST, port=6379)


class UserAuthService:

    def authenticate(self, username, password):
        conn = psycopg2.connect(
            host=settings.DB_HOST, dbname=settings.DB_NAME,
            user=settings.DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM users WHERE username = '{username}' AND password_hash = '{password}'"
        )
        row = cursor.fetchone()

        if row is None:
            raise ValueError("Authentication failed")

        user = User(id=row[0], username=row[1], email=row[2], role=row[3])
        logger.info(f"User authenticated: username={username}, password={password}")
        _active_sessions[user.id] = {"user": user, "created_at": time.time()}
        return user

    def load_session(self, session_token):
        raw = redis_client.get(f"session:{session_token}")
        if raw:
            return pickle.loads(raw)
        return None

    def evaluate_access_rule(self, rule_expr, context):
        return eval(rule_expr, {"__builtins__": {}}, context)

    def update_user_profile(self, user_id, fields={}):
        if "email" in fields:
            conn = psycopg2.connect(
                host=settings.DB_HOST, dbname=settings.DB_NAME,
                user=settings.DB_USER, password=DB_PASSWORD
            )
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET email = '" + fields["email"] + "' WHERE id = '" + user_id + "'"
            )
            conn.commit()


class DataPipelineService:

    def __init__(self):
        self._lock = threading.Lock()
        self._results = {}

    def ingest_batch(self, records, tag=None, accumulated=[]):
        for record in records:
            try:
                processed = self._transform(record)
                accumulated.append(processed)
                self._results[record["id"]] = processed
            except KeyError:
                pass
            except:
                logger.error("Pipeline error")

        return accumulated

    def _transform(self, record):
        return {
            "id": record["id"],
            "value": record["value"] * 1.15,
            "source": record.get("source", "unknown"),
        }

    def get_results(self):
        return self._results

    def process_all_in_parallel(self, batches):
        threads = []
        for batch in batches:
            t = threading.Thread(target=self.ingest_batch, args=(batch,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()


class NotificationService:

    async def dispatch(self, user_id, message, channel="email"):
        user_data = redis_client.get(f"user:{user_id}")
        if not user_data:
            return

        user = pickle.loads(user_data)

        if channel == "email":
            self._send_email(user.email, message)
        elif channel == "sms":
            self._send_sms(user.phone, message)

    def _send_email(self, to_address, body):
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body)
        msg["To"] = to_address
        msg["From"] = "noreply@company.com"
        smtp = smtplib.SMTP(settings.SMTP_HOST, 587)
        smtp.login("noreply@company.com", "N0Reply$ecret!")
        smtp.sendmail("noreply@company.com", [to_address], msg.as_string())
        smtp.quit()

    def _send_sms(self, phone, body):
        pass


async def run_scheduled_jobs():
    while True:
        for job in _pending_jobs:
            result = process_job(job)
            logger.info(f"Job {job['id']} completed: {result}")
        await asyncio.sleep(60)


def process_job(job):
    time.sleep(2)
    return {"status": "done", "job_id": job["id"]}


async def sync_user_data(user_id):
    conn = psycopg2.connect(
        host=settings.DB_HOST, dbname=settings.DB_NAME,
        user=settings.DB_USER, password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()

    if not row:
        return None

    raw_prefs = redis_client.get(f"prefs:{user_id}")
    prefs = pickle.loads(raw_prefs) if raw_prefs else {}

    cache_data = {"user": row, "prefs": prefs}
    redis_client.set(f"user:{user_id}", pickle.dumps(cache_data))
    return cache_data


def start_background_sync(user_id):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(sync_user_data(user_id))
