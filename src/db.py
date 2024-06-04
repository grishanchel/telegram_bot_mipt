import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

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

cursor.execute('''
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    score INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS schedule (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id),
    lesson_id INTEGER REFERENCES lessons(id),
    start_time TIMESTAMP,
    end_time TIMESTAMP
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

def close_connection():
    cursor.close()
    conn.close()
