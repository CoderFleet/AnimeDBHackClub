import database

def main():
    print("Welcome to the Anime List Database")
    while True:
        print("\nMenu:")
        print("1. Add Anime")
        print("2. View All Anime")
        print("3. Update Anime")
        print("4. Delete Anime")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            title = input("Enter anime title: ")
            genre = input("Enter anime genre: ")
            episodes = int(input("Enter number of episodes: "))
            status = input("Enter status (Watching/Completed/On Hold/Dropped): ")
            database.add_anime(title, genre, episodes, status)
            print("Anime added successfully!")
        elif choice == '2':
            anime_list = database.get_all_anime()
            for anime in anime_list:
                print(f"ID: {anime[0]}, Title: {anime[1]}, Genre: {anime[2]}, Episodes: {anime[3]}, Status: {anime[4]}")
        elif choice == '3':
            anime_id = int(input("Enter anime ID to update: "))
            title = input("Enter new title: ")
            genre = input("Enter new genre: ")
            episodes = int(input("Enter new number of episodes: "))
            status = input("Enter new status (Watching/Completed/On Hold/Dropped): ")
            database.update_anime(anime_id, title, genre, episodes, status)
            print("Anime updated successfully!")
        elif choice == '4':
            anime_id = int(input("Enter anime ID to delete: "))
            database.delete_anime(anime_id)
            print("Anime deleted successfully!")
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
