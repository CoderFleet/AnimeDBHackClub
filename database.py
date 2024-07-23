import sqlite3

def create_connection():
    conn = sqlite3.connect('anime_list.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            episodes INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_anime(title, genre, episodes, status):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO anime (title, genre, episodes, status)
        VALUES (?, ?, ?, ?)
    ''', (title, genre, episodes, status))
    conn.commit()
    conn.close()

def get_all_anime():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM anime')
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_anime(anime_id, title, genre, episodes, status):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE anime
        SET title = ?, genre = ?, episodes = ?, status = ?
        WHERE id = ?
    ''', (title, genre, episodes, status, anime_id))
    conn.commit()
    conn.close()

def delete_anime(anime_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM anime WHERE id = ?', (anime_id,))
    conn.commit()
    conn.close()

create_table()
