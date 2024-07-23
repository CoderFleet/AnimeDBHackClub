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
        print(f"ID: {anime[0]}, Title: {anime[1]}, Genre: {anime[2]}, Episodes: {anime[3]}, Status: {anime[4]}")

def main():
    print("Welcome to the Anime List Database")
    while True:
        print("\nMenu:")
        print("1. Add Anime")
        print("2. View All Anime")
        print("3. Update Anime")
        print("4. Delete Anime")
        print("5. Search Anime by Title")
        print("6. Filter Anime by Genre")
        print("7. Filter Anime by Status")
        print("8. Exit")
        choice = get_user_input("Enter your choice: ", int, 1, 8)

        if choice == 1:
            title = input("Enter anime title: ")
            genre = input("Enter anime genre: ")
            episodes = get_user_input("Enter number of episodes: ", int, 1)
            status = input("Enter status (Watching/Completed/On Hold/Dropped): ")
            database.add_anime(title, genre, episodes, status)
            print("Anime added successfully!")
        elif choice == 2:
            anime_list = database.get_all_anime()
            print_anime_list(anime_list)
        elif choice == 3:
            anime_id = get_user_input("Enter anime ID to update: ", int, 1)
            title = input("Enter new title: ")
            genre = input("Enter new genre: ")
            episodes = get_user_input("Enter new number of episodes: ", int, 1)
            status = input("Enter new status (Watching/Completed/On Hold/Dropped): ")
            database.update_anime(anime_id, title, genre, episodes, status)
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
            break

if __name__ == "__main__":
    main()
