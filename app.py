import os
import telebot
from flask import Flask, request, abort
from config import BOT_TOKEN
from database import init_db
from handlers import start, slots, my_bookings, admin

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

init_db()

start.register(bot)
slots.register(bot)
my_bookings.register(bot)
admin.register(bot)

@app.route(f"/api/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "", 200
    else:
        abort(403)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running.", 200

if __name__ == "__main__":
    app.run(port=5000)