import os.path

from PIL.ImageQt import QImage
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QMainWindow, QScrollArea, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QDialog, \
    QDialogButtonBox, QFormLayout, QAbstractButton, QButtonGroup, QRadioButton, QCheckBox

from scheduler.config import IMAGES_DIR
from .skeletons.schedule_window import Ui_Dialog
from scheduler.data.models.structure import Group


class ScheduleHolder(QWidget):
    def __init__(self, parent, name):
        super().__init__(parent)
        self.name = name

        layout = QHBoxLayout()
        name_label = QLabel(name)
        rename_btn = QPushButton()

    def create(self):
        ...

    def rename(self):
        ...

    def delete(self):
        ...


class ScheduleSelectDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Выбрать расписание')
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)


class ScheduleEditDialog(Ui_Dialog, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(self.size())
        QScrollArea().setWidget(self.scheduleSpace)
        self.layout().setAlignment(Qt.AlignTop)

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
