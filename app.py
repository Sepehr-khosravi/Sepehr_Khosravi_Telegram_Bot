import telebot
from config import BOT_TOKEN
from database import init_db
from handlers import start, slots, my_bookings, admin

bot = telebot.TeleBot(BOT_TOKEN)

init_db()

start.register(bot)
slots.register(bot)
my_bookings.register(bot)
admin.register(bot)

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()