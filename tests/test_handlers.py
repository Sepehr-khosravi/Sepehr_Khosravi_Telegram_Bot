import pytest
from unittest.mock import MagicMock
import database
from handlers import slots as slots_handler
from handlers import admin as admin_handler


class FakeBot:
    """Captures handler registrations so tests can call them directly."""
    def __init__(self):
        self.handlers = {}          # command -> fn
        self.callbacks = []         # list of (func, predicate)
        self.replies = []

    def message_handler(self, commands):
        def deco(fn):
            for cmd in commands:
                self.handlers[cmd] = fn
            return fn
        return deco

    def callback_query_handler(self, func):
        def deco(fn):
            self.callbacks.append((fn, func))
            return fn
        return deco

    def reply_to(self, message, text, **kwargs):
        self.replies.append(("reply", text))

    def edit_message_text(self, text, *a, **kw):
        self.replies.append(("edit", text))

    def answer_callback_query(self, *a, **kw):
        self.replies.append(("answer", kw.get("text", "")))


def make_message(user_id, text="/slots"):
    m = MagicMock()
    m.from_user.id = user_id
    m.text = text
    m.chat.id = 999
    m.message_id = 1
    return m


def make_call(user_id, data):
    c = MagicMock()
    c.from_user.id = user_id
    c.data = data
    c.id = "cb"
    c.message.chat.id = 999
    c.message.message_id = 1
    return c


@pytest.fixture
def bot():
    return FakeBot()


@pytest.fixture
def wired_slots(bot):
    slots_handler.register(bot)
    return bot


@pytest.fixture
def wired_admin(bot, monkeypatch):
    monkeypatch.setattr(admin_handler, "ADMIN_ID", 777)
    admin_handler.register(bot)
    return bot


# ---------- /slots ----------

def test_slots_empty_db_says_no_slots(temp_db, wired_slots):
    wired_slots.handlers["slots"](make_message(111))
    assert wired_slots.replies[-1][1].startswith("No free times")


def test_slots_shows_buttons(temp_db, wired_slots):
    database.add_slot("2026-11-24 09:00")
    wired_slots.handlers["slots"](make_message(111))
    assert "Free times" in wired_slots.replies[-1][1]


def test_slots_blocked_if_user_already_booked(temp_db, wired_slots):
    sid = database.add_slot("2026-11-24 09:00")
    database.try_book_slot(sid, 111)
    wired_slots.handlers["slots"](make_message(111))
    assert "already have a booking" in wired_slots.replies[-1][1]


# ---------- pick + confirm ----------

def test_pick_shows_confirm_not_booking(temp_db, wired_slots):
    sid = database.add_slot("2026-11-24 09:00")
    pick_fn = [fn for fn, pred in wired_slots.callbacks
               if pred(make_call(111, f"pick:{sid}"))][0]
    pick_fn(make_call(111, f"pick:{sid}"))
    # DB must still be free — nothing booked from viewing
    assert database.get_slot(sid)[2] == 0
    assert "Book" in wired_slots.replies[-1][1]


def test_confirm_books_slot(temp_db, wired_slots):
    sid = database.add_slot("2026-11-24 09:00")
    confirm_fn = [fn for fn, pred in wired_slots.callbacks
                  if pred(make_call(111, f"confirm:{sid}"))][0]
    confirm_fn(make_call(111, f"confirm:{sid}"))
    assert database.get_slot(sid)[2] == 1
    assert database.has_active_booking(111) is True


def test_confirm_fails_if_slot_already_taken(temp_db, wired_slots):
    sid = database.add_slot("2026-11-24 09:00")
    database.try_book_slot(sid, 222)   # someone else grabbed it
    confirm_fn = [fn for fn, pred in wired_slots.callbacks
                  if pred(make_call(111, f"confirm:{sid}"))][0]
    confirm_fn(make_call(111, f"confirm:{sid}"))
    assert database.has_active_booking(111) is False
    # last reply should be an "edit" telling the user it's gone
    assert wired_slots.replies[-1][0] == "edit"
    assert "no longer" in wired_slots.replies[-1][1].lower() or \
           "taken" in wired_slots.replies[-1][1].lower()


# ---------- admin ----------

def test_add_slot_ignored_for_non_admin(temp_db, wired_admin):
    wired_admin.handlers["add_slot"](
        make_message(999, "/add_slot 2026-11-24 09:00")   # not the admin
    )
    assert database.get_all_slots() == []


def test_add_slot_works_for_admin(temp_db, wired_admin):
    wired_admin.handlers["add_slot"](
        make_message(777, "/add_slot 2026-11-24 09:00")
    )
    assert len(database.get_all_slots()) == 1


def test_add_slot_rejects_bad_format(temp_db, wired_admin):
    wired_admin.handlers["add_slot"](
        make_message(777, "/add_slot tomorrow 9am")
    )
    assert database.get_all_slots() == []
    assert "Bad format" in wired_admin.replies[-1][1]