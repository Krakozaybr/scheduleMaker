from PyQt5.QtWidgets import QWidget

from scheduler.data.models.structure import Lesson, Group, Classroom, Teacher
from .help_windows.core import EditModelListWindow
from .make_schedule import ScheduleWindow
from .skeletons.main_window import Ui_Form as MainSkeleton


class MainWindow(MainSkeleton, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.makeScheduleBtn.clicked.connect(self.make_schedule)
        self.lessonsBtn.clicked.connect(lambda: self.show_model_list(Lesson, 'Уроки'))
        self.groupsBtn.clicked.connect(lambda: self.show_model_list(Group, 'Классы'))
        self.classroomsBtn.clicked.connect(lambda: self.show_model_list(Classroom, 'Кабинеты'))
        self.teachersBtn.clicked.connect(lambda: self.show_model_list(Teacher, 'Учителя'))
        self.active_window = None

    def show_model_list(self, cls, name):
        self.launch(EditModelListWindow(cls.objects, name))

    def make_schedule(self):
        self.launch(ScheduleWindow())

    def launch(self, win):
        if self.active_window:
            self.active_window.close()
        self.active_window = win
        win.show()

    def closeEvent(self, a0):
        for win in self.windows.values():
            win.close()
