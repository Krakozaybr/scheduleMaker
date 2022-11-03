import sys

from PyQt5.QtWidgets import QApplication

from data.database_interaction.db_utils import create_main_db, create_schedule_db
from data.models.structure import Teacher, Group
from data.process_image import process_image
from view.main_window import MainWindow


def create_dbs():
    create_main_db()
    create_schedule_db('example')


def test_teacher():
    Teacher.load_objects()
    t = Teacher(2, 'name')
    print(Teacher.db_fields)
    print(*[i.get_data() for i in Teacher.objects.values()], sep='\n')


def test_image():
    process_image(r'C:\Users\alex_\PycharmProjects\scheduleMaker\scheduler\data\store\images\default.png',
                  'default.png')


def start():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    start()
