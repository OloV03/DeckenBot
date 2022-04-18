from datetime import datetime
import random
import time
import telebot
from config import montage_info, bot, sh


# запись номера договора
def montage_number(msg):
    montage_info[msg.chat.id] = {}
    montage_info[msg.chat.id]['number'] = msg.text
    bot.send_message(msg.chat.id, 'Записано, #{0}'.format(msg.text))
    bot.send_message(msg.chat.id, "Введите цену договора (без точек и пробелов)")
    bot.register_next_step_handler(msg, montage_price)


# сумма договора
def montage_price(msg):
    # есть ли доп позиции?
    montage_info[msg.chat.id]['inoe'] = False
    montage_info[msg.chat.id]['dop_ques'] = False

    if msg.text.isdigit():
        price = 0
        if int(msg.text) % 40000 != 0:
            price = int(msg.text) // 40000 + 1
        else:
            price = int(msg.text) // 40000
        montage_info[msg.chat.id]['price'] = msg.text
        montage_info[msg.chat.id]['days'] = price

        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('Без скидки'))
        keyboard.add(telebot.types.KeyboardButton('До 15%'))
        keyboard.add(telebot.types.KeyboardButton('15-20%'))
        keyboard.add(telebot.types.KeyboardButton('Более 20%'))
        bot.send_message(msg.chat.id, "Какая скидка предоставлена?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, sale)

    else:
        bot.send_message(msg.chat.id, "Кажется ты написал что-то не то. Укажите верное значение цены")
        bot.register_next_step_handler(msg, montage_price)


# скидка по договору
def sale(msg):
    values = ['Без скидки', 'До 15%', '15-20%', 'Более 20%']
    if msg.text in values:
        montage_info[msg.chat.id]['price'] += "\nСкидка: " + msg.text

    else:
        bot.send_message(msg.chat.id, 'Неверный ввод, повторите пожалуйста')
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('Без скидки'))
        keyboard.add(telebot.types.KeyboardButton('До 15%'))
        keyboard.add(telebot.types.KeyboardButton('15-20%'))
        keyboard.add(telebot.types.KeyboardButton('Более 20%'))
        bot.send_message(msg.chat.id, "Какая скидка предоставлена?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, sale)

    bot.send_message(msg.chat.id, "Размер внесенно аванса: ")
    bot.register_next_step_handler(msg, avance)


# аванс
def avance(msg):
    if msg.text.isdigit():
        montage_info[msg.chat.id]['price'] += "\nАванс: " + msg.text
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('Наличными'))
        keyboard.add(telebot.types.KeyboardButton('Безналичными'))
        bot.send_message(msg.chat.id, "Как внесен аванс?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, type_avance)
    else:
        bot.send_message(msg.chat.id, 'Неверный ввод, повторите пожалуйста')
        bot.send_message(msg.chat.id, "Размер внесенно аванса (без точек/запятых): ")
        bot.register_next_step_handler(msg, avance)


# как внесен аванс (нал/безнал)
def type_avance(msg):
    values = ['Наличными', 'Безналичными']
    if msg.text in values:
        montage_info[msg.chat.id]['price'] += " (" + msg.text + ")"

    else:
        bot.send_message(msg.chat.id, 'Неверный ввод, повторите пожалуйста')

        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('Наличными'))
        keyboard.add(telebot.types.KeyboardButton('Безналичными'))
        bot.send_message(msg.chat.id, "Как внесен аванс?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, type_avance)

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('Да'))
    keyboard.add(telebot.types.KeyboardButton('Нет'))
    bot.send_message(msg.chat.id, "Есть ли какие-то доп. позиции?", reply_markup=keyboard)
    montage_info[msg.chat.id]['dop_pos'] = ""
    bot.register_next_step_handler(msg, dop_positions)


