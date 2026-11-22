# Project Booking Bot

A Telegram bot that lets clients see your free time slots and book one,
and lets you (the admin) manage those slots without touching code.

Stack: Python, pyTelegramBotAPI, SQLite, python-dotenv.

---

## Features

### For clients
- /slots — see free times as buttons (viewing does NOT book anything).
- Tap a slot -> confirm screen -> only "Confirm" writes the booking.
- /my — see your bookings and cancel them.
- One active booking per user (no double-booking).
- Race-safe: if two users tap the same slot, only one wins.

### For the admin (you)
- /add_slot YYYY-MM-DD HH:MM — add a free time.
- /all — list all slots, tap trash to remove a free one.
- Admin commands locked to ADMIN_ID in .env.

---

## Project structure

my-bot/
  .env                  secrets (not committed)
  .env.example          template (committed)
  .gitignore
  app.py                entry point, wires modules
  config.py             env vars
  database.py           all SQLite logic
  keyboards.py          inline keyboard builders
  handlers/
    __init__.py
    start.py            /start, /help
    slots.py            /slots + pick + confirm
    my_bookings.py      /my + cancel
    admin.py            /add_slot, /all
  booking.db            auto-created (not committed)

Design rule: handlers never touch SQL. All DB access goes through
database.py. All keyboards go in keyboards.py. app.py only wires things.

---

## Setup

1. Enter the project:
   cd my-bot

2. Create and activate venv:
   Windows:        python -m venv .venv && .venv\Scripts\activate
   macOS / Linux:  python3 -m venv .venv && source .venv/bin/activate

3. Install dependencies:
   pip install pyTelegramBotAPI python-dotenv

4. Create a bot: message @BotFather on Telegram, send /newbot,
   copy the token.

5. Get your numeric ID: message @userinfobot.

6. Create .env with:
   BOT_TOKEN=your_token_here
   ADMIN_ID=your_numeric_id

7. Run:
   python app.py

---

## Usage

Admin:
  /add_slot 2026-11-24 09:00
  /add_slot 2026-11-24 14:00
  /all

Client:
  /slots   tap a time, then Confirm
  /my      view or cancel bookings
  /help    command list

---

## Test checklist

1. Start the bot.
2. As admin, add two slots.
3. /slots shows both buttons.
4. Tap one -> confirm screen (DB unchanged).
5. Confirm -> booked.
6. /my -> your booking, tap cancel -> slot free again.
7. Book the freed slot from a second account.
8. /slots again -> "You already have a booking."

---

## Data model

free_slots: id, start_time (YYYY-MM-DD HH:MM), is_booked (0/1)
bookings:   id, user_id, slot_id (UNIQUE), created_at

---

## Troubleshooting

ModuleNotFoundError telebot    -> venv not active
ValueError BOT_TOKEN           -> .env missing or misnamed
401 Unauthorized               -> wrong token
409 Conflict                   -> two bot instances running
"Admins only"                  -> ADMIN_ID wrong
"Bad format" on /add_slot      -> must be YYYY-MM-DD HH:MM

---

## Roadmap

- [ ] Reminders before a booked slot
- [ ] Note/description per booking
- [ ] Time-zone support
- [ ] Webhooks for production
- [ ] Web admin dashboard

---

## Security

- .env is gitignored. Never commit your bot token.
- Token leak? Revoke via BotFather with /revoke, then update .env.

---

## License

Personal project. Use it, learn from it, change it.
