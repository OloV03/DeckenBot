import sqlite3

import gspread
import telebot

token = 'your_telegram_bot_tokn=en'
google_id = 'your_google_id'

montage_info = {}
bot = telebot.TeleBot(token)
# открываем нашу таблицу
sh = gspread.service_account(filename='servise_account.json').open_by_key(google_id)

# подключаем БД
conn = sqlite3.connect("database_name", check_same_thread=False)
cursor = conn.cursor()

# получение id "главного" admina
cursor.execute(f'SELECT admin_id FROM admins WHERE main = {1}')
admin_id = cursor.fetchone()[0]
# -------------------------------
