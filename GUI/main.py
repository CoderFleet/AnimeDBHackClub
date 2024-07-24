import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QMenuBar, QMenu, QAction, QListWidget, QLineEdit, QPushButton, QDialog, QFormLayout, QDialogButtonBox

class AnimeEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add New Anime')
        self.setGeometry(150, 150, 300, 200)
        self.initUI()

    def initUI(self):
        layout = QFormLayout()
        
        self.title_input = QLineEdit(self)
        self.genre_input = QLineEdit(self)
        self.rating_input = QLineEdit(self)

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

    def initUI(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        add_action = QAction('Add Anime', self)
        exit_action = QAction('Exit', self)
        
        file_menu.addAction(add_action)
        file_menu.addAction(exit_action)

        add_action.triggered.connect(self.show_add_anime_dialog)
        exit_action.triggered.connect(self.close)

        central_widget = QWidget()
        layout = QVBoxLayout()

        welcome_label = QLabel('Welcome to the Anime List Database!', self)
        layout.addWidget(welcome_label)

        self.anime_list = QListWidget()
        self.anime_list.addItem('No anime added yet.')
        layout.addWidget(self.anime_list)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_add_anime_dialog(self):
        dialog = AnimeEntryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            title, genre, rating = dialog.get_data()
            self.anime_list.addItem(f'Title: {title}, Genre: {genre}, Rating: {rating}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = AnimeListApp()
    main_window.show()
    sys.exit(app.exec_())
