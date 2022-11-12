from .core import DBModel
from .fields import *
from scheduler.util import make_string_short


class NamedModel(DBModel):
    name = StringField('name', russian_name='Имя')
    length = 20

    def __str__(self):
        return make_string_short(self.name, self.length)


class Group(NamedModel):
    _plural_class_name = 'Классы'


class Teacher(NamedModel):
    _plural_class_name = 'Учителя'
    image = ImageField('image', default=f"'{config.DEFAULT_TEACHER_IMG}'", russian_name='Изображение')


class Classroom(NamedModel):
    _plural_class_name = 'Кабинеты'


class Lesson(NamedModel):
    _plural_class_name = 'Уроки'
    teacher = ForeignField('teacher', Teacher, russian_name='Учитель')

    def are_same(self, another):
        return another.name == self.name


def structure_load():
    Group.load_objects(config.MAIN_DB_NAME)
    Teacher.load_objects(config.MAIN_DB_NAME)
    Classroom.load_objects(config.MAIN_DB_NAME)
    Lesson.load_objects(config.MAIN_DB_NAME)
