from dataclasses import dataclass
from .core import DBModelWithManager
import scheduler.config as config


@dataclass
class Group(DBModelWithManager):
    db_fields = ['id', 'name']
    serialization_values = {
        'id': lambda self: self.id,
        'name': lambda self: self.name
    }

    id: int
    name: str

    @staticmethod
    def load_objects():
        data = Group.load_data(config.MAIN_DB_NAME, Group, fields=Group.db_fields)
        for group_id, name in data:
            Group(group_id, name)

    @staticmethod
    def get_table_name() -> str:
        return config.groups_table_name


@dataclass
class Teacher(DBModelWithManager):
    db_fields = ['id', 'name']
    serialization_values = {
        'id': lambda self: self.id,
        'name': lambda self: self.name
    }

    id: int
    name: str

    @staticmethod
    def load_objects():
        data = Teacher.load_data(config.MAIN_DB_NAME, Teacher, fields=Teacher.db_fields)
        for teacher_id, name in data or []:
            Teacher(teacher_id, name)

    @staticmethod
    def get_table_name() -> str:
        return config.teachers_table_name


@dataclass
class Classroom(DBModelWithManager):
    db_fields = ['id', 'name']
    serialization_values = {
        'id': lambda self: self.id,
        'name': lambda self: self.name
    }

    id: int
    name: str

    @staticmethod
    def load_objects():
        data = Classroom.load_data(config.MAIN_DB_NAME, Classroom, fields=Classroom.db_fields)
        for classroom_id, name in data:
            Classroom(classroom_id, name)

    @staticmethod
    def get_table_name() -> str:
        return config.classrooms_table_name


class Lesson(DBModelWithManager):
    db_fields = ['id', 'teacher_id', 'name']
    serialization_values = {
        'id': lambda self: self.id,
        'teacher_id': lambda self: self.teacher.id,
        'name': lambda self: self.name,
    }

    def __init__(self, lesson_id: int, teacher_id: int, name: str):
        self.id = lesson_id
        self.teacher = Teacher.objects[teacher_id]
        self.name = name
        self.__post_init__()

    def are_same(self, another):
        return another.name == self.name

    @staticmethod
    def load_objects():
        data = Lesson.load_data(config.MAIN_DB_NAME, Lesson, fields=Lesson.db_fields)
        for lesson_id, teacher_id, name in data:
            Lesson(lesson_id, teacher_id, name)

    @staticmethod
    def get_table_name() -> str:
        return config.lessons_table_name


def structure_load():
    Group.load_objects()
    Teacher.load_objects()
    Classroom.load_objects()
    Lesson.load_objects()
