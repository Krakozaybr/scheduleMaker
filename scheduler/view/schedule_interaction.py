from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QScrollArea,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QButtonGroup,
    QRadioButton,
    QInputDialog,
    QFileDialog,
)
import xlsxwriter
import scheduler.config as config
from scheduler.data.models.schedule import Schedule, Day
from scheduler.data.models.structure import Group, Lesson, Classroom
from scheduler.util import make_string_short
from .core import *
from .skeletons.schedule_window import Ui_Dialog
from .structure_interaction import ItemListDialog, SelectOneItemListDialog


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
            self, "Изменить название", "Введите название:", text=self.name
        )
        if ok:
            text = text.strip()
            res = Schedule.rename(self.name, text)
            if not res:
                ErrorDialog(self, "Переименование невозможно").exec()
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
        super().__init__(parent, Schedule.get_all_schedules(), "Расписания")
        self.setWindowTitle("Выбрать расписание")

        self.buttonGroup = QButtonGroup()
        self.holders = dict()

        self.result = None

    def get_header_widgets(self):
        self.create_btn = QPushButton("Добавить расписание")
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
        name, ok = QInputDialog.getMultiLineText(
            self, "Добавить расписание", "Введите название:"
        )
        if ok:
            name = name.strip()
            if Schedule.create(name):
                self.objects = Schedule.get_all_schedules()
                self.update_objects()
            else:
                ErrorDialog(
                    self, "Не удалось создать расписание с таким названием"
                ).exec()

    def accept(self):
        super().accept()
        for holder in self.holders.values():
            if holder.is_chosen():
                self.result = holder.name
                break

    def get_result(self):
        return self.result


class DayEventHolder(QWidget):
    def __init__(self, parent, lesson, classroom, update_parent, index, day):
        super().__init__(parent)
        self.lesson = lesson
        self.classroom = classroom
        self.update_parent = update_parent
        self.index = index
        self.day = day

        layout = QHBoxLayout()

        change_classroom_btn = PicButton(self, config.EDIT_IMG)
        change_lesson_btn = PicButton(self, config.EDIT_IMG)
        uplift_btn = PicButton(self, config.UPLIFT_IMG)
        downlift_btn = PicButton(self, config.DOWNLIFT_IMG)
        delete_btn = PicButton(self, config.DELETE_IMG)

        change_classroom_btn.clicked.connect(self.change_classroom)
        change_lesson_btn.clicked.connect(self.change_lesson)
        uplift_btn.clicked.connect(self.uplift)
        downlift_btn.clicked.connect(self.downlift)
        delete_btn.clicked.connect(self.delete_lesson)

        self.lesson_label = QLabel(str(lesson))
        self.lesson_label.setFixedHeight(uplift_btn.height())
        self.lesson_label.setAlignment(Qt.AlignCenter)
        self.classroom_label = QLabel(str(classroom))
        self.classroom_label.setAlignment(Qt.AlignCenter)
        self.classroom_label.setFixedHeight(uplift_btn.height())

        self.check_if_overlap()

        layout.addWidget(QLabel(str(self.index + 1)))
        layout.addWidget(self.lesson_label)
        layout.addWidget(change_lesson_btn)
        layout.addWidget(self.classroom_label)
        layout.addWidget(change_classroom_btn)
        layout.addWidget(uplift_btn)
        layout.addWidget(downlift_btn)
        layout.addWidget(delete_btn)

        self.setLayout(layout)

    def change_classroom(self):
        dialog = SelectOneItemListDialog(self, Classroom.objects)
        dialog.exec()
        res = dialog.get_selected()
        if res:
            self.day.set_classroom(self.index, res)
            self.update_parent()

    def change_lesson(self):
        dialog = SelectOneItemListDialog(self, Lesson.objects)
        dialog.exec()
        res = dialog.get_selected()
        if res:
            self.day.set_lesson(self.index, res)
            self.update_parent()

    def uplift(self):
        if self.day.uplift_at(self.index):
            self.update_parent()
        else:
            ErrorDialog(self, "Операция невозможна")

    def downlift(self):
        if self.day.downlift_at(self.index):
            self.update_parent()
        else:
            ErrorDialog(self, "Операция невозможна")

    def delete_lesson(self):
        dialog = ConfirmDialog(self)
        dialog.exec()
        if dialog.confirmed:
            self.day.remove_day_item_at(self.index)
            self.update_parent()

    def check_if_overlap(self):
        style = """
            background: red;
            padding: 2px;
            color: white;
            """
        if self.classroom.id > -1 and any(
            i.classrooms[self.index].id == self.classroom.id
            for i in Day.objects.values()
            if isinstance(i, Day)
            and i.classrooms[self.index].id > -1
            and i.id != self.day.id
            and i.day_order == self.day.day_order
        ):
            self.classroom_label.setStyleSheet(style)
        if self.lesson.id > -1 and any(
            i.lessons[self.index].teacher.id == self.lesson.teacher.id
            for i in Day.objects.values()
            if isinstance(i, Day)
            and i.lessons[self.index].id > -1
            and i.id != self.day.id
            and i.day_order == self.day.day_order
        ):
            self.lesson_label.setStyleSheet(style)


