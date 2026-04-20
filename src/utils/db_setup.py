import sqlite3
import os

def init_db():
    if not os.path.exists('data'):
        os.makedirs('data')

    db_connection = sqlite3.connect('data/edumind.db')
    cursor = db_connection.cursor()

    ## Table: class
    cursor.execute('''CREATE TABLE IF NOT EXISTS classes (class_id TEXT PRIMARY KEY,class_name TEXT)''')

    ## Table: students
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students(
       student_id INTEGER PRIMARY KEY,
       first_name TEXT,
       last_name TEXT,
       class_id TEXT,
       parent_email TEXT,
       parent_phone TEXT,
       FOREIGN KEY (class_id) REFERENCES classes (class_id)
       )
   ''')

    ## Table: grades
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS grades (
        grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        grade INTEGER,
        date TEXT,
        FOREIGN KEY (student_id) REFERENCES students (student_id)
    )
    ''')

    db_connection.commit()
    db_connection.close()
    print('Database created successfully')

if __name__ == '__main__':
    init_db()