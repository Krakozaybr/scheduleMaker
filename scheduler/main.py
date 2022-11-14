import sys

from PyQt5.QtWidgets import QApplication

from scheduler.config import MAIN_DB_NAME
from scheduler.data.database_interaction.db_utils import (
    create_db_with_models,
    db_exists,
)
from scheduler.data.models.structure import (
    Teacher,
    Group,
    Lesson,
    Classroom,
    structure_load,
)
from view.main_window import MainWindow


def create_main_db():
    create_db_with_models(MAIN_DB_NAME, Teacher, Group, Lesson, Classroom)


def start():
    # Checks if main db exists
    if not db_exists(MAIN_DB_NAME):
        create_main_db()
    # Loads the structure classes
    structure_load()
    # Launching PyQT5 application
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start()
