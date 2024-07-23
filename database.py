import sqlite3

def create_connection():
    return sqlite3.connect('anime_list.db')

def create_table():
    conn = create_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS anime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                genre TEXT NOT NULL,
                episodes INTEGER NOT NULL,
                status TEXT NOT NULL
            )
        ''')

def add_anime(title, genre, episodes, status):
    conn = create_connection()
    with conn:
        conn.execute('''
            INSERT INTO anime (title, genre, episodes, status)
            VALUES (?, ?, ?, ?)
        ''', (title, genre, episodes, status))

def get_all_anime():
    conn = create_connection()
    with conn:
        return conn.execute('SELECT * FROM anime').fetchall()

def update_anime(anime_id, title, genre, episodes, status):
    conn = create_connection()
    with conn:
        conn.execute('''
            UPDATE anime
            SET title = ?, genre = ?, episodes = ?, status = ?
            WHERE id = ?
        ''', (title, genre, episodes, status, anime_id))

def delete_anime(anime_id):
    conn = create_connection()
    with conn:
        conn.execute('DELETE FROM anime WHERE id = ?', (anime_id,))

def search_anime_by_title(title):
    conn = create_connection()
    with conn:
        return conn.execute('SELECT * FROM anime WHERE title LIKE ?', ('%' + title + '%',)).fetchall()

def filter_anime_by_genre(genre):
    conn = create_connection()
    with conn:
        return conn.execute('SELECT * FROM anime WHERE genre = ?', (genre,)).fetchall()

def filter_anime_by_status(status):
    conn = create_connection()
    with conn:
        return conn.execute('SELECT * FROM anime WHERE status = ?', (status,)).fetchall()

create_table()