class DayHolder(QWidget):
    def __init__(self, parent, day):
        super().__init__()
        self.parent_dialog = parent
        self.day = day
        self.add_lesson_btn = QPushButton("Добавить урок")

        layout = QVBoxLayout()
        self.lessons_layout = QVBoxLayout()

        self.update_day_items()

        layout.addWidget(QLabel(str(day)))
        layout.addItem(self.lessons_layout)
        layout.addWidget(self.add_lesson_btn)

        self.add_lesson_btn.clicked.connect(self.add_day_item)

        self.setLayout(layout)

    def update_day_items(self):
        day_items = zip(self.day.lessons, self.day.classrooms)

        for i in reversed(range(self.lessons_layout.count())):
            self.lessons_layout.itemAt(i).widget().setParent(None)

        for i, (lesson, classroom) in enumerate(day_items):
            self.lessons_layout.addWidget(
                DayEventHolder(self, lesson, classroom, self.repaint_all, i, self.day)
            )
        self.parent_dialog.update_layout()

    def repaint_all(self):
        self.day.save()
        self.parent_dialog.update_content()

    def add_day_item(self):
        self.day.add_empty()
        self.repaint_all()


class ScheduleEditDialog(Ui_Dialog, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.scroll = None
        self.widget_container = None
        self.scroll_layout = None
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.layout().setAlignment(Qt.AlignTop)

        self.selected_schedule = None
        self.selected_group = None
        self.day_holders = []

        for group in Group.objects.values():
            self.groupSelect.addItem(str(group), group)

        self.exportBtn.clicked.connect(self.export)
        self.selectScheduleBtn.clicked.connect(self.select_schedule)
        self.groupSelect.currentIndexChanged.connect(self.update_content)

    def update_content(self):
        if self.selected_schedule and self.groupSelect.currentIndex() > -1:
            group = self.groupSelect.currentData()
            self.day_holders.clear()
            self.scheduleSpace.setParent(None)

            self.scheduleSpace = QtWidgets.QWidget(self)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
            )
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.scheduleSpace.sizePolicy().hasHeightForWidth()
            )
            self.scheduleSpace.setSizePolicy(sizePolicy)
            self.scheduleSpace.setObjectName("scheduleSpace")
            self.verticalLayout.addWidget(self.scheduleSpace)

            self.scroll_layout = QVBoxLayout()
            widget = QWidget()
            self.widget_container = QVBoxLayout()
            self.scroll = QScrollArea()
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scroll.setFixedHeight(470)

            for day in Schedule.get_week(group).days:
                day_holder = DayHolder(self, day)
                self.day_holders.append(day_holder)
                self.widget_container.addWidget(day_holder)
            widget.setLayout(self.widget_container)
            self.scroll.setWidget(widget)
            self.scroll_layout.addWidget(self.scroll)
            self.scheduleSpace.setLayout(self.scroll_layout)
            self.scheduleSpace.repaint()

    def update_layout(self):
        self.scroll.setParent(None)
        self.scroll_layout.addWidget(self.scroll)

    def select_schedule(self):
        dialog = ScheduleSelectDialog(self)
        dialog.exec()
        if dialog.get_result():
            self.selected_schedule = dialog.get_result()
            Schedule(self.selected_schedule)
            self.currentScheduleLabel.setText(self.selected_schedule)
            self.update_content()

    def export(self):
        filename = QFileDialog.getSaveFileName(
            self, "Save excel file", "", "Audio Files (*.xlsx)"
        )[0]
        if filename.endswith(".xlsx"):
            with xlsxwriter.Workbook(filename) as workbook:
                try:
                    worksheet = workbook.add_worksheet()

                    for i, group in enumerate(Group.objects.values()):
                        week = Schedule.get_week(group)
                        left_col = i * 5
                        worksheet.merge_range(0, left_col, 0, left_col + 3, str(group))
                        cursor = 2
                        for day in week.days:
                            worksheet.merge_range(
                                cursor, left_col, cursor, left_col + 3, str(day)
                            )
                            cursor += 1
                            for j, (lesson, classroom) in enumerate(
                                zip(day.lessons, day.classrooms)
                            ):
                                worksheet.write(cursor, left_col, j + 1)
                                worksheet.merge_range(
                                    cursor,
                                    left_col + 1,
                                    cursor,
                                    left_col + 2,
                                    str(lesson),
                                )
                                worksheet.write(cursor, left_col + 3, str(classroom))
                                cursor += 1
                            cursor += 1
                    workbook.close()
                except Exception as err:
                    print(err)
        elif filename:
            ErrorDialog(self, "Недопустимый формат").exec()
