# Tests

How to run and understand the tests for this bot.

## Install test deps

    pip install pytest pytest-cov

## Run all tests

    pytest

## Run with coverage

    pytest --cov=database --cov=handlers --cov-report=term-missing

## Run one file

    pytest tests/test_database.py
    pytest tests/test_handlers.py

## Run one test

    pytest tests/test_database.py::test_double_book_race_only_one_wins

## What is tested

- test_database.py  -> booking rules, cancel, race safety (no Telegram needed)
- test_handlers.py  -> handler flow with a fake bot (no real token needed)

## Key behaviors verified

- /slots never books; only the Confirm tap writes to the DB.
- Two users tapping the same slot: only one wins.
- A user cannot hold two active bookings.
- A user cannot cancel someone else's booking.
- Admin commands are locked to ADMIN_ID.

## Notes

- Each test uses a fresh temp SQLite DB (see conftest.py).
- No network, no real bot token required. Runs in < 1s.
- If config.py complains about a missing BOT_TOKEN, conftest.py sets
  dummy env vars before import, so tests still run.