# внесение доп позиций
def dop_positions(msg):
    variants = ['Фотопечать', 'Конструкции', 'Парящий',
                'Световые линии', 'Ткань', 'Теневой профиль',
                'Цветное полотно/вставка', 'Лента RGB+White']

    if msg.text == "Нет" or msg.text == "Далее -->":
        # выбор возможной высотности
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('До 3 метров'))
        keyboard.add(telebot.types.KeyboardButton('Более 3 метров'))
        bot.send_message(msg.chat.id, "Какова высота потолка?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, visotnost)

    else:
        montage_info[msg.chat.id]['inoe'] = True

        if msg.text in ['Фотопечать', 'Конструкции']:
            bot.send_message(msg.chat.id, 'На изготовление требуется 5 рабочих дней!')

        if msg.text in ['Парящий', 'Теневой профиль']:
            var = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            var.add(telebot.types.KeyboardButton('Стеновой'))
            var.add(telebot.types.KeyboardButton('Потолочный'))
            montage_info[msg.chat.id]['dop_pos'] += msg.text + ' ('
            montage_info[msg.chat.id]['dop_ques'] = True
            bot.send_message(msg.chat.id, 'Уточните, какой именно профиль?', reply_markup=var)
            bot.register_next_step_handler(msg, dop_positions)
            return

        if msg.text != "Да" and montage_info[msg.chat.id]['dop_ques'] == False:
            montage_info[msg.chat.id]['dop_pos'] += msg.text + '\n'
        elif msg.text != "Да" and montage_info[msg.chat.id]['dop_ques']:
            montage_info[msg.chat.id]['dop_pos'] += msg.text + ')\n'
            montage_info[msg.chat.id]['dop_ques'] = False

        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('Далее -->'))
        for i in variants:
            keyboard.add(telebot.types.KeyboardButton(i))

        bot.send_message(msg.chat.id, "Выберете необходимые или напишите название самостоятельно:",
                         reply_markup=keyboard)
        bot.register_next_step_handler(msg, dop_positions)


# Выстоность потолка
def visotnost(msg):
    check = False
    montage_info[msg.chat.id]['h'] = ''
    if msg.text == "До 3 метров":
        check = True
        pass
    elif msg.text == "Более 3 метров":
        check = True
        montage_info[msg.chat.id]['h'] += "\nВысотность выше 3 метров"
    else:
        # выбор возможной высотности
        bot.send_message(msg.chat.id, 'Ввыдены некорректные данные, повторите ввод')
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('До 3 метров'))
        keyboard.add(telebot.types.KeyboardButton('Более 3 метров'))
        bot.send_message(msg.chat.id, "Какова высота потолка?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, visotnost)

    if check:
        # выбор этапности монтажа
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('Монтаж полностью'))
        keyboard.add(telebot.types.KeyboardButton('Первый этап (багет)'))
        keyboard.add(telebot.types.KeyboardButton('Второй этап (полотна)'))
        bot.send_message(msg.chat.id, "Какова этапность монтажа?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, stages_montage)


# Этапность монтажа
def stages_montage(msg):
    check = False
    if msg.text == 'Монтаж полностью':
        montage_info[msg.chat.id]['stage'] = '\nЭтапность: Полный монтаж'
        check = True
    elif msg.text == 'Первый этап (багет)':
        montage_info[msg.chat.id]['stage'] = '\nЭтапность: 1 этап (багет)'
        check = True
    elif msg.text == 'Второй этап (полотна)':
        montage_info[msg.chat.id]['stage'] = '\nЭтапность: 2 этап (полотна)'
        check = True
    else:
        bot.send_message(msg.chat.id, "Неверный ввод")
        bot.register_next_step_handler(msg, stages_montage)

    if check:
        # Поиск свободных дней
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('Текущая неделя'))
        keyboard.add(telebot.types.KeyboardButton('Следующая неделя'))
        keyboard.add(telebot.types.KeyboardButton('Через 2 недели'))
        keyboard.add(telebot.types.KeyboardButton('Через 3 недели'))
        keyboard.add(telebot.types.KeyboardButton('Иное'))
        bot.send_message(msg.chat.id, "Когда планируется монтаж?", reply_markup=keyboard)
        bot.register_next_step_handler(msg, montage_date_itog)


