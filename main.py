import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import mysql.connector


class BookCatalogApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Каталог книг")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #F5F5F5;")

        # Подключение к базе данных
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="root",  # замените на вашего пользователя MySQL
            password="admin",  # замените на ваш пароль
            database="book_catalog"
        )

        # Создаем интерфейс
        self.init_ui()

    def init_ui(self):
        # Заголовок
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 10, 10, 10)

        header_widget.setStyleSheet("background-color: #ABCFCE; border-radius: 4px;")

        header = QLabel("Каталог книг")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2C3E50;")

        logo = QLabel()
        pixmap = QPixmap("book_icon.png")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaledToHeight(50, Qt.SmoothTransformation))
        else:
            logo.setText("📚")
            logo.setStyleSheet("font-size: 30px;")

        header_layout.addWidget(header)
        header_layout.addWidget(logo, alignment=Qt.AlignRight)
        header_widget.setLayout(header_layout)

        # Scroll area для карточек
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_layout.setSpacing(5)  # Меньше расстояния между карточками
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        self.cards_container.setLayout(self.cards_layout)

        self.scroll_area.setWidget(self.cards_container)

        # Основной контейнер
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(header_widget)
        layout.addWidget(self.scroll_area)
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Загружаем данные
        self.load_books()

    def load_books(self):
        # Очищаем текущие карточки
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        cursor = self.db_connection.cursor(dictionary=True)
        query = """
            SELECT b.*, a.name as author_name, g.name as genre_name 
            FROM books b
            JOIN authors a ON b.author_id = a.author_id
            JOIN genres g ON b.genre_id = g.genre_id
            ORDER BY b.title
        """
        cursor.execute(query)
        books = cursor.fetchall()
        cursor.close()

        for book in books:
            self.add_book_card(book)

    def add_book_card(self, book):
        # Создаем обычный QWidget вместо QFrame, чтобы не было рамки по умолчанию
        card = QWidget()
        card.setStyleSheet("""
            background-color: white;
            border-radius: 4px;
            padding: 10px;
        """)

        card_layout = QVBoxLayout()
        card_layout.setSpacing(4)
        card_layout.setContentsMargins(6, 6, 6, 6)  # внутренние отступы

        title_label = QLabel(f"<b>{book['title']}</b>")
        title_label.setStyleSheet("color: #2C3E50;")

        author_label = QLabel(f"Автор: {book['author_name']}")
        genre_label = QLabel(f"Жанр: {book['genre_name']}")
        year_label = QLabel(f"Год издания: {book['publication_year']}")
        isbn_label = QLabel(f"ISBN: {book['isbn']}")

        price_qty_layout = QHBoxLayout()
        price_label = QLabel(f"Цена: {book['price']} ₽")
        qty_label = QLabel(f"В наличии: {book['quantity']} шт.")
        price_qty_layout.addWidget(price_label)
        price_qty_layout.addWidget(qty_label)
        price_qty_layout.addStretch()

        # Добавляем элементы на карточку
        card_layout.addWidget(title_label)
        card_layout.addWidget(author_label)
        card_layout.addWidget(genre_label)
        card_layout.addWidget(year_label)
        card_layout.addWidget(isbn_label)
        card_layout.addLayout(price_qty_layout)

        card.setLayout(card_layout)
        self.cards_layout.addWidget(card)

    def closeEvent(self, event):
        self.db_connection.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookCatalogApp()
    window.show()
    sys.exit(app.exec())