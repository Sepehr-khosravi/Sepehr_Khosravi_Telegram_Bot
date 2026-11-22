import pytest
import database
from database import (
    add_slot, remove_slot, get_free_slots, get_slot, get_all_slots,
    has_active_booking, try_book_slot, get_user_bookings, cancel_booking,
)

USER_A = 111
USER_B = 222


# ---------- Slots ----------

def test_add_slot_and_list(temp_db):
    slot_id = add_slot("2026-11-24 09:00")
    assert isinstance(slot_id, int)
    free = get_free_slots()
    assert free == [(slot_id, "2026-11-24 09:00")]


def test_multiple_slots_sorted_by_time(temp_db):
    add_slot("2026-11-24 14:00")
    add_slot("2026-11-24 09:00")
    times = [t for _, t in get_free_slots()]
    assert times == ["2026-11-24 09:00", "2026-11-24 14:00"]


def test_remove_free_slot(temp_db):
    slot_id = add_slot("2026-11-24 09:00")
    assert remove_slot(slot_id) is True
    assert get_free_slots() == []


def test_cannot_remove_booked_slot(temp_db):
    slot_id = add_slot("2026-11-24 09:00")
    try_book_slot(slot_id, USER_A)
    assert remove_slot(slot_id) is False        # protected
    assert get_slot(slot_id)[2] == 1            # still booked


# ---------- Booking ----------

def test_book_free_slot_succeeds(temp_db):
    slot_id = add_slot("2026-11-24 09:00")
    assert try_book_slot(slot_id, USER_A) is True
    assert has_active_booking(USER_A) is True
    assert get_slot(slot_id)[2] == 1            # is_booked = 1


def test_cannot_book_already_booked_slot(temp_db):
    slot_id = add_slot("2026-11-24 09:00")
    assert try_book_slot(slot_id, USER_A) is True
    # second attempt (even a different user) must fail
    assert try_book_slot(slot_id, USER_B) is False
    assert has_active_booking(USER_B) is False


def test_cannot_book_nonexistent_slot(temp_db):
    assert try_book_slot(9999, USER_A) is False


def test_booked_slot_disappears_from_free_list(temp_db):
    id1 = add_slot("2026-11-24 09:00")
    id2 = add_slot("2026-11-24 14:00")
    try_book_slot(id1, USER_A)
    free_ids = [i for i, _ in get_free_slots()]
    assert id1 not in free_ids
    assert id2 in free_ids


# ---------- Cancel ----------

def test_cancel_booking_frees_slot(temp_db):
    slot_id = add_slot("2026-11-24 09:00")
    try_book_slot(slot_id, USER_A)
    [booking_id, _] = get_user_bookings(USER_A)[0]
    assert cancel_booking(booking_id, USER_A) is True
    assert get_slot(slot_id)[2] == 0            # free again
    assert get_user_bookings(USER_A) == []


def test_cannot_cancel_someone_elses_booking(temp_db):
    slot_id = add_slot("2026-11-24 09:00")
    try_book_slot(slot_id, USER_A)
    [booking_id, _] = get_user_bookings(USER_A)[0]
    # USER_B tries to cancel USER_A's booking
    assert cancel_booking(booking_id, USER_B) is False
    assert has_active_booking(USER_A) is True  # untouched


def test_cancel_nonexistent_booking(temp_db):
    assert cancel_booking(9999, USER_A) is False


# ---------- User state ----------

def test_has_active_booking_false_for_new_user(temp_db):
    assert has_active_booking(USER_A) is False


def test_user_bookings_lists_own_only(temp_db):
    s1 = add_slot("2026-11-24 09:00")
    s2 = add_slot("2026-11-24 10:00")
    try_book_slot(s1, USER_A)
    try_book_slot(s2, USER_B)
    a = get_user_bookings(USER_A)
    b = get_user_bookings(USER_B)
    assert len(a) == 1 and a[0][1] == "2026-11-24 09:00"
    assert len(b) == 1 and b[0][1] == "2026-11-24 10:00"


# ---------- Race safety ----------

def test_double_book_race_only_one_wins(temp_db):
    """Two users try to book the same slot: only one succeeds."""
    slot_id = add_slot("2026-11-24 09:00")
    first = try_book_slot(slot_id, USER_A)
    second = try_book_slot(slot_id, USER_B)
    assert first is True
    assert second is False
    assert has_active_booking(USER_A) is True
    assert has_active_booking(USER_B) is False