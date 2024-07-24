import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QMenuBar, QMenu, QAction, QListWidget, QLineEdit, QDialog, QFormLayout, QDialogButtonBox, QStatusBar, QInputDialog, QMenu

class AnimeEntryDialog(QDialog):
    def __init__(self, parent=None, title='', genre='', rating=''):
        super().__init__(parent)
        self.setWindowTitle('Edit Anime' if title else 'Add New Anime')
        self.setGeometry(150, 150, 300, 200)
        self.initUI(title, genre, rating)

    def initUI(self, title, genre, rating):
        layout = QFormLayout()
        
        self.title_input = QLineEdit(self)
        self.genre_input = QLineEdit(self)
        self.rating_input = QLineEdit(self)

        self.title_input.setText(title)
        self.genre_input.setText(genre)
        self.rating_input.setText(rating)

        layout.addRow('Title:', self.title_input)
        layout.addRow('Genre:', self.genre_input)
        layout.addRow('Rating:', self.rating_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_data(self):
        return self.title_input.text(), self.genre_input.text(), self.rating_input.text()

class AnimeListApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Anime List Database')
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        self.setup_database()
        self.load_data()

    def initUI(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        add_action = QAction('Add Anime', self)
        clear_action = QAction('Clear List', self)
        search_action = QAction('Search Anime', self)
        exit_action = QAction('Exit', self)
        
        file_menu.addAction(add_action)
        file_menu.addAction(clear_action)
        file_menu.addAction(search_action)
        file_menu.addAction(exit_action)

        add_action.triggered.connect(self.show_add_anime_dialog)
        clear_action.triggered.connect(self.clear_list)
        search_action.triggered.connect(self.search_anime)
        exit_action.triggered.connect(self.close)

        self.anime_list = QListWidget()
        self.anime_list.setContextMenuPolicy(3)  # Custom context menu policy
        self.anime_list.customContextMenuRequested.connect(self.show_context_menu)

        central_widget = QWidget()
        layout = QVBoxLayout()

        welcome_label = QLabel('Welcome to the Anime List Database!', self)
        layout.addWidget(welcome_label)
        layout.addWidget(self.anime_list)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

    def show_add_anime_dialog(self):
        dialog = AnimeEntryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            title, genre, rating = dialog.get_data()
            self.anime_list.addItem(f'Title: {title}, Genre: {genre}, Rating: {rating}')
            self.save_data(title, genre, rating)
            self.statusbar.showMessage(f'Added: {title}', 5000)

    def show_context_menu(self, pos):
        menu = QMenu()
        edit_action = menu.addAction('Edit')
        remove_action = menu.addAction('Remove')
        action = menu.exec_(self.anime_list.viewport().mapToGlobal(pos))

        selected_item = self.anime_list.currentItem()
        if action == edit_action:
            if selected_item:
                data = selected_item.text().split(', ')
                title = data[0].replace('Title: ', '')
                genre = data[1].replace('Genre: ', '')
                rating = data[2].replace('Rating: ', '')
                self.show_edit_anime_dialog(title, genre, rating)
        elif action == remove_action:
            if selected_item:
                title = selected_item.text().split(', ')[0].replace('Title: ', '')
                self.anime_list.takeItem(self.anime_list.row(selected_item))
                self.delete_data(title)
                self.statusbar.showMessage(f'Removed: {title}', 5000)

    def show_edit_anime_dialog(self, title, genre, rating):
        dialog = AnimeEntryDialog(self, title, genre, rating)
        if dialog.exec_() == QDialog.Accepted:
            new_title, new_genre, new_rating = dialog.get_data()
            self.update_data(title, new_title, new_genre, new_rating)
            self.refresh_list()
            self.statusbar.showMessage(f'Updated: {title}', 5000)

    def save_data(self, title, genre, rating):
        conn = sqlite3.connect('anime_list.db')
        c = conn.cursor()
        c.execute("INSERT INTO anime (title, genre, rating) VALUES (?, ?, ?)", (title, genre, rating))
        conn.commit()
        conn.close()

    def update_data(self, old_title, new_title, genre, rating):
        conn = sqlite3.connect('anime_list.db')
        c = conn.cursor()
        c.execute("UPDATE anime SET title=?, genre=?, rating=? WHERE title=?", (new_title, genre, rating, old_title))
        conn.commit()
        conn.close()

    def delete_data(self, title):
        conn = sqlite3.connect('anime_list.db')
        c = conn.cursor()
        c.execute("DELETE FROM anime WHERE title=?", (title,))
        conn.commit()
        conn.close()

    def load_data(self):
        conn = sqlite3.connect('anime_list.db')
        c = conn.cursor()
        c.execute("SELECT title, genre, rating FROM anime")
        rows = c.fetchall()
        conn.close()
        for row in rows:
            title, genre, rating = row
            self.anime_list.addItem(f'Title: {title}, Genre: {genre}, Rating: {rating}')
        self.statusbar.showMessage('Loaded anime list from database', 5000)

    def refresh_list(self):
        self.anime_list.clear()
        self.load_data()

    def clear_list(self):
        self.anime_list.clear()
        conn = sqlite3.connect('anime_list.db')
        c = conn.cursor()
        c.execute("DELETE FROM anime")
        conn.commit()
        conn.close()
        self.statusbar.showMessage('Cleared anime list', 5000)

    def search_anime(self):
        text, ok = QInputDialog.getText(self, 'Search Anime', 'Enter title to search:')
        if ok and text:
            found = False
            for i in range(self.anime_list.count()):
                item = self.anime_list.item(i)
                if text.lower() in item.text().lower():
                    self.anime_list.setCurrentItem(item)
                    self.statusbar.showMessage(f'Found: {text}', 5000)
                    found = True
                    break
            if not found:
                self.statusbar.showMessage(f'No anime found with title: {text}', 5000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = AnimeListApp()
    main_window.show()
    sys.exit(app.exec_())
