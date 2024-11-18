import sys
import os

from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtSql import QSqlTableModel

from PepinaScraper.scraper import Scraper
from PepinaScraper.db import DB


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


class TableViewWidget(qtw.QWidget):
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.setWindowTitle("Shoes data")

        # Layout setup
        layout = qtw.QVBoxLayout(self)

        # Filter input for size
        self.filter_input = qtw.QLineEdit(self)
        self.filter_input.setPlaceholderText("Filter by size...")
        self.filter_input.textChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_input)

        # Table view setup
        self.table_view = qtw.QTableView(self)
        layout.addWidget(self.table_view)

        # Model setup
        self.model = QSqlTableModel(self, db_connection)
        self.model.setTable("shoes")
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.model.select()

        # Configure column headers (optional)
        self.model.setHeaderData(0, qtc.Qt.Orientation.Horizontal, "Brand")
        self.model.setHeaderData(1, qtc.Qt.Orientation.Horizontal, "Title")
        self.model.setHeaderData(2, qtc.Qt.Orientation.Horizontal, "Price")
        self.model.setHeaderData(3, qtc.Qt.Orientation.Horizontal, "Color")
        self.model.setHeaderData(4, qtc.Qt.Orientation.Horizontal, "Sizes")
        self.model.setHeaderData(5, qtc.Qt.Orientation.Horizontal, "Link")

        # Set model to table view
        self.table_view.setModel(self.model)

        # Enable sorting
        self.table_view.setSortingEnabled(True)

        # Customize table view
        self.table_view.resizeColumnsToContents()

    def apply_filter(self):
        # Get the text from the filter input
        size = self.filter_input.text().strip()
        # Apply filter if there's a size input, otherwise clear filter
        if size:
            self.model.setFilter(f"FIND_IN_SET('{size}', sizes) > 0")
        else:
            self.model.setFilter("")  # Clear the filter


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
        qtw.QMessageBox.information(self, "Успех", "Скрейпингът е успешно завършен.")

    def on_scraper_error(self, error_message):
        '''Callback for handling scraper errors'''
        self.setCursor(qtc.Qt.CursorShape.ArrowCursor)
        self.btnShowData.setEnabled(True)
        qtw.QMessageBox.critical(self, "Грешка", f"Скрейпингът не е извършен: {error_message}")

    def show_data(self):
        if not hasattr(self, "tableViewWidget"):
            self.tableViewWidget = TableViewWidget(self.db.qsql_conn)
        self.tableViewWidget.show()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
