import sys

from .skeletons.main_window import Ui_Form as MainSkeleton
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QBuffer
from PyQt5.QtGui import QPixmap, QImage, QColor, QTransform
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QTableWidgetItem, QComboBox, QPushButton, QMainWindow


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 300)
        self.combobox = QComboBox(self)
        self.combobox.move(10, 10)
        # self.combobox.addItem('123123')
        self.combobox.addAction()


class MainWindow(MainSkeleton, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.exportBtn.clicked.connect(self.export)

    def export(self):
        self.test_window = TestWindow()
        self.test_window.show()
