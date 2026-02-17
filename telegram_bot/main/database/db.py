import psycopg2

from telegram_bot.main.config import DATABASE_URL

def get_connection():
    return psycopg2.connect(DATABASE_URL)

