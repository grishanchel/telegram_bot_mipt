import psycopg2
import telebot
from telebot import types
import os
from dotenv import load_dotenv

API_TOKEN = os.getenv('API_TOKEN')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

bot = telebot.TeleBot(API_TOKEN)

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cursor = conn.cursor()

class Student:
    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.courses = []

    def enroll_course(self, course):
        self.courses.append(course)

    def drop_course(self, course):
        self.courses.remove(course)

class Teacher:
    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.courses = []

    def create_course(self, course_name):
        course = Course(course_name, self)
        self.courses.append(course)
        return course

    def add_lesson(self, course, lesson):
        course.add_lesson(lesson)

class Course:
    def __init__(self, name, teacher):
        self.name = name
        self.teacher = teacher
        self.lessons = []

    def add_lesson(self, lesson):
        self.lessons.append(lesson)

    def remove_lesson(self, lesson):
        self.lessons.remove(lesson)

class Lesson:
    def __init__(self, title, content):
        self.title = title
        self.content = content

    def update_content(self, new_content):
        self.content = new_content

class ChatBot:
    def __init__(self):
        self.students = []
        self.teachers = []

    def register_student(self, student):
        self.students.append(student)

    def register_teacher(self, teacher):
        self.teachers.append(teacher)

    def find_student_by_email(self, email):
        for student in self.students:
            if student.email == email:
                return student
        return None

chat_bot = ChatBot()

user_data = {}

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    teacher_id INTEGER REFERENCES teachers(id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    content TEXT,
    course_id INTEGER REFERENCES courses(id)
);
''')

conn.commit()

def register_student_to_db(first_name, last_name, email):
    cursor.execute('INSERT INTO students (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id', (first_name, last_name, email))
    conn.commit()
    return cursor.fetchone()[0]

def find_student_by_email(email):
    cursor.execute('SELECT * FROM students WHERE email=%s', (email,))
    return cursor.fetchone()

def get_schedule_for_student(student_id):
    cursor.execute('''
        SELECT s.start_time, s.end_time, l.title, c.name
        FROM schedule s
        JOIN lessons l ON s.lesson_id = l.id
        JOIN courses c ON s.course_id = c.id
        JOIN students st ON st.id = %s
        WHERE st.id = %s;
    ''', (student_id, student_id))
    return cursor.fetchall()

def get_notifications_for_student(student_id):
    cursor.execute('SELECT message, timestamp FROM notifications WHERE student_id=%s', (student_id,))
    return cursor.fetchall()

def get_test_results_for_student(student_id):
    cursor.execute('''
        SELECT c.name, tr.score, tr.timestamp
        FROM test_results tr
        JOIN courses c ON tr.course_id = c.id
        WHERE tr.student_id = %s;
    ''', (student_id,))
    return cursor.fetchall()

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

cursor.close()
conn.close()


