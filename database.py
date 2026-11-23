import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS free_slots (
            id SERIAL PRIMARY KEY,
            start_time TEXT NOT NULL,
            is_booked INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            slot_id INTEGER UNIQUE REFERENCES free_slots(id),
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ---------- Slots ----------

def add_slot(start_time: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO free_slots (start_time) VALUES (%s) RETURNING id", (start_time,))
    slot_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return slot_id

def remove_slot(slot_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM free_slots WHERE id = %s AND is_booked = 0", (slot_id,))
    ok = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return ok

def get_free_slots():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, start_time FROM free_slots WHERE is_booked = 0 ORDER BY start_time")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_slot(slot_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, start_time, is_booked FROM free_slots WHERE id = %s", (slot_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_all_slots():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, start_time, is_booked FROM free_slots ORDER BY start_time")
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------- Bookings ----------

def has_active_booking(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM bookings WHERE user_id = %s LIMIT 1", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def try_book_slot(slot_id: int, user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE free_slots SET is_booked = 1 WHERE id = %s AND is_booked = 0",
            (slot_id,)
        )
        if cursor.rowcount == 0:
            conn.rollback()
            return False
        cursor.execute(
            "INSERT INTO bookings (user_id, slot_id, created_at) VALUES (%s, %s, %s)",
            (user_id, slot_id, datetime.now().isoformat())
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def get_user_bookings(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.id, s.start_time
        FROM bookings b JOIN free_slots s ON b.slot_id = s.id
        WHERE b.user_id = %s
        ORDER BY s.start_time
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def cancel_booking(booking_id: int, user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT slot_id FROM bookings WHERE id = %s AND user_id = %s",
        (booking_id, user_id)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    slot_id = row[0]
    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
    cursor.execute("UPDATE free_slots SET is_booked = 0 WHERE id = %s", (slot_id,))
    conn.commit()
    conn.close()
    return True