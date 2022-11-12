import os.path

from PIL.ImageQt import QImage
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QMainWindow, QScrollArea, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QDialog, \
    QDialogButtonBox, QFormLayout, QAbstractButton, QButtonGroup, QRadioButton, QCheckBox, QInputDialog

import scheduler.config as config
from scheduler.util import make_string_short
from .core import *
from .skeletons.schedule_window import Ui_Dialog
from scheduler.data.models.structure import Group
from scheduler.data.models.schedule import Schedule
from .structure_interaction import ItemListDialog


class ScheduleHolder(QWidget):
    def __init__(self, parent, name, button_group):
        super().__init__(parent)
        self.name = name

        layout = QHBoxLayout()
        self.name_label = QLabel(make_string_short(name, 30))
        rename_btn = PicButton(self, config.EDIT_IMG)
        delete_btn = PicButton(self, config.DELETE_IMG)
        self.radio_btn = QRadioButton()

        button_group.addButton(self.radio_btn)

        self.name_label.setFixedWidth(80)

        layout.addWidget(self.name_label)
        layout.addWidget(rename_btn)
        layout.addWidget(delete_btn)
        layout.addWidget(self.radio_btn)

        rename_btn.clicked.connect(self.rename)
        delete_btn.clicked.connect(self.delete)

        self.setLayout(layout)

    def rename(self):
        text, ok = QInputDialog.getMultiLineText(
            self,
            'Изменить название',
            'Введите название:',
            text=self.name
        )
        if ok:
            text = text.strip()
            res = Schedule.rename(self.name, text)
            if not res:
                ErrorDialog(self, 'Переименование невозможно').exec()
            else:
                self.name = text
                self.name_label.setText(text)

    def delete(self):
        dialog = ConfirmDialog(self)
        dialog.exec()
        if dialog.confirmed:
            Schedule.delete(self.name)
            self.setParent(None)

    def is_chosen(self):
        return self.radio_btn.isChecked()


class ScheduleSelectDialog(ItemListDialog):
    def __init__(self, parent):
        super().__init__(parent, Schedule.get_all_schedules(), 'Расписания')
        self.setWindowTitle('Выбрать расписание')

        self.buttonGroup = QButtonGroup()
        self.holders = dict()

        self.result = None

    def get_header_widgets(self):
        self.create_btn = QPushButton('Добавить расписание')
        self.create_btn.clicked.connect(self.create_schedule)
        return [self.create_btn]

    def get_button_box(self):
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        return buttonBox

    def get_row(self, obj):
        self.holders[obj] = ScheduleHolder(self, obj, self.buttonGroup)
        return self.holders[obj]

    def create_schedule(self):
        name, ok = QInputDialog.getMultiLineText(self, 'Добавить расписание', 'Введите название:')
        if ok:
            name = name.strip()
            if Schedule.create(name):
                self.objects = Schedule.get_all_schedules()
                self.update_objects()
            else:
                ErrorDialog(self, 'Не удалось создать расписание с таким названием').exec()

    def accept(self):
        super().accept()
        for holder in self.holders.values():
            if holder.is_chosen():
                self.result = holder.name
                break

    def get_result(self):
        return self.result


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
        dialog = ScheduleSelectDialog(self)
        dialog.exec()
        if dialog.get_result():
            self.selected_schedule = dialog.get_result()
            self.currentScheduleLabel.setText(self.selected_schedule)

    def export(self):
        print(Schedule.get_all_schedules())
