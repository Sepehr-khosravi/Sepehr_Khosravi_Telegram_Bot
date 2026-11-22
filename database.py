import sqlite3
from datetime import datetime
from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS free_slots (
            id INTEGER PRIMARY KEY,
            start_time TEXT NOT NULL,
            is_booked INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            slot_id INTEGER UNIQUE,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ---------- Slots ----------

def add_slot(start_time: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO free_slots (start_time) VALUES (?)", (start_time,))
    slot_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return slot_id

def remove_slot(slot_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    # Don't delete booked slots — prevents deleting someone's reservation
    cursor.execute("DELETE FROM free_slots WHERE id = ? AND is_booked = 0", (slot_id,))
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
    cursor.execute("SELECT id, start_time, is_booked FROM free_slots WHERE id = ?", (slot_id,))
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
    cursor.execute("SELECT 1 FROM bookings WHERE user_id = ? LIMIT 1", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def try_book_slot(slot_id: int, user_id: int) -> bool:
    """Atomic: only succeeds if slot is still free. Returns True on success."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE free_slots SET is_booked = 1 WHERE id = ? AND is_booked = 0",
            (slot_id,)
        )
        if cursor.rowcount == 0:
            conn.rollback()
            return False  # someone else grabbed it first
        cursor.execute(
            "INSERT INTO bookings (user_id, slot_id, created_at) VALUES (?, ?, ?)",
            (user_id, slot_id, datetime.now().isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
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
        WHERE b.user_id = ?
        ORDER BY s.start_time
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def cancel_booking(booking_id: int, user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT slot_id FROM bookings WHERE id = ? AND user_id = ?",
        (booking_id, user_id)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    slot_id = row[0]
    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    cursor.execute("UPDATE free_slots SET is_booked = 0 WHERE id = ?", (slot_id,))
    conn.commit()
    conn.close()
    return True