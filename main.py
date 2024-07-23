import database

def get_user_input(prompt, dtype, min_value=None, max_value=None):
    while True:
        try:
            value = dtype(input(prompt))
            if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
                raise ValueError
            return value
        except ValueError:
            print(f"Please enter a valid {dtype.__name__} between {min_value} and {max_value}.")

def register():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    conn = database.create_connection()
    try:
        with conn:
            conn.execute('''
                INSERT INTO users (username, password)
                VALUES (?, ?)
            ''', (username, password))
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Username already exists.")

def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    conn = database.create_connection()
    with conn:
        cursor = conn.execute('''
            SELECT id FROM users
            WHERE username = ? AND password = ?
        ''', (username, password))
        user = cursor.fetchone()
        if user:
            print("Login successful!")
            return True
        else:
            print("Invalid username or password.")
            return False

def get_user_id(username):
    conn = database.create_connection()
    with conn:
        cursor = conn.execute('''
            SELECT id FROM users
            WHERE username = ?
        ''', (username,))
        user = cursor.fetchone()
        return user[0] if user else None

def print_anime_list(anime_list):
    print(f"{'ID':<5} {'Title':<30} {'Episodes':<10} {'Status':<10}")
    print("="*55)
    for anime in anime_list:
        print(f"{anime[0]:<5} {anime[1]:<30} {anime[2]:<10} {anime[3]:<10}")

def add_anime():
    title = input("Enter anime title: ")
    episodes = get_user_input("Enter number of episodes: ", int, 1)
    status = input("Enter status (e.g., 'Completed', 'Ongoing'): ")
    database.add_anime(title, episodes, status)
    print("Anime added successfully!")

def update_anime():
    anime_id = get_user_input("Enter anime ID to update: ", int, 1)
    title = input("Enter new title: ")
    episodes = get_user_input("Enter new number of episodes: ", int, 1)
    status = input("Enter new status (e.g., 'Completed', 'Ongoing'): ")
    database.update_anime(anime_id, title, episodes, status)
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
    genre_id = get_user_input("Enter genre ID to filter by: ", int, 1)
    anime_list = database.filter_anime_by_genre(genre_id)
    print_anime_list(anime_list)

def filter_anime_by_status():
    status = input("Enter status to filter by (e.g., 'Completed', 'Ongoing'): ")
    anime_list = database.filter_anime_by_status(status)
    print_anime_list(anime_list)

def search_anime_by_genres():
    genre_ids = list(map(int, input("Enter genre IDs (comma-separated): ").split(',')))
    anime_list = database.search_anime_by_genres(genre_ids)
    print_anime_list(anime_list)

def filter_anime_by_statuses():
    statuses = input("Enter statuses (comma-separated): ").split(',')
    anime_list = database.filter_anime_by_statuses(statuses)
    print_anime_list(anime_list)

def add_review(user_id):
    anime_id = get_user_input("Enter anime ID to review: ", int, 1)
    rating = get_user_input("Enter your rating (1-10): ", int, 1, 10)
    review = input("Enter your review: ")
    database.add_review(user_id, anime_id, rating, review)
    print("Review added successfully!")

def update_review():
    review_id = get_user_input("Enter review ID to update: ", int, 1)
    rating = get_user_input("Enter new rating (1-10): ", int, 1, 10)
    review = input("Enter new review: ")
    database.update_review(review_id, rating, review)
    print("Review updated successfully!")

def delete_review():
    review_id = get_user_input("Enter review ID to delete: ", int, 1)
    database.delete_review(review_id)
    print("Review deleted successfully!")

def view_reviews_for_anime():
    anime_id = get_user_input("Enter anime ID to view reviews: ", int, 1)
    reviews = database.get_reviews_for_anime(anime_id)
    if not reviews:
        print("No reviews found for this anime.")
        return
    print(f"{'Username':<20} {'Rating':<6} {'Review':<50}")
    print("="*80)
    for review in reviews:
        print(f"{review[0]:<20} {review[1]:<6} {review[2]:<50}")

def view_user_reviews(user_id):
    reviews = database.get_user_reviews(user_id)
    if not reviews:
        print("No reviews found for your account.")
        return
    print(f"{'Anime Title':<30} {'Rating':<6} {'Review':<50}")
    print("="*80)
    for review in reviews:
        print(f"{review[0]:<30} {review[1]:<6} {review[2]:<50}")

def view_preferences(user_id):
    preferences = database.get_preferences(user_id)
    if not preferences:
        print("No preferences found.")
        return
    print(f"{'Key':<20} {'Value':<50}")
    print("="*70)
    for key, value in preferences:
        print(f"{key:<20} {value:<50}")

def update_preferences(user_id):
    key = input("Enter preference key to update: ")
    value = input("Enter new value: ")
    database.update_preference(user_id, key, value)
    print("Preference updated successfully!")

def add_genre():
    name = input("Enter genre name: ")
    database.add_genre(name)
    print("Genre added successfully!")

def update_genre():
    genre_id = get_user_input("Enter genre ID to update: ", int, 1)
    new_name = input("Enter new genre name: ")
    database.update_genre(genre_id, new_name)
    print("Genre updated successfully!")

def delete_genre():
    genre_id = get_user_input("Enter genre ID to delete: ", int, 1)
    database.delete_genre(genre_id)
    print("Genre deleted successfully!")

def view_all_genres():
    genres = database.get_all_genres()
    print(f"{'ID':<5} {'Name':<30}")
    print("="*35)
    for genre in genres:
        print(f"{genre[0]:<5} {genre[1]:<30}")

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
        print("8. Search Anime by Multiple Genres")
        print("9. Filter Anime by Multiple Statuses")
        print("10. Add Review")
        print("11. Update Review")
        print("12. Delete Review")
        print("13. View Reviews for Anime")
        print("14. View Your Reviews")
        print("15. Export to CSV")
        print("16. Backup Database")
        print("17. View Preferences")
        print("18. Update Preferences")
        print("19. Manage Genres") # New option
        print("20. Logout")
        choice = get_user_input("Enter your choice: ", int, 1, 20)

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
            search_anime_by_genres()
        elif choice == 9:
            filter_anime_by_statuses()
        elif choice == 10:
            add_review(user_id)
        elif choice == 11:
            update_review()
        elif choice == 12:
            delete_review()
        elif choice == 13:
            view_reviews_for_anime()
        elif choice == 14:
            view_user_reviews(user_id)
        elif choice == 15:
            filename = input("Enter filename for export (default: anime_list.csv): ")
            if not filename:
                filename = 'anime_list.csv'
            database.export_to_csv(filename)
            print(f"Anime list exported to {filename}.")
        elif choice == 16:
            database.backup_database()
        elif choice == 17:
            if user_id:
                view_preferences(user_id)
        elif choice == 18:
            if user_id:
                update_preferences(user_id)
        elif choice == 19: # Manage genres
            print("\n1. Add Genre")
            print("2. Update Genre")
            print("3. Delete Genre")
            print("4. View All Genres")
            genre_choice = get_user_input("Enter your choice: ", int, 1, 4)
            if genre_choice == 1:
                add_genre()
            elif genre_choice == 2:
                update_genre()
            elif genre_choice == 3:
                delete_genre()
            elif genre_choice == 4:
                view_all_genres()
        elif choice == 20:
            print("Logged out successfully.")
            main()

if __name__ == "__main__":
    main()
