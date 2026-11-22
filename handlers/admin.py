import html
from datetime import datetime
from telebot.types import CallbackQuery, Message
from config import ADMIN_ID
from database import add_slot, remove_slot, get_all_slots
from keyboards import admin_slots_keyboard

def _is_admin(user_id: int) -> bool:
    return ADMIN_ID is not None and user_id == ADMIN_ID

def _parse_dt(text: str) -> str | None:
    """Accepts 'YYYY-MM-DD HH:MM'. Returns normalized string or None."""
    try:
        dt = datetime.strptime(text.strip(), "%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return None

def register(bot):

    @bot.message_handler(commands=['add_slot'])
    def cmd_add_slot(message: Message):
        if not _is_admin(message.from_user.id):
            bot.reply_to(message, "⛔ Admins only.")
            return
        # /add_slot 2026-11-24 09:00
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "Usage: <code>/add_slot YYYY-MM-DD HH:MM</code>", parse_mode="HTML")
            return
        normalized = _parse_dt(parts[1])
        if not normalized:
            bot.reply_to(message, "❌ Bad format. Use <code>YYYY-MM-DD HH:MM</code>", parse_mode="HTML")
            return
        slot_id = add_slot(normalized)
        bot.reply_to(message, f"✅ Added slot #{slot_id}: {normalized}")

    @bot.message_handler(commands=['all'])
    def cmd_all(message: Message):
        if not _is_admin(message.from_user.id):
            bot.reply_to(message, "⛔ Admins only.")
            return
        rows = get_all_slots()
        if not rows:
            bot.reply_to(message, "No slots at all. Use /add_slot.")
            return
        bot.reply_to(
            message,
            "🗂 <b>All slots</b> — tap 🗑 to remove a <i>free</i> one:",
            reply_markup=admin_slots_keyboard(),
            parse_mode="HTML"
        )

    @bot.callback_query_handler(func=lambda c: c.data.startswith("adminremove:"))
    def on_remove(call: CallbackQuery):
        if not _is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Admins only.")
            return
        slot_id = int(call.data.split(":")[1])
        if remove_slot(slot_id):
            bot.answer_callback_query(call.id, "Removed")
            bot.edit_message_text("✅ Slot removed.",
                                  call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "Can't remove (may be booked).")