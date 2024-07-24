import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QMenuBar, QMenu, QAction, QListWidget,
                             QLineEdit, QDialog, QFormLayout, QDialogButtonBox, QStatusBar, QInputDialog, QComboBox,
                             QPushButton, QMessageBox, QFileDialog, QSpinBox, QHBoxLayout, QTableWidget, QTableWidgetItem)

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
        self.setGeometry(100, 100, 900, 700)
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

        self.rating_min_spinbox = QSpinBox(self)
        self.rating_min_spinbox.setRange(0, 10)
        self.rating_min_spinbox.setPrefix('Min Rating: ')
        self.rating_min_spinbox.setValue(0)

        self.rating_max_spinbox = QSpinBox(self)
        self.rating_max_spinbox.setRange(0, 10)
        self.rating_max_spinbox.setPrefix('Max Rating: ')
        self.rating_max_spinbox.setValue(10)

        self.filter_button = QPushButton('Filter by Rating', self)
        self.filter_button.clicked.connect(self.filter_by_rating)

        self.clear_filter_button = QPushButton('Clear Filters', self)
        self.clear_filter_button.clicked.connect(self.clear_filters)

        self.sort_by_genre_button = QPushButton('Sort by Genre', self)
        self.sort_by_genre_button.clicked.connect(self.sort_by_genre)

        self.filter_label = QLabel('Filter by:', self)

        self.search_history = QListWidget(self)
        self.search_history.setWindowTitle('Search History')
        self.search_history.setFixedWidth(200)
        self.search_history.setMaximumHeight(200)

        self.statistics_table = QTableWidget(0, 3, self)
        self.statistics_table.setHorizontalHeaderLabels(['Total Animes', 'Average Rating', 'Highest Rating'])

        self.view_details_button = QPushButton('View Details', self)
        self.view_details_button.clicked.connect(self.view_details)

        self.rate_anime_button = QPushButton('Rate Anime', self)
        self.rate_anime_button.clicked.connect(self.rate_anime)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.filter_combobox)
        filter_layout.addWidget(self.rating_min_spinbox)
        filter_layout.addWidget(self.rating_max_spinbox)
        filter_layout.addWidget(self.filter_button)
        filter_layout.addWidget(self.clear_filter_button)
        filter_layout.addWidget(self.sort_by_genre_button)
        filter_layout.addWidget(self.filter_label)

        central_widget = QWidget()
        layout = QVBoxLayout()

        welcome_label = QLabel('Welcome to the Anime List Database!', self)
        layout.addWidget(welcome_label)
        layout.addWidget(self.anime_list)
        layout.addWidget(self.sort_button)
        layout.addLayout(filter_layout)
        layout.addWidget(QLabel('Search History:'))
        layout.addWidget(self.search_history)
        layout.addWidget(self.statistics_table)
        layout.addWidget(self.view_details_button)
        layout.addWidget(self.rate_anime_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

    def setup_database(self):
        conn = sqlite3.connect('anime_list.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS anime (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                genre TEXT NOT NULL,
                rating REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

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
            self.add_to_search_history(title)

    def add_to_search_history(self, title):
        if title:
            self.search_history.addItem(title)

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
            self.statusbar.showMessage(f'Updated: {new_title}', 5000)

    def save_data(self, title, genre, rating):
        conn = sqlite3.connect('anime_list.db')
        c = conn.cursor()
        c.execute("INSERT INTO anime (title, genre, rating) VALUES (?, ?, ?)", (title, genre, rating))
        conn.commit()
        conn.close()
        self.refresh_list()

    def delete_data(self, title):
        conn = sqlite3.connect('anime_list.db')
        c = conn.cursor()
        c.execute("DELETE FROM anime WHERE title=?", (title,))
        conn.commit()
        conn.close()
        self.refresh_list()

    def update_data(self, old_title, new_title, new_genre, new_rating):
        conn = sqlite3.connect('anime_list.db')
        c = conn.cursor()
        c.execute("UPDATE anime SET title=?, genre=?, rating=? WHERE title=?", (new_title, new_genre, new_rating, old_title))
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
        self.update_statistics()

    def refresh_list(self):
        self.load_data()

    def update_statistics(self):
        conn = sqlite3.connect('anime_list.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*), AVG(rating), MAX(rating) FROM anime")
        result = c.fetchone()
        conn.close()
        total, avg_rating, highest_rating = result
        highest_rating = float(highest_rating) if highest_rating is not None else 0
        self.statistics_table.setRowCount(1)
        self.statistics_table.setItem(0, 0, QTableWidgetItem(str(total)))
        self.statistics_table.setItem(0, 1, QTableWidgetItem(f'{avg_rating:.2f}' if avg_rating is not None else 'N/A'))
        self.statistics_table.setItem(0, 2, QTableWidgetItem(f'{highest_rating:.1f}' if highest_rating is not None else 'N/A'))

    def clear_list(self):
        self.anime_list.clear()
        self.statusbar.showMessage('List cleared', 5000)

    def clear_filters(self):
        self.filter_combobox.setCurrentIndex(0)
        self.rating_min_spinbox.setValue(0)
        self.rating_max_spinbox.setValue(10)
        self.refresh_list()

    def search_anime(self):
        text, ok = QInputDialog.getText(self, 'Search Anime', 'Enter anime title:')
        if ok:
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
            self.add_to_search_history(text)

    def sort_by_title(self):
        self.anime_list.sortItems()

    def sort_by_genre(self):
        items = [self.anime_list.item(i) for i in range(self.anime_list.count())]
        sorted_items = sorted(items, key=lambda x: x.text().split(', ')[1].replace('Genre: ', ''))
        self.anime_list.clear()
        for item in sorted_items:
            self.anime_list.addItem(item.text())

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

    def filter_by_rating(self):
        min_rating = self.rating_min_spinbox.value()
        max_rating = self.rating_max_spinbox.value()
        conn = sqlite3.connect('anime_list.db')
        c = conn.cursor()
        c.execute("SELECT title, genre, rating FROM anime WHERE rating BETWEEN ? AND ?", (min_rating, max_rating))
        rows = c.fetchall()
        conn.close()
        self.anime_list.clear()
        for row in rows:
            title, genre, rating = row
            self.anime_list.addItem(f'Title: {title}, Genre: {genre}, Rating: {rating}')
        self.statusbar.showMessage(f'Filtered by rating: {min_rating} - {max_rating}', 5000)

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
                next(reader)
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

    def view_details(self):
        selected_item = self.anime_list.currentItem()
        if selected_item:
            data = selected_item.text().split(', ')
            title = data[0].replace('Title: ', '')
            genre = data[1].replace('Genre: ', '')
            rating = data[2].replace('Rating: ', '')
            QMessageBox.information(self, 'Anime Details', f'Title: {title}\nGenre: {genre}\nRating: {rating}')

    def rate_anime(self):
        selected_item = self.anime_list.currentItem()
        if selected_item:
            data = selected_item.text().split(', ')
            title = data[0].replace('Title: ', '')
            rating, ok = QInputDialog.getDouble(self, 'Rate Anime', 'Enter new rating (0-10):', 0, 0, 10, 1)
            if ok:
                conn = sqlite3.connect('anime_list.db')
                c = conn.cursor()
                c.execute("UPDATE anime SET rating=? WHERE title=?", (rating, title))
                conn.commit()
                conn.close()
                self.refresh_list()
                self.statusbar.showMessage(f'Updated rating for {title}', 5000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = AnimeListApp()
    main_window.show()
    sys.exit(app.exec_())
