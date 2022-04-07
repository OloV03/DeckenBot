from datetime import datetime, timedelta
import telebot
import time
from config import bot, sh, cursor, admin_id
from AdminCommand import admin_handler
from NewMontage import montage_number


# ---------------------------------------
# Список доступных команд:
# /start - начало работы
# /new_work - внесение нового монтажа
# /admin - команды для администратора
# /restart - обновление таблицы монтажей
# ---------------------------------------

# Заполнение таблицы google
def table_info(id):
    today = datetime.today()
    if today.strftime('%d.%m') != sh.sheet1.cell(1, 1).value[4:9]:
        bot.send_message(id, 'Следующие 30 минут бот будет обновлять таблицу')
        week = {1: 'Пн', 2: 'Вт', 3: 'Ср', 4: 'Чт', 5: 'Пт', 6: 'Сб'}
        week_date = {}
        k = 1
        for i in range(1, 28):
            while True:
                try:
                    if i != 7 and i != 14 and i != 21:
                        sh.sheet1.update_cell(23, i, '0/800.000')
                        if k == 7: k = 1
                        # устанавливаем знаечние 1-ой строки таблицы для текущей недели
                        sh.sheet1.update_cell(1, i, '{} ({})'.format(week[k],
                                                                     (today + timedelta(days=i - 1)).strftime('%d.%m')))
                        week_date[i] = sh.sheet1.cell(1, i)

                        if i < 21:
                            j = 2  # строка
                            while j < 22:
                                try:
                                    # ячейка текущей недели
                                    text_old = sh.sheet1.cell(j, i).value
                                    # ячейка будущей недели
                                    text_new = sh.sheet1.cell(j, i + 7).value

                                    if text_new != None:
                                        sh.sheet1.update_cell(j, i, text_new)
                                        sh.sheet1.update_cell(j, i + 7, '')
                                        j = j + 1

                                    elif text_old != None:
                                        sh.sheet1.update_cell(j, i, '')
                                        j = j + 1
                                    else:
                                        j += 1
                                except:
                                    time.sleep(1)
                        k = k + 1
                    break
                except:
                    time.sleep(2)

    else:
        bot.send_message(id, 'Таблица обновлена, изменения не требуются')

# основная логика работы DeckenBot`а
while True:
    try:
        # restart
        @bot.message_handler(command=['restart'])
        def restart(message):
            cursor.execute('SELECT * FROM admins WHERE admin_id = ?', (message.chat.id,))
            data = cursor.fetchall()
            if len(data) != 0:
                if datetime.today().isoweekday() == 1:
                    table_info(message.chat.id)
        # --------------------------

        # admin
        @bot.message_handler(commands=['admin'])
        def add_user_id(message):
            cursor.execute('SELECT * FROM admins WHERE admin_id = ?', (message.chat.id,))
            data = cursor.fetchall()
            if len(data) != 0:
                commands = ['Добавить специалиста', 'Удалить специалиста', 'Список всех специалистов',
                            'Добавить администратора', 'Отмена']
                key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                for comm in commands:
                    key.add(telebot.types.KeyboardButton(comm))

                bot.send_message(message.chat.id, 'Выберите одну из доступных функций', reply_markup=key)
                bot.register_next_step_handler(message, admin_handler)
            else:
                bot.send_message(message.chat.id, 'Нет прав администратора для доступа к данной команде')
        # --------------------------


        # start
        @bot.message_handler(commands=['start'])
        def start_message(message):
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (message.chat.id,))
            res = len(cursor.fetchall())

            if res != 0:
                bot.reply_to(message, "Приветствую, " + message.from_user.first_name)
                bot.send_message(message.chat.id, 'Для начала работы выберите команду из "Меню"')
            else:
                bot.send_message(message.chat.id, 'Привет, Красавчик!\n' +
                                 'Сейчас уточню у начальства, насколько ты крут и вернусь.\n' +
                                 'Подожди, пожалуйста, пару минут')
                bot.send_message(admin_id,
                                 f'Грибок пытается войти:\n{message.chat.id} + {message.from_user.first_name}')

                for i in range(30):
                    cursor.execute("SELECT * FROM users WHERE user_id = ?", (message.chat.id,))
                    res = len(cursor.fetchall())

                    if res != 0:
                        bot.send_message(message.chat.id,
                                         f'Да уж, {message.from_user.first_name}, ты действительно крутой перец!')
                        bot.send_message(message.chat.id,
                                         'Теперь ты можешь приступить к работе со Мной (лучшим и единственным ботом компании Decken)' +
                                         '\nДля начала работы выберите команду из "Меню"')
                        break
                    else:
                        time.sleep(5)
        # --------------------------

        # '/new_work'
        @bot.message_handler(commands=['new_work'])
        def send_welcome(message):
            cursor.execute("SELECT * FROM users WHERE user_id = {}".format(message.chat.id))
            res = len(cursor.fetchall())

            if res != 0:
                bot.send_message(message.chat.id, "Приветствую, " + message.from_user.first_name)

                bot.send_message(message.from_user.id, "Внесите номер договора")
                bot.register_next_step_handler(message, montage_number)

            else:
                bot.send_message(message.chat.id, 'Привет, Красавчик!\n' +
                                 'Сейчас уточню у начальства, насколько ты крут и вернусь.\n' +
                                 'Подожди, пожалуйста, пару минут')
                bot.send_message(admin_id,
                                 f'Грибок пытается войти:\n{message.chat.id} + {message.from_user.first_name}')
        # --------------------------

        bot.polling(none_stop=True)
    except:
        # Таймер на 5 секунд если Telegram разорвет соединение
        time.sleep(5)
