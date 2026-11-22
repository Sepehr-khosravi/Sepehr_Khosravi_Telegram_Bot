import os 
from dotenv import load_dotenv
import telebot

load_dotenv()

token = os.getenv("BOT_TOKEN")

if not token :
    raise ValueError("You need to set BOT_TOKEN in you .env file.")


bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message) :
    bot.reply_to(message, "Hey!, I'm your project booking bot. Use \book to find a free slot.")


if __name__ == "__main__" :
    print("Bot is running...")
    bot.infinity_polling()
