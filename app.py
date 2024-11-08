import sys

from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from PyQt6.QtGui import QPixmap

from PepinaScraper.scraper import Scraper

BASE_URL = 'https://pepina.bg/products/jeni/obuvki'

class MainWindow(qtw.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('BNR Crawler')

        layout = qtw.QVBoxLayout()

        btnRunScraper = qtw.QPushButton('Run Scraper')

        layout.addWidget(btnRunScraper)

        mainWidget = qtw.QWidget()
        mainWidget.setLayout(layout)

        self.setCentralWidget(mainWidget)

        self.show()


        # Add signals
        btnRunScraper.clicked.connect(self.onBtnRunScraperClicked)

    def onBtnRunScraperClicked(self):
        scraper = Scraper(BASE_URL)
        scraper.run()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec())