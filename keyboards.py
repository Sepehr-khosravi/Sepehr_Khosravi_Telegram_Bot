from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_free_slots

def slots_keyboard():
    slots = get_free_slots()
    kb = InlineKeyboardMarkup()
    for slot_id, start_time in slots:
        kb.add(InlineKeyboardButton(
            text=f"🕒 {start_time}",
            callback_data=f"pick:{slot_id}"
        ))
    return kb

def confirm_keyboard(slot_id: int):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(text="✅ Confirm", callback_data=f"confirm:{slot_id}"),
        InlineKeyboardButton(text="❌ Cancel",  callback_data="abort")
    )
    return kb

def my_bookings_keyboard(bookings):
    kb = InlineKeyboardMarkup()
    for booking_id, start_time in bookings:
        kb.add(InlineKeyboardButton(
            text=f"❌ Cancel {start_time}",
            callback_data=f"cancelbooking:{booking_id}"
        ))
    return kb

def admin_slots_keyboard():
    from database import get_all_slots
    kb = InlineKeyboardMarkup()
    for slot_id, start_time, is_booked in get_all_slots():
        label = f"🗑 {start_time}" + (" (booked)" if is_booked else "")
        kb.add(InlineKeyboardButton(text=label, callback_data=f"adminremove:{slot_id}"))
    return kb