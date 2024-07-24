import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QMenuBar, QMenu, QAction, QListWidget,
                             QLineEdit, QDialog, QFormLayout, QDialogButtonBox, QStatusBar, QInputDialog, QMenu,
                             QComboBox, QPushButton, QMessageBox, QFileDialog)

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
        layout.addRow('Rating (0-10):', self.rating_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_data(self):
        return self.title_input.text(), self.genre_input.text(), self.rating_input.text()

    def validate_rating(self, rating):
        try:
            value = float(rating)
            if 0 <= value <= 10:
                return True
            return False
        except ValueError:
            return False

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
        export_action = QAction('Export to CSV', self)
        import_action = QAction('Import from CSV', self)
        exit_action = QAction('Exit', self)

        file_menu.addAction(add_action)
        file_menu.addAction(clear_action)
        file_menu.addAction(search_action)
        file_menu.addAction(export_action)
        file_menu.addAction(import_action)
        file_menu.addAction(exit_action)

        add_action.triggered.connect(self.show_add_anime_dialog)
        clear_action.triggered.connect(self.clear_list)
        search_action.triggered.connect(self.search_anime)
        export_action.triggered.connect(self.export_to_csv)
        import_action.triggered.connect(self.import_from_csv)
        exit_action.triggered.connect(self.close)

        self.anime_list = QListWidget()
        self.anime_list.setContextMenuPolicy(3)
        self.anime_list.customContextMenuRequested.connect(self.show_context_menu)

        self.sort_button = QPushButton('Sort by Title', self)
        self.sort_button.clicked.connect(self.sort_by_title)

        self.filter_combobox = QComboBox(self)
        self.filter_combobox.addItem('All Genres')
        self.filter_combobox.addItem('Action')
        self.filter_combobox.addItem('Comedy')
        self.filter_combobox.addItem('Drama')
        self.filter_combobox.addItem('Fantasy')
        self.filter_combobox.addItem('Horror')
        self.filter_combobox.currentIndexChanged.connect(self.filter_by_genre)

        central_widget = QWidget()
        layout = QVBoxLayout()

        welcome_label = QLabel('Welcome to the Anime List Database!', self)
        layout.addWidget(welcome_label)
        layout.addWidget(self.anime_list)
        layout.addWidget(self.sort_button)
        layout.addWidget(self.filter_combobox)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

    def show_add_anime_dialog(self):
        dialog = AnimeEntryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            title, genre, rating = dialog.get_data()
            if not title.strip():
                QMessageBox.warning(self, 'Warning', 'Title cannot be empty.')
                return
            if not dialog.validate_rating(rating):
                QMessageBox.warning(self, 'Warning', 'Rating must be a number between 0 and 10.')
                return
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
            if not new_title.strip():
                QMessageBox.warning(self, 'Warning', 'Title cannot be empty.')
                return
            if not dialog.validate_rating(new_rating):
                QMessageBox.warning(self, 'Warning', 'Rating must be a number between 0 and 10.')
                return
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
        self.anime_list.clear()
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

    def sort_by_title(self):
        self.anime_list.sortItems()

    def filter_by_genre(self, index):
        genre = self.filter_combobox.currentText()
        conn = sqlite3.connect('anime_list.db')
        c = conn.cursor()
        if genre == 'All Genres':
            c.execute("SELECT title, genre, rating FROM anime")
        else:
            c.execute("SELECT title, genre, rating FROM anime WHERE genre=?", (genre,))
        rows = c.fetchall()
        conn.close()
        self.anime_list.clear()
        for row in rows:
            title, genre, rating = row
            self.anime_list.addItem(f'Title: {title}, Genre: {genre}, Rating: {rating}')
        self.statusbar.showMessage(f'Filtered by genre: {genre}', 5000)

    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Export to CSV', '', 'CSV Files (*.csv)')
        if file_path:
            conn = sqlite3.connect('anime_list.db')
            c = conn.cursor()
            c.execute("SELECT title, genre, rating FROM anime")
            rows = c.fetchall()
            conn.close()
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Title', 'Genre', 'Rating'])
                writer.writerows(rows)
            self.statusbar.showMessage(f'Exported to {file_path}', 5000)

    def import_from_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Import from CSV', '', 'CSV Files (*.csv)')
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                conn = sqlite3.connect('anime_list.db')
                c = conn.cursor()
                c.execute("DELETE FROM anime")
                for row in reader:
                    if len(row) == 3:
                        c.execute("INSERT INTO anime (title, genre, rating) VALUES (?, ?, ?)", row)
                conn.commit()
                conn.close()
            self.refresh_list()
            self.statusbar.showMessage(f'Imported from {file_path}', 5000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = AnimeListApp()
    main_window.show()
    sys.exit(app.exec_())
