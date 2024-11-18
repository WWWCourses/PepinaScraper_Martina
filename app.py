import sys
import os
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from PyQt6.QtGui import QPixmap
from PepinaScraper.scraper import Scraper
from PepinaScraper.db import DB
from PyQt6.QtWidgets import QMessageBox
from PepinaScraper import read_config
from PepinaScraper.crawler import Crawler

from PyQt6.QtCore import QThread, pyqtSignal

BASE_URL = 'https://pepina.bg/products/jeni/obuvki'

class ScraperThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url

    def run(self):
        try:
            scraper = Scraper(self.base_url)
            scraper.run()  # това ще се стартира в отделен thread
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class DataTable(qtw.QTableWidget):
    '''Клас за представяне на таблицата с данни'''
    def __init__(self, db, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db  # Pass database object explicitly
        self.column_names = ["Brand", "Price", "Color"]
        self.setup_table()

    def setup_table(self):
        self.setColumnCount(len(self.column_names))
        self.setHorizontalHeaderLabels(self.column_names)
        self.resizeColumnsToContents()
        self.setSortingEnabled(True)
        self.update_table(self.db.select_all_data())

    def update_table(self, data):
        self.setRowCount(0)
        for row_num, row_data in enumerate(data):
            self.insertRow(row_num)
            for col_num, value in enumerate(row_data):
                self.setItem(row_num, col_num, qtw.QTableWidgetItem(str(value)))

    def filter_by_size(self, size):
        try:
            size = float(size)
            data = self.db.select_data_by_size(size)
            self.update_table(data)
        except ValueError:
            qtw.QMessageBox.warning(None, "Грешка", "Моля, въведете валиден номер.")

    def sort_by_price(self, ascending=True):
        column = 1
        order = qtc.Qt.SortOrder.AscendingOrder if ascending else qtc.Qt.SortOrder.DescendingOrder
        self.sortItems(column, order)


class TableViewWidget(qtw.QWidget):
    '''Клас за интерфейс и сортиране с филтър'''
    def __init__(self, db, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tableView = DataTable(db)
        self.setup_gui()

    def setup_gui(self):
        layout = qtw.QVBoxLayout()
        layout.addWidget(self.tableView)

        self.filter_size_input = qtw.QLineEdit()
        self.filter_size_input.setPlaceholderText('Въведете номера на обувката (пример, "38") ')
        self.filter_size_input.textChanged.connect(self.tableView.filter_by_size)
        layout.addWidget(self.filter_size_input)

        btnSortAsc = qtw.QPushButton("Сортиране по възходящ ред.")
        btnSortAsc.clicked.connect(lambda: self.tableView.sort_by_price(ascending=True))
        layout.addWidget(btnSortAsc)

        btnSortDesc = qtw.QPushButton("Сортиране по низходящ ред.")
        btnSortDesc.clicked.connect(lambda: self.tableView.sort_by_price(ascending=False))
        layout.addWidget(btnSortDesc)

        btnClose = qtw.QPushButton("Затваряне")
        btnClose.clicked.connect(self.close)
        layout.addWidget(btnClose)

        self.setLayout(layout)


class MainWindow(qtw.QMainWindow):
    '''Главен прозорец на приложението'''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Pepina Crawler')

        self.db = DB()
        if not self.db.conn:
            QMessageBox.critical(None, "Грешка на базата данни!", "Провалена връзка на базата с данни.")
            sys.exit()

        self.setup_gui()

    def setup_gui(self):
        layout = qtw.QVBoxLayout()

        img_label = qtw.QLabel()
        pixmap = QPixmap(self.get_image_path())
        pixmap = pixmap.scaled(600, 400, qtc.Qt.AspectRatioMode.KeepAspectRatio)
        img_label.setPixmap(pixmap)
        img_label.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(img_label)

        btnRunScraper = qtw.QPushButton('Стартиране на Скрейп')
        btnRunScraper.clicked.connect(self.run_scraper)
        layout.addWidget(btnRunScraper)

        self.btnShowData = qtw.QPushButton("Показване на данните")
        self.btnShowData.clicked.connect(self.show_data)
        layout.addWidget(self.btnShowData)

        mainWidget = qtw.QWidget()
        mainWidget.setLayout(layout)
        self.setCentralWidget(mainWidget)
        self.show()

    def get_image_path(self):
        return os.path.abspath('./PepinaScraper/images/PepinaScraper.png')

    def run_scraper(self):
        '''Функция за стартиране на скрейпване в отделен thread'''
        self.scraper_thread = ScraperThread(BASE_URL)
        self.scraper_thread.finished.connect(self.on_scraper_finished)
        self.scraper_thread.error.connect(self.on_scraper_error)
        self.scraper_thread.start()

        # Disable UI elements while scraping
        self.setCursor(qtc.Qt.CursorShape.WaitCursor)
        self.btnShowData.setEnabled(False)

    def on_scraper_finished(self):
        '''Callback when scraping is done'''
        self.setCursor(qtc.Qt.CursorShape.ArrowCursor)
        self.btnShowData.setEnabled(True)
        self.load_data()  # Refresh the data in the table
        qtw.QMessageBox.information(self, "Успех", "Скрейпингът е успешно завършен.")

    def on_scraper_error(self, error_message):
        '''Callback for handling scraper errors'''
        self.setCursor(qtc.Qt.CursorShape.ArrowCursor)
        self.btnShowData.setEnabled(True)
        qtw.QMessageBox.critical(self, "Грешка", f"Скрейпингът не е извършен: {error_message}")

    def show_data(self):
        if not hasattr(self, "tableViewWidget"):
            self.tableViewWidget = TableViewWidget(self.db)
        self.tableViewWidget.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
