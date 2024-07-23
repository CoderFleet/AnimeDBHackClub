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
    for anime in anime_list:
        print(f"ID: {anime[0]}, Title: {anime[1]}, Genres: {anime[2]}, Episodes: {anime[3]}, Status: {anime[4]}")

def register():
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    if database.register_user(username, password):
        print("User registered successfully!")
    else:
        print("Username already exists.")

def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    if database.login_user(username, password):
        print("Login successful!")
        return True
    else:
        print("Invalid username or password.")
        return False

def main():
    print("Welcome to the Anime List Database")
    logged_in = False
    while not logged_in:
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")
        choice = get_user_input("Enter your choice: ", int, 1, 3)
        if choice == 1:
            register()
        elif choice == 2:
            logged_in = login()
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
        print("8. Logout")
        choice = get_user_input("Enter your choice: ", int, 1, 8)

        if choice == 1:
            title = input("Enter anime title: ")
            genres = input("Enter anime genres (comma separated): ").split(',')
            genres = [genre.strip() for genre in genres]
            episodes = get_user_input("Enter number of episodes: ", int, 1)
            status = input("Enter status (Watching/Completed/On Hold/Dropped): ")
            database.add_anime(title, episodes, status, genres)
            print("Anime added successfully!")
        elif choice == 2:
            anime_list = database.get_all_anime()
            print_anime_list(anime_list)
        elif choice == 3:
            anime_id = get_user_input("Enter anime ID to update: ", int, 1)
            title = input("Enter new title: ")
            genres = input("Enter new genres (comma separated): ").split(',')
            genres = [genre.strip() for genre in genres]
            episodes = get_user_input("Enter new number of episodes: ", int, 1)
            status = input("Enter new status (Watching/Completed/On Hold/Dropped): ")
            database.update_anime(anime_id, title, episodes, status, genres)
            print("Anime updated successfully!")
        elif choice == 4:
            anime_id = get_user_input("Enter anime ID to delete: ", int, 1)
            database.delete_anime(anime_id)
            print("Anime deleted successfully!")
        elif choice == 5:
            title = input("Enter anime title to search: ")
            anime_list = database.search_anime_by_title(title)
            print_anime_list(anime_list)
        elif choice == 6:
            genre = input("Enter genre to filter by: ")
            anime_list = database.filter_anime_by_genre(genre)
            print_anime_list(anime_list)
        elif choice == 7:
            status = input("Enter status to filter by (Watching/Completed/On Hold/Dropped): ")
            anime_list = database.filter_anime_by_status(status)
            print_anime_list(anime_list)
        elif choice == 8:
            print("Logged out successfully.")
            main()

if __name__ == "__main__":
    main()
