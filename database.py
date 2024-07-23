import sqlite3

def create_connection():
    return sqlite3.connect('anime_list.db')

def create_table():
    conn = create_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS anime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                episodes INTEGER NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS genre (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS anime_genre (
                anime_id INTEGER,
                genre_id INTEGER,
                FOREIGN KEY (anime_id) REFERENCES anime (id),
                FOREIGN KEY (genre_id) REFERENCES genre (id),
                PRIMARY KEY (anime_id, genre_id)
            )
        ''')

def register_user(username, password):
    conn = create_connection()
    with conn:
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            return True
        except sqlite3.IntegrityError:
            return False

def login_user(username, password):
    conn = create_connection()
    with conn:
        cursor = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        return user is not None

def add_genre(name):
    conn = create_connection()
    with conn:
        conn.execute('INSERT INTO genre (name) VALUES (?)', (name,))

def get_genre_id(name):
    conn = create_connection()
    with conn:
        cursor = conn.execute('SELECT id FROM genre WHERE name = ?', (name,))
        genre = cursor.fetchone()
        if genre:
            return genre[0]
        else:
            return None

def add_anime(title, episodes, status, genres):
    conn = create_connection()
    with conn:
        cursor = conn.execute('INSERT INTO anime (title, episodes, status) VALUES (?, ?, ?)', (title, episodes, status))
        anime_id = cursor.lastrowid
        for genre in genres:
            genre_id = get_genre_id(genre)
            if genre_id is None:
                add_genre(genre)
                genre_id = get_genre_id(genre)
            conn.execute('INSERT INTO anime_genre (anime_id, genre_id) VALUES (?, ?)', (anime_id, genre_id))

def get_all_anime():
    conn = create_connection()
    with conn:
        cursor = conn.execute('''
            SELECT anime.id, anime.title, GROUP_CONCAT(genre.name), anime.episodes, anime.status
            FROM anime
            LEFT JOIN anime_genre ON anime.id = anime_genre.anime_id
            LEFT JOIN genre ON anime_genre.genre_id = genre.id
            GROUP BY anime.id
        ''')
        return cursor.fetchall()

def update_anime(anime_id, title, episodes, status, genres):
    conn = create_connection()
    with conn:
        conn.execute('UPDATE anime SET title = ?, episodes = ?, status = ? WHERE id = ?', (title, episodes, status, anime_id))
        conn.execute('DELETE FROM anime_genre WHERE anime_id = ?', (anime_id,))
        for genre in genres:
            genre_id = get_genre_id(genre)
            if genre_id is None:
                add_genre(genre)
                genre_id = get_genre_id(genre)
            conn.execute('INSERT INTO anime_genre (anime_id, genre_id) VALUES (?, ?)', (anime_id, genre_id))

def delete_anime(anime_id):
    conn = create_connection()
    with conn:
        conn.execute('DELETE FROM anime WHERE id = ?', (anime_id,))
        conn.execute('DELETE FROM anime_genre WHERE anime_id = ?', (anime_id,))

def search_anime_by_title(title):
    conn = create_connection()
    with conn:
        cursor = conn.execute('''
            SELECT anime.id, anime.title, GROUP_CONCAT(genre.name), anime.episodes, anime.status
            FROM anime
            LEFT JOIN anime_genre ON anime.id = anime_genre.anime_id
            LEFT JOIN genre ON anime_genre.genre_id = genre.id
            WHERE anime.title LIKE ?
            GROUP BY anime.id
        ''', ('%' + title + '%',))
        return cursor.fetchall()

def filter_anime_by_genre(genre):
    conn = create_connection()
    with conn:
        cursor = conn.execute('''
            SELECT anime.id, anime.title, GROUP_CONCAT(genre.name), anime.episodes, anime.status
            FROM anime
            LEFT JOIN anime_genre ON anime.id = anime_genre.anime_id
            LEFT JOIN genre ON anime_genre.genre_id = genre.id
            WHERE genre.name = ?
            GROUP BY anime.id
        ''', (genre,))
        return cursor.fetchall()

def filter_anime_by_status(status):
    conn = create_connection()
    with conn:
        cursor = conn.execute('''
            SELECT anime.id, anime.title, GROUP_CONCAT(genre.name), anime.episodes, anime.status
            FROM anime
            LEFT JOIN anime_genre ON anime.id = anime_genre.anime_id
            LEFT JOIN genre ON anime_genre.genre_id = genre.id
            WHERE anime.status = ?
            GROUP BY anime.id
        ''', (status,))
        return cursor.fetchall()

create_table()