# выбор даты монтажа
def montage_date_itog(msg):
    if msg.text == 'Текущая неделя':
        bot.send_message(msg.chat.id, "Поиск свободных дней...")
        markup = telebot.types.InlineKeyboardMarkup()
        time.sleep(random.randrange(1, 2))
        today = datetime.today().isoweekday() + 1
        for i in range(today, 7):
            if int(sh.sheet1.cell(22, i).value) > 0:
                markup.add(telebot.types.InlineKeyboardButton(sh.sheet1.cell(1, i).value, callback_data=i))
        bot.send_message(msg.chat.id, "А вот и они!\nВыберите подходящий", reply_markup=markup)
    elif msg.text == 'Следующая неделя':
        bot.send_message(msg.chat.id, "Поиск свободных дней...")
        markup = telebot.types.InlineKeyboardMarkup()
        time.sleep(random.randrange(1, 2))
        for i in range(8, 14):
            if int(sh.sheet1.cell(22, i).value) > 0:
                markup.add(telebot.types.InlineKeyboardButton(sh.sheet1.cell(1, i).value, callback_data=i))
        bot.send_message(msg.chat.id, "А вот и они!\nВыберите подходящий", reply_markup=markup)
    elif msg.text == 'Через 2 недели':
        bot.send_message(msg.chat.id, "Поиск свободных дней...")
        markup = telebot.types.InlineKeyboardMarkup()
        time.sleep(random.randrange(1, 2))
        for i in range(15, 21):
            if int(sh.sheet1.cell(22, i).value) > 0:
                markup.add(telebot.types.InlineKeyboardButton(sh.sheet1.cell(1, i).value, callback_data=i))
        bot.send_message(msg.chat.id, "А вот и они!\nВыберите подходящий", reply_markup=markup)
    elif msg.text == 'Через 3 недели':
        bot.send_message(msg.chat.id, "Поиск свободных дней...")
        markup = telebot.types.InlineKeyboardMarkup()
        time.sleep(random.randrange(1, 2))
        for i in range(22, 28):
            if int(sh.sheet1.cell(22, i).value) > 0:
                markup.add(telebot.types.InlineKeyboardButton(sh.sheet1.cell(1, i).value, callback_data=i))
        bot.send_message(msg.chat.id, "А вот и они!\nВыберите подходящий", reply_markup=markup)
    elif msg.text == 'Иное':
        bot.send_message(msg.chat.id, "Укажите желаемую дату\nФормат: дд.мм")
        bot.register_next_step_handler(msg, inoe_date)
    else:
        bot.send_message(msg.chat.id, "Кажется ты написал что-то не то. Выбери один из предложенных вариантов.")
        bot.register_next_step_handler(msg, montage_date_itog)


# внесение монтажа в графу "Иное"
def inoe_date(msg):
    bot.send_message(msg.chat.id, 'Проверка...')
    montage_info[msg.chat.id]['дата'] = msg.text
    montage_info[msg.chat.id]['last date'] = msg.text
    check_data(msg, 29, msg.chat.id)


# обработка кнопок
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Проверка...',
                          reply_markup=None)
    check_data(call.message, int(call.data), call.message.chat.id)


