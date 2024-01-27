import sqlite3

def create_database():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    # SQLite doesn't let for date types thats why there is text date_done

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            date_done TEXT
        )
    ''')


    conn.commit()
    conn.close()

def sample_data():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    # Check if the table is empty
    cursor.execute('SELECT COUNT(*) FROM tasks')
    count = cursor.fetchone()[0]

    if count == 0:
        # Table is empty, insert sample tasks
        sample_tasks = [
            ('Zadanie 1', 'Przykładowy opis zadania 1', '2024-01-20'),
            ('Zadanie 2', 'Przykładowy opis zadania 2', '2024-01-21'),
            ('Zadanie 3', 'Przykładowy opis zadania 3', '2024-01-22'),
            ('Zadanie 4', 'Przykładowy opis zadania 4', '2024-01-23'),
            ('Zadanie 5', 'Przykładowy opis zadania 5', '2024-01-24'),
            ('Zadanie 6', 'Przykładowy opis zadania 6', '2024-01-20'),
            ('Zadanie 7', 'Przykładowy opis zadania 7', '2024-01-21'),
            ('Zadanie 8', 'Przykładowy opis zadania 8', '2024-01-22'),
            ('Zadanie 9', 'Przykładowy opis zadania 9', '2024-01-23'),
            ('Zadanie 10', 'Przykładowy opis zadania 10', '2024-01-24'),
        ]

        cursor.executemany('INSERT INTO tasks (title, description, date_done) VALUES (?, ?, ?)', sample_tasks)
        conn.commit()

    conn.close()