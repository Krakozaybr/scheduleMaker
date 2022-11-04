from .core import DBModel
import scheduler.config as config
from .fields import *


class Group(DBModel):
    name = StringField('name')


class Teacher(DBModel):
    name = StringField('name')


class Classroom(DBModel):
    name = StringField('name')


class Lesson(DBModel):
    name = StringField('name')
    teacher = ForeignField('teacher', Teacher)

    def are_same(self, another):
        return another.name == self.name


def structure_load():
    Group.load_objects(config.MAIN_DB_NAME)
    Teacher.load_objects(config.MAIN_DB_NAME)
    Classroom.load_objects(config.MAIN_DB_NAME)
    Lesson.load_objects(config.MAIN_DB_NAME)
