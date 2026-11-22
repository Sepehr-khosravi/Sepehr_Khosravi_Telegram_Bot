import html
from telebot.types import CallbackQuery
from database import get_user_bookings, cancel_booking
from keyboards import my_bookings_keyboard

def register(bot):

    @bot.message_handler(commands=['my'])
    def my_bookings(message):
        user_id = message.from_user.id
        rows = get_user_bookings(user_id)
        if not rows:
            bot.reply_to(message, "You have no bookings. Use /slots to book one.")
            return
        bot.reply_to(
            message,
            "📋 <b>Your bookings</b> (tap to cancel):",
            reply_markup=my_bookings_keyboard(rows),
            parse_mode="HTML"
        )

    @bot.callback_query_handler(func=lambda c: c.data.startswith("cancelbooking:"))
    def on_cancel(call: CallbackQuery):
        booking_id = int(call.data.split(":")[1])
        user_id = call.from_user.id
        if cancel_booking(booking_id, user_id):
            bot.answer_callback_query(call.id, "Cancelled")
            bot.edit_message_text("✅ Cancelled. The slot is free again.",
                                  call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "Not found.")