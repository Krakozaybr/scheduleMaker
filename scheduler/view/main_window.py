from PyQt5.QtWidgets import QWidget

from scheduler.data.models.structure import Lesson, Group, Classroom, Teacher
from .help_windows.core import EditListDialog
from .make_schedule import ScheduleEditDialog
from .skeletons.main_window import Ui_Form as MainSkeleton


class MainWindow(MainSkeleton, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.makeScheduleBtn.clicked.connect(self.make_schedule)
        self.editBtn.clicked.connect(self.show_model_list)

    def show_model_list(self):
        EditListDialog(self, (Lesson, Group, Classroom, Teacher)).exec()

    def make_schedule(self):
        ScheduleEditDialog(self).exec()
