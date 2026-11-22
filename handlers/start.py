def register(bot):
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(
            message,
            "👋 <b>Project Booking Bot</b>\n\n"
            "Commands:\n"
            "/slots — see free times and book one\n"
            "/my — your bookings (and cancel)\n"
            "/help — this message",
            parse_mode="HTML"
        )