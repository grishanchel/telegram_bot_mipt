import os

import telebot
from telebot import types

from dotenv import load_dotenv
from db import (register_student_to_db, find_student_by_email, get_schedule_for_student,
                get_notifications_for_student, get_test_results_for_student, close_connection)
from chatbot import ChatBot

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

bot = telebot.TeleBot(API_TOKEN)
chat_bot = ChatBot()

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Регистрация', 'Вход')
    bot.send_message(message.chat.id, "Добро пожаловать в мфти телеграм бота. Пожалуйста, зарегистрируйтесь или войдите в существующий аккаунт", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Регистрация')
def register(message):
    msg = bot.send_message(message.chat.id, "Введите имя")
    bot.register_next_step_handler(msg, receive_first_name)

def receive_first_name(message):
    user_data['first_name'] = message.text
    msg = bot.send_message(message.chat.id, "Введите фамилию")
    bot.register_next_step_handler(msg, receive_last_name)

def receive_last_name(message):
    user_data['last_name'] = message.text
    msg = bot.send_message(message.chat.id, "Введите электронную почту")
    bot.register_next_step_handler(msg, receive_email)

def receive_email(message):
    user_data['email'] = message.text
    if find_student_by_email(user_data['email']):
        bot.send_message(message.chat.id, "Эта почта уже зарегистрирована")
        return start(message)
    register_student_to_db(user_data['first_name'], user_data['last_name'], user_data['email'])
    bot.send_message(message.chat.id, f"Спасибо за регистрацию, {user_data['first_name']} {user_data['last_name']}!")
    main_menu(message)

@bot.message_handler(func=lambda message: message.text == 'Вход')
def login(message):
    msg = bot.send_message(message.chat.id, "Введите электронную почту")
    bot.register_next_step_handler(msg, receive_login_email)

def receive_login_email(message):
    email = message.text
    student = find_student_by_email(email)
    if student:
        bot.send_message(message.chat.id, f"Добро пожаловать, {student[1]} {student[2]}!")
        main_menu(message)
    else:
        bot.send_message(message.chat.id, "Аккаунт не найден")
        start(message)

@bot.message_handler(commands=['menu'])
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Расписание', 'Уведомления', 'Задать вопрос', 'Результаты теста')
    bot.send_message(message.chat.id, "Main Menu:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Расписание')
def schedule(message):
    student_id = user_data.get('student_id')
    if student_id:
        schedule = get_schedule_for_student(student_id)
        if schedule:
            response = "Расписание\n"
            for item in schedule:
                response += f"{item[0]} - {item[1]}: {item[2]} ({item[3]})\n"
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "Расписание не найдено")
    else:
        bot.send_message(message.chat.id, "Сначала войдите в аккаунт")

@bot.message_handler(func=lambda message: message.text == 'Уведомления')
def notifications(message):
    student_id = user_data.get('student_id')
    if student_id:
        notifications = get_notifications_for_student(student_id)
        if notifications:
            response = "Уведомления\n"
            for item in notifications:
                response += f"{item[1]}: {item[0]}\n"
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "Уведомления не найдены")
    else:
        bot.send_message(message.chat.id, "Сначала войдите в аккаунт")

@bot.message_handler(func=lambda message: message.text == 'Задать вопрос')
def ask_question(message):
    bot.send_message(message.chat.id, "Напишите ваш вопрос")

@bot.message_handler(func=lambda message: message.text == 'Результаты теста')
def test_results(message):
    student_id = user_data.get('student_id')
    if student_id:
        results = get_test_results_for_student(student_id)
        if results:
            response = "Результаты теста\n"
            for item in results:
                response += f"{item[2]}: {item[0]} - {item[1]} баллы\n"
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "Результаты теста не найдены")
    else:
        bot.send_message(message.chat.id, "Сначала войдите в аккаунт")

bot.polling(none_stop=True, interval=0)

close_connection()
