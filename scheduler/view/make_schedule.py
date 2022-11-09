import os.path

from PIL.ImageQt import QImage
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QMainWindow, QScrollArea, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QDialog, \
    QDialogButtonBox, QFormLayout, QAbstractButton, QButtonGroup, QRadioButton, QCheckBox

from scheduler.config import IMAGES_DIR
from .skeletons.schedule_window import Ui_Form
from scheduler.data.models.structure import Group


class ScheduleSelectDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        ...


class ScheduleWindow(Ui_Form, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        QScrollArea(self).setWidget(self.scheduleSpace)

        self.selected_schedule = None
        for group in Group.objects.values():
            self.groupSelect.addItem(str(group), group)

        self.exportBtn.clicked.connect(self.export)
        self.selectScheduleBtn.clicked.connect(self.select_schedule)
        self.groupSelect.currentIndexChanged.connect(self.update_content)

    def update_content(self):
        if self.selected_schedule and self.groupSelect.currentIndex() > -1:
            group = self.groupSelect.currentData()


    def select_schedule(self):
        ...

    def export(self):
        print(self.groupSelect.currentData())
