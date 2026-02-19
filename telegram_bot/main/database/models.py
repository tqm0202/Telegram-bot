import logging
import json

from .db import get_connection
from telegram_bot.main.config import ADMIN_ID

logger = logging.getLogger(__name__)

def create_tables():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE,
            username TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id BIGINT PRIMARY KEY,
            is_primary BOOLEAN NOT NULL DEFAULT FALSE
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS incoming_messages (
            id BIGSERIAL PRIMARY KEY,
            telegram_message_id BIGINT NOT NULL,
            chat_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            username TEXT,
            content_type TEXT NOT NULL,
            text TEXT,
            caption TEXT,
            file_id TEXT,
            file_unique_id TEXT,
            file_name TEXT,
            miype TEXT,
            file_size BIGINT,
            payload JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """)
        cursor.execute("SELECT COUNT(*) FROM admins")
        admins_count = cursor.fetchone()[0]
        if admins_count == 0:
            cursor.execute("""
            INSERT INTO admins (user_id, is_primary)
            VALUES (%s, TRUE)
            """, (ADMIN_ID,))
        conn.commit()
    except Exception:
        logger.exception("Failed to create tables")
        raise
    finally:
        conn.close()


def add_user(user_id, username):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO users (user_id, username)
        VALUES (%s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET username = EXCLUDED.username
        """, (user_id, username))
        conn.commit()
        logger.info("Upserted user into PostgreSQL: user_id=%s username=%s", user_id, username)
    except Exception:
        logger.exception("Failed to upsert user: user_id=%s username=%s", user_id, username)
        conn.rollback()
        raise
    finally:
        conn.close()


def is_admin(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def set_primary_admin(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE admins SET is_primary = FALSE")
        cursor.execute("""
        INSERT INTO admins (user_id, is_primary)
        VALUES (%s, TRUE)
        ON CONFLICT (user_id)
        DO UPDATE SET is_primary = TRUE
        """, (user_id,))
        conn.commit()
    except Exception:
        logger.exception("Failed to set primary admin: user_id=%s", user_id)
        conn.rollback()
        raise
    finally:
        conn.close()


def get_primary_admin_id():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT user_id
        FROM admins
        WHERE is_primary = TRUE
        ORDER BY user_id
        LIMIT 1
        """)
        row = cursor.fetchone()
        return row[0] if row else ADMIN_ID
    finally:
        conn.close()


def add_admin(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO admins (user_id, is_primary)
        VALUES (%s, FALSE)
        ON CONFLICT (user_id)
        DO NOTHING
        """, (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        logger.exception("Failed to add admin: user_id=%s", user_id)
        conn.rollback()
        raise
    finally:
        conn.close()


def remove_admin(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT is_primary FROM admins WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            return False, "not_found"
        if row[0]:
            return False, "primary"

        cursor.execute("DELETE FROM admins WHERE user_id = %s", (user_id,))
        conn.commit()
        return True, "deleted"
    except Exception:
        logger.exception("Failed to remove admin: user_id=%s", user_id)
        conn.rollback()
        raise
    finally:
        conn.close()


def list_admins():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT user_id, is_primary
        FROM admins
        ORDER BY is_primary DESC, user_id ASC
        """)
        return cursor.fetchall()
    finally:
        conn.close()


def save_incoming_message(
    *,
    telegram_message_id,
    chat_id,
    user_id,
    username,
    content_type,
    text=None,
    caption=None,
    file_id=None,
    file_unique_id=None,
    file_name=None,
    mime_type=None,
    file_size=None,
    payload=None,
):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO incoming_messages (
                telegram_message_id,
                chat_id,
                user_id,
                username,
                content_type,
                text,
                caption,
                file_id,
                file_unique_id,
                file_name,
                mime_type,
                file_size,
                payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            """,
            (
                telegram_message_id,
                chat_id,
                user_id,
                username,
                content_type,
                text,
                caption,
                file_id,
                file_unique_id,
                file_name,
                mime_type,
                file_size,
                json.dumps(payload) if payload is not None else None,
            ),
        )
        conn.commit()
    except Exception:
        logger.exception(
            "Failed to save incoming message: user_id=%s message_id=%s content_type=%s",
            user_id,
            telegram_message_id,
            content_type,
        )
        conn.rollback()
        raise
    finally:
        conn.close()