# проверка внесения
def check_data(message, col, id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(telebot.types.KeyboardButton('Все верно'))
    markup.add(telebot.types.KeyboardButton('Внести заново'))
    if col != 29:
        montage_info[id]['last date'] = sh.sheet1.cell(1, col).value

    text_montage = f'№: {montage_info[id]["number"]}\n' \
                   f'Цена: {montage_info[id]["price"]}' \
                   f'{montage_info[id]["stage"]}' \
                   f'{montage_info[id]["h"]}\n' \
                   f'Начало монтажа: {montage_info[id]["last date"]}'

    if montage_info[id]['inoe']:
        text_montage += f'\nДоп. позиции:\n{montage_info[message.chat.id]["dop_pos"]}'
    bot.send_message(id, f'Верны ли данные для внесения:\n{text_montage}', reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: check_data_res(msg, col, id))

def check_data_res(message, col, id):
    if message.text == 'Все верно':

        text = date_montages(col, id)
        bot.send_message(id, text)
    else:
        bot.send_message(id, 'Внесите данные снова, выбрав команду из "Меню"')

# внесение монтажа в таблицу
def date_montages(col, id):
    x = 0
    while x < 1:
        try:
            text_montage = ""
            if montage_info[id]['days'] == 1 and col != 29:
                value = sh.sheet1.col_values(col)
                text_for_sheet_cell = ""
                if montage_info[id]['inoe']:
                    text_for_sheet_cell += "$ $ $ $ $ ДОПЫ $ $ $ $ $\n"

                text_for_sheet_cell += f"№: {montage_info[id]['number']}\n" \
                                       f"Цена: {montage_info[id]['price']}" \
                                       f'{montage_info[id]["stage"]}' \
                                       f"{montage_info[id]['h']}"

                if montage_info[id]['inoe']:
                    text_for_sheet_cell += f'\nДоп. позиции:\n{montage_info[id]["dop_pos"]}'
                t = value.index('') + 1
                sh.sheet1.update_cell(t, col, text_for_sheet_cell)

                # получаем сумму всех договоров
                text = sh.sheet1.cell(23, col).value
                print(str(montage_info[id]['price']).split("\n")[0])
                text_for_cell = int((montage_info[id]['price']).split("\n")[0]) + int(text[:-8])
                sh.sheet1.update_cell(23, col, f'{text_for_cell}/800.000')
                text_montage = text_for_sheet_cell

                montage_info[id]['last date'] = sh.sheet1.cell(1, col).value
            elif col != 29:
                if (28 - col) >= montage_info[id]['days']:
                    # переменная для перебора свободных дней
                    colums = col
                    days = montage_info[id]['days']
                    days_mon = 1
                    montage_info[id]['last date'] = sh.sheet1.cell(1, col).value
                    for i in range(1, days + 1):
                        while True:
                            if colums != 7 and colums != 14 and colums != 21 and colums != 28:
                                if int(sh.sheet1.cell(22, colums).value) > 0:
                                    value = sh.sheet1.col_values(colums)

                                    text_for_sheet_cell = ""
                                    if montage_info[id]['inoe']:
                                        text_for_sheet_cell += "$ $ $ $ $ ДОПЫ $ $ $ $ $\n"
                                    text_for_sheet_cell += f"№: {montage_info[id]['number']}\n" \
                                                           f"Цена: {montage_info[id]['price']}" \
                                                           f'{montage_info[id]["stage"]}' \
                                                           f"{montage_info[id]['h']}\n" \
                                                           f"День монтажа: {str(days_mon)}"
                                    if montage_info[id]['inoe']:
                                        text_for_sheet_cell += f'\nДоп. позиции:\n{montage_info[id]["dop_pos"]}'

                                    t = value.index('') + 1
                                    sh.sheet1.update_cell(t, colums, text_for_sheet_cell)

                                    # вносим сумму всех договоров
                                    if (i != days):
                                        text = sh.sheet1.cell(23, colums).value
                                        text_for_cell = 40000 + int(text[:-8])
                                        sh.sheet1.update_cell(23, colums, f'{text_for_cell}/800.000')
                                    else:
                                        text = sh.sheet1.cell(23, colums).value
                                        text_for_cell = (int(montage_info[id]['price']) - (
                                                40000 * (i - 1))) + int(text[:-8])
                                        sh.sheet1.update_cell(23, colums, f'{text_for_cell}/800.000')

                                    colums = colums + 1
                                    days_mon = days_mon + 1
                                    if (i != 1):
                                        montage_info[id]['last date'] += ', ' + sh.sheet1.cell(1, colums - 1).value
                                    break
                                else:
                                    colums = colums + 1
                            else:
                                colums = colums + 1
                    text_montage = '№: {0}\nЦена: {1}'.format(montage_info[id]['number'],
                                                              montage_info[id]['price'])
                    if montage_info[id]['inoe']:
                        text_montage += f'\nДоп. позиции:\n{montage_info[id]["dop_pos"]}'
                else:
                    # вносим монтаж в категорию "Иное", однако в сообщении пользователю говорим точные даты (монтаж просто "не вместился в следующую неделю")
                    value = sh.sheet1.col_values(29)
                    x = value.index('#') + 1
                    if sh.sheet1.cell(x + 1, 15).value == '' or '#':
                        sh.sheet1.update_cell(x + 1, 29, '#')
                    montage_info[id]['дата'] = sh.sheet1.cell(1, col).value

                    text_montage = ""
                    if montage_info[id]['inoe']:
                        text_for_sheet_cell += "$ $ $ $ $ ДОПЫ $ $ $ $ $\n"

                    text_montage += f"Дата: {montage_info[id]['дата']}\n" \
                                    f"№: {montage_info[id]['number']}\n" \
                                    f"Цена: {montage_info[id]['price']}" \
                                    f'{montage_info[id]["stage"]}' \
                                    f"{montage_info[id]['h']}\n" \
                                    f"Необходимо дней для монтажа: {montage_info[id]['days']}"
                    if montage_info[id]['inoe']:
                        text_montage += f"\nДоп. позиции:\n{montage_info[id]['dop_pos']}"
                    sh.sheet1.update_cell(x, 29, text_montage)

                    last_date = (datetime.today() + datetime.timedelta(days=(13 - datetime.today().isoweekday())))
                    # получаем крайнюю дату следующей недели

                    week = {1: 'Пн', 2: 'Вт', 3: 'Ср', 4: 'Чт', 5: 'Пн', 6: 'Сб'}
                    montage_info[id]['last date'] = sh.sheet1.cell(1, col).value
                    # сначала внесем даты, которые есть в таблице
                    for i in range(col + 1, 14):
                        montage_info[id]['last date'] += ', ' + sh.sheet1.cell(1, i).value
                    # теперь вносим даты, "не вместившиеся" в таблицу
                    x = montage_info[id]['days'] - (14 - col)
                    time.sleep(1.5)
                    for i in range(1, x + 1):
                        montage_info[id]['last date'] += ', ' + '{} ({})'.format(week[i], (
                                last_date + datetime.timedelta(days=i + 1)).strftime('%d.%m'))

                    text_montage = f"№: {montage_info[id]['number']}\n" \
                                   f"Цена: {montage_info[id]['price']}\n"
                    if montage_info[id]['inoe']:
                        text_montage += f"\nДоп. позиции:\n{montage_info[id]['dop_pos']}"
            else:
                value = sh.sheet1.col_values(col)
                x = value.index('#') + 1
                if sh.sheet1.cell(x + 1, col).value == '' or '#':
                    sh.sheet1.update_cell(x + 1, col, '#')

                text_montage = ""
                if montage_info[id]['inoe']:
                    text_for_sheet_cell += "$ $ $ $ $ ДОПЫ $ $ $ $ $\n"

                text_montage += f"Дата: {montage_info[id]['дата']}\n" \
                                f"№: {montage_info[id]['number']}\n" \
                                f'{montage_info[id]["stage"]}' \
                                f"Цена: {montage_info[id]['price']}" \
                                f"{montage_info[id]['h']}\n" \
                                f"Необходимо дней для монтажа: {montage_info[id]['days']}"

                if montage_info[id]['inoe']:
                    text_montage += f"\nДоп. позиции:\n{montage_info[id]['dop_pos']}"

                sh.sheet1.update_cell(x, col, text_montage)

            if montage_info[id]['days'] == 1:
                print(5)
                text = f"Внесено\n{text_montage}\nДень начала монтажа: {montage_info[id]['last date']}"
            else:
                text = f"Внесено\n{text_montage}\nДаты монтажа: {montage_info[id]['last date']}"
            x = 2
            return text
        except:
            time.sleep(1)
