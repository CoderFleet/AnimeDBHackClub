import database

def get_user_input(prompt, type_=str, min_=None, max_=None, range_=None):
    while True:
        user_input = input(prompt)
        try:
            user_input = type_(user_input)
        except ValueError:
            print(f"Please enter a valid {type_.__name__}.")
            continue
        if min_ is not None and user_input < min_:
            print(f"Please enter a value greater than {min_}.")
        elif max_ is not None and user_input > max_:
            print(f"Please enter a value less than {max_}.")
        elif range_ is not None and user_input not in range_:
            print(f"Please enter a value in {range_}.")
        else:
            return user_input

def print_anime_list(anime_list):
    if not anime_list:
        print("No anime found.")
        return
    print(f"{'ID':<5} {'Title':<30} {'Genres':<30} {'Episodes':<10} {'Status':<10}")
    print("="*85)
    for anime in anime_list:
        print(f"{anime[0]:<5} {anime[1]:<30} {anime[2]:<30} {anime[3]:<10} {anime[4]:<10}")

def register():
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    if database.register_user(username, password):
        print("User registered successfully!")
    else:
        print("Username already exists. Please try a different one.")

def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    if database.login_user(username, password):
        print("Login successful!")
        return True
    else:
        print("Invalid username or password. Please try again.")
        return False

def get_user_id(username):
    conn = database.create_connection()
    with conn:
        cursor = conn.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        return user[0] if user else None

def add_anime():
    title = input("Enter anime title: ")
    genres = input("Enter anime genres (comma separated): ").split(',')
    genres = [genre.strip() for genre in genres]
    episodes = get_user_input("Enter number of episodes: ", int, 1)
    status = input("Enter status (Watching/Completed/On Hold/Dropped): ")
    database.add_anime(title, episodes, status, genres)
    print("Anime added successfully!")

def update_anime():
    anime_id = get_user_input("Enter anime ID to update: ", int, 1)
    title = input("Enter new title: ")
    genres = input("Enter new genres (comma separated): ").split(',')
    genres = [genre.strip() for genre in genres]
    episodes = get_user_input("Enter new number of episodes: ", int, 1)
    status = input("Enter new status (Watching/Completed/On Hold/Dropped): ")
    database.update_anime(anime_id, title, episodes, status, genres)
    print("Anime updated successfully!")

def delete_anime():
    anime_id = get_user_input("Enter anime ID to delete: ", int, 1)
    database.delete_anime(anime_id)
    print("Anime deleted successfully!")

def search_anime_by_title():
    title = input("Enter anime title to search: ")
    anime_list = database.search_anime_by_title(title)
    print_anime_list(anime_list)

def filter_anime_by_genre():
    genre = input("Enter genre to filter by: ")
    anime_list = database.filter_anime_by_genre(genre)
    print_anime_list(anime_list)

def filter_anime_by_status():
    status = input("Enter status to filter by (Watching/Completed/On Hold/Dropped): ")
    anime_list = database.filter_anime_by_status(status)
    print_anime_list(anime_list)

def view_preferences(user_id):
    preferences = database.get_all_preferences(user_id)
    if not preferences:
        print("No preferences set.")
        return
    print("Current Preferences:")
    for key, value in preferences.items():
        print(f"{key}: {value}")

def update_preferences(user_id):
    print("1. Set Default Genre")
    print("2. Set Viewing Options")
    choice = get_user_input("Enter your choice: ", int, 1, 2)
    if choice == 1:
        genre = input("Enter your default genre: ")
        database.set_preference(user_id, 'default_genre', genre)
        print("Default genre updated!")
    elif choice == 2:
        option = input("Enter viewing option (e.g., List/Grid): ")
        database.set_preference(user_id, 'viewing_option', option)
        print("Viewing option updated!")

def main():
    print("Welcome to the Anime List Database")
    logged_in = False
    user_id = None
    while not logged_in:
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")
        choice = get_user_input("Enter your choice: ", int, 1, 3)
        if choice == 1:
            register()
        elif choice == 2:
            username = input("Enter your username: ")
            logged_in = login()
            if logged_in:
                user_id = get_user_id(username)
        elif choice == 3:
            return

    while True:
        print("\nMenu:")
        print("1. Add Anime")
        print("2. View All Anime")
        print("3. Update Anime")
        print("4. Delete Anime")
        print("5. Search Anime by Title")
        print("6. Filter Anime by Genre")
        print("7. Filter Anime by Status")
        print("8. Export to CSV")
        print("9. Backup Database")
        print("10. View Preferences")
        print("11. Update Preferences")
        print("12. Logout")
        choice = get_user_input("Enter your choice: ", int, 1, 12)

        if choice == 1:
            add_anime()
        elif choice == 2:
            anime_list = database.get_all_anime()
            print_anime_list(anime_list)
        elif choice == 3:
            update_anime()
        elif choice == 4:
            delete_anime()
        elif choice == 5:
            search_anime_by_title()
        elif choice == 6:
            filter_anime_by_genre()
        elif choice == 7:
            filter_anime_by_status()
        elif choice == 8:
            filename = input("Enter filename for export (default: anime_list.csv): ")
            if not filename:
                filename = 'anime_list.csv'
            database.export_to_csv(filename)
            print(f"Anime list exported to {filename}.")
        elif choice == 9:
            database.backup_database()
        elif choice == 10:
            if user_id:
                view_preferences(user_id)
        elif choice == 11:
            if user_id:
                update_preferences(user_id)
        elif choice == 12:
            print("Logged out successfully.")
            main()

if __name__ == "__main__":
    main()
