from .core import DBModel
import scheduler.config as config
from .fields import *


class NamedModel(DBModel):
    name = StringField('name', russian_name='Имя')
    length = 20

    def __str__(self):
        if len(self.name) > self.length:
            return self.name[:self.length - 3] + '...'
        return self.name[:self.length]


class Group(NamedModel):
    pass


class Teacher(NamedModel):
    image = ImageField('image', default="'default.png'", russian_name='Изображение')


class Classroom(NamedModel):
    pass


class Lesson(NamedModel):
    teacher = ForeignField('teacher', Teacher, russian_name='Учитель')

    def are_same(self, another):
        return another.name == self.name


def structure_load():
    Group.load_objects(config.MAIN_DB_NAME)
    Teacher.load_objects(config.MAIN_DB_NAME)
    Classroom.load_objects(config.MAIN_DB_NAME)
    Lesson.load_objects(config.MAIN_DB_NAME)
