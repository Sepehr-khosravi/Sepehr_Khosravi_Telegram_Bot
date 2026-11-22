import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = "booking.db"

# Your Telegram numeric user ID. Get it from @userinfobot on Telegram.
_admin_raw = os.getenv("ADMIN_ID")
ADMIN_ID = int(_admin_raw) if _admin_raw and _admin_raw.isdigit() else None

if not BOT_TOKEN:
    raise ValueError("You need to set BOT_TOKEN in your .env file.")