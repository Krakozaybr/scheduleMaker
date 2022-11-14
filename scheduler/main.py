import sys

from PyQt5.QtWidgets import QApplication

from scheduler.config import MAIN_DB_NAME
from scheduler.data.database_interaction.db_utils import (
    create_db_with_models,
    delete_db,
)
from scheduler.data.database_interaction.sql_commands import CREATE_DB_TABLE, INSERT
from scheduler.data.models.schedule import Day
from scheduler.data.models.structure import (
    Teacher,
    Group,
    Lesson,
    Classroom,
    structure_load,
)
from scheduler.data.process_image import process_image
from view.main_window import MainWindow


def create_dbs():
    create_db_with_models(MAIN_DB_NAME, Teacher, Group, Lesson, Classroom)
    create_db_with_models("example", Day)


def delete_dbs():
    delete_db(MAIN_DB_NAME)
    delete_db("example")


def test_teacher():
    Teacher.new(name="toge", image="default.png")
    lesson = Lesson(id=1, name="LolKek", teacher=1)
    print(lesson.teacher.name)
    print(CREATE_DB_TABLE % (Lesson.get_table_name(), lesson.to_sql()))
    print(lesson.get_data())
    print(
        INSERT
        % (
            lesson.get_table_name(),
            ", ".join(map(lambda x: x.name, lesson.fields)),
            ", ".join(map(str, lesson.get_data())),
        )
    )


def test_image():
    process_image(
        r"C:\Users\alex_\PycharmProjects\scheduleMaker\scheduler\data\store\images\default.png",
        "default.png",
    )


def start():
    structure_load()
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())


def db_test2():
    Teacher.load_objects(MAIN_DB_NAME)
    Lesson.load_objects(MAIN_DB_NAME)
    lesson = Lesson.new(name="les1", teacher=1)
    print(lesson.get_data())
    print(lesson.get_data_without_id())
    lesson = Lesson.objects[1]
    lesson.teacher.value.name.value = "teach3"
    print(lesson.get_data())
    lesson.teacher.value.save()
    lesson.save()


if __name__ == "__main__":
    start()
    # test_teacher()
