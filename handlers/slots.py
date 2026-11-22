import html
from telebot.types import CallbackQuery
from database import (
    get_free_slots, get_slot, has_active_booking, try_book_slot
)
from keyboards import slots_keyboard, confirm_keyboard

def register(bot):

    @bot.message_handler(commands=['slots'])
    def list_slots(message):
        user_id = message.from_user.id
        if has_active_booking(user_id):
            bot.reply_to(message, "You already have a booking. Use /my to view or cancel it first.")
            return
        slots = get_free_slots()
        if not slots:
            bot.reply_to(message, "No free times right now. Try again later.")
            return
        bot.reply_to(
            message,
            "🕒 <b>Free times</b> — tap one to book:",
            reply_markup=slots_keyboard(),
            parse_mode="HTML"
        )

    @bot.callback_query_handler(func=lambda c: c.data.startswith("pick:"))
    def on_pick(call: CallbackQuery):
        slot_id = int(call.data.split(":")[1])
        slot = get_slot(slot_id)
        if not slot or slot[2] == 1:
            bot.answer_callback_query(call.id, "Sorry, that slot is no longer available.")
            bot.edit_message_text("❌ That slot was just taken. Use /slots again.",
                                  call.message.chat.id, call.message.message_id)
            return
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            f"Book <b>{html.escape(slot[1])}</b>?",
            call.message.chat.id, call.message.message_id,
            reply_markup=confirm_keyboard(slot_id),
            parse_mode="HTML"
        )

    @bot.callback_query_handler(func=lambda c: c.data.startswith("confirm:"))
    def on_confirm(call: CallbackQuery):
        slot_id = int(call.data.split(":")[1])
        user_id = call.from_user.id
        if has_active_booking(user_id):
            bot.answer_callback_query(call.id, "You already have a booking.")
            return
        ok = try_book_slot(slot_id, user_id)
        if ok:
            slot = get_slot(slot_id)
            bot.answer_callback_query(call.id, "Booked ✅")
            bot.edit_message_text(
                f"✅ Booked <b>{html.escape(slot[1])}</b>. See /my.",
                call.message.chat.id, call.message.message_id,
                parse_mode="HTML"
            )
        else:
            bot.answer_callback_query(call.id, "Too late — someone took it.")
            bot.edit_message_text("❌ That slot was just taken. Use /slots again.",
                                  call.message.chat.id, call.message.message_id)

    @bot.callback_query_handler(func=lambda c: c.data == "abort")
    def on_abort(call: CallbackQuery):
        bot.answer_callback_query(call.id, "Cancelled")
        bot.edit_message_text("No problem — nothing was booked. Use /slots to see times again.",
                              call.message.chat.id, call.message.message_id)