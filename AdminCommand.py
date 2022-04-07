import telebot
from config import bot, cursor, conn

# обработка команд "админа"
def admin_handler(m):
    if m.text == 'Отмена':
        bot.send_message(m.chat.id, 'Команда отменена. Выберите команду из "Меню"', reply_markup=None)
    elif m.text == 'Добавить специалиста':
        add_user(m)
    elif m.text == 'Удалить специалиста':
        del_user(m)
    elif m.text == 'Список всех специалистов':
        all_users(m)
    elif m.text == 'Добавить администратора':
        add_admin(m)

# функция добавления данных в таблицу 'users' БД
def db_table_val(user_id: int, user_name: str, user_surname: str, user_number: str):
    cursor.execute('INSERT INTO users (user_id, user_name, user_surname, user_number) VALUES (?,?,?,?)',
                   (user_id, user_name, user_surname, user_number))
    conn.commit()


# добавление админов в таблицу 'admins'
def db_admins(admin_id: int, admin_name: str):
    cursor.execute('INSERT INTO admins (admin_id, admin_name) VALUES (?,?)', (admin_id, admin_name))
    conn.commit()

# добавление пользователя
def add_user(message):
    admin_info = {}
    bot.send_message(message.chat.id, 'Введите ID пользователя', reply_markup=None)
    bot.register_next_step_handler(message, lambda msg: add_user_name(msg, admin_info))

def add_user_name(message, admin_info):
    admin_info['id'] = int(message.text)
    bot.send_message(message.chat.id, 'Укажите имя специалиста')
    bot.register_next_step_handler(message, lambda msg: add_user_surname(msg, admin_info))

def add_user_surname(message, admin_info):
    admin_info['name'] = message.text
    bot.send_message(message.chat.id, 'Укажите фамилию специалиста')
    bot.register_next_step_handler(message, lambda msg: add_user_number(msg, admin_info))

def add_user_number(message, admin_info):
    admin_info['surname'] = message.text
    bot.send_message(message.chat.id, 'Укажите номер специалиста')
    bot.register_next_step_handler(message, lambda msg: add_user_itog(msg, admin_info))

def add_user_itog(message, admin_info):
    admin_info['number'] = message.text
    bot.send_message(message.chat.id, 'Данные внесены.\nМожно приступить к работе!')
    db_table_val(admin_info['id'], admin_info['name'], admin_info['surname'], admin_info['number'])
# -----------------------


# удаление пользователя
def del_user(message):
    bot.send_message(message.chat.id, 'Введите номер специалиста', reply_markup=None)
    bot.register_next_step_handler(message, del_user_data)

def del_user_data(message):
    if message.text.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Операция отменена')
    else:
        cursor.execute('SELECT * FROM users WHERE user_number = ?', (message.text,))
        data1 = cursor.fetchall()
        if len(data1) != 0:
            data = data1[0]
            text = f'Имя специалиста: {data[2]} {data[3]}\nНомер: {data[4]}'
            key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            key.add(telebot.types.KeyboardButton('Да'))
            key.add(telebot.types.KeyboardButton('Нет'))
            bot.send_message(message.chat.id, f'{text}')
            bot.send_message(message.chat.id, 'Удалить данного перчика?', reply_markup=key)
            bot.register_next_step_handler(message, lambda m: del_user_res(m, data))
        elif len(data1) == 0:
            bot.send_message(message.chat.id, 'Данный пользователь не найден\nВведите корректный номер')
            bot.send_message(message.chat.id, 'Для отмены операции введите "Отмена"')
            bot.register_next_step_handler(message, del_user_data)

def del_user_res(message, data):
    if message.text == 'Да':
        cursor.execute(f'DELETE FROM users WHERE user_id = {data[1]}')
        conn.commit()
        bot.send_message(message.chat.id, 'Специалист удален из базы данных (так ему и надо)')
    elif message.text == 'Нет':
        bot.send_message(message.chat.id, 'Ладно, ладно, пускай работает (пока что)')
    else:
        bot.send_message(message.chat.id, 'Такой команды нет, извините')
# ----------------------


# список всех пользователей
def all_users(message):
    cursor.execute('SELECT * FROM users')
    data = cursor.fetchall()
    text = ''
    for var in data:
        text += f'Специалист: {var[2]} {var[3]} (номер: {var[4]})\n\n'
    bot.send_message(message.chat.id, text, reply_markup=None)
# --------------------------


# добавление администратора
def add_admin(message):
    bot.send_message(message.chat.id, 'Введите номер пользователя', reply_markup=None)
    bot.register_next_step_handler(message, add_admin_data)

def add_admin_data(message):
    if message.text.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Операция отменена')
    else:
        cursor.execute('SELECT * FROM users WHERE user_number = ?', (message.text,))
        data1 = cursor.fetchall()
        if len(data1) != 0:
            data = data1[0]
            text = f'Имя специалиста: {data[2]} {data[3]}\nНомер: {data[4]}'
            key = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            key.add(telebot.types.KeyboardButton('Да'))
            key.add(telebot.types.KeyboardButton('Нет'))
            bot.send_message(message.chat.id, f'{text}')
            bot.send_message(message.chat.id, 'Сделать данного пользователя администратором?', reply_markup=key)
            bot.register_next_step_handler(message, lambda m: add_admin_res(m, data))
        elif len(data1) == 0:
            bot.send_message(message.chat.id, 'Данный пользователь не найден\nВведите корректный номер')
            bot.send_message(message.chat.id, 'Для отмены операции введите "Отмена"')
            bot.register_next_step_handler(message, add_admin_data)

def add_admin_res(message, data):
    if message.text == 'Да':
        db_admins(data[1], data[2])
        bot.send_message(message.chat.id, 'Теперь он наделен властью!')
    elif message.text == 'Нет':
        bot.send_message(message.chat.id, 'Он еще не дослужился до такого чина!')
# --------------------------