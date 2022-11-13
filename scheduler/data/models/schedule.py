from .structure import Lesson, structure_load, Group, Classroom
from .core import DBModel
from scheduler.config import MAIN_DB_NAME
from ..database_interaction.db_utils import get_dbs, db_exists, create_db_with_models, delete_db
from .fields import *
from pathvalidate import is_valid_filename


class Day(DBModel):
    lessons = ListField('lessons', Lesson, list_item_type=ForeignField)
    classrooms = ListField('classrooms', Classroom, list_item_type=ForeignField)
    group_obj = ForeignField('group_obj', Group)
    day_order = IntegerField('day_order')
    day_names = {
        1: 'Понедельник',
        2: 'Вторник',
        3: 'Среда',
        4: 'Четверг',
        5: 'Пятница',
        6: 'Суббота',
    }

    def add_empty(self):
        self.classrooms.append(Field.ObjectHolder(self.null, self.__class__.classrooms))
        self.lessons.append(Field.ObjectHolder(self.null, self.__class__.lessons))

    def remove_day_item_at(self, index):
        del self.classrooms[index]
        del self.lessons[index]

    def set_lesson(self, index, lesson):
        self.lessons[index].value = lesson

    def set_classroom(self, index, classroom):
        self.classrooms[index].value = classroom

    def uplift_at(self, i):
        if not i:
            return False
        return self._change_pos(i, -1)

    def downlift_at(self, i):
        if i == len(self.lessons) - 1:
            return False
        return self._change_pos(i, 1)

    def _change_pos(self, i, d):
        self.classrooms[i + d], self.classrooms[i] = self.classrooms[i], self.classrooms[i + d]
        self.lessons[i + d], self.lessons[i] = self.lessons[i], self.lessons[i + d]
        return True

    def __str__(self):
        return Day.day_names[self.day_order]

    def __gt__(self, other):
        return self.day_order > other.day_order


class Week(DBModel):
    days = ListField('days', Day, list_item_type=ForeignField)
    group_obj = ForeignField('group_obj', Group)


class Schedule:
    is_main_data_loaded = False

    def __init__(self, name):
        if not Schedule.is_main_data_loaded:
            structure_load()
            Schedule.is_main_data_loaded = True
        if not db_exists(name):
            create_db_with_models(name, Day, Week)
        Day.objects.clear()
        Week.objects.clear()
        Day.load_objects(name)
        Week.load_objects(name)

    @staticmethod
    def get_all_schedules():
        return [i for i in get_dbs() if i != MAIN_DB_NAME]

    @staticmethod
    def rename(old_name, new_name):
        if db_exists(new_name) or not is_valid_filename(new_name):
            return False
        os.rename(
            os.path.join(config.STORE_DIR, old_name) + '.sqlite',
            os.path.join(config.STORE_DIR, new_name) + '.sqlite'
        )
        return True

    @staticmethod
    def delete(name):
        delete_db(name)

    @staticmethod
    def create(name):
        if not is_valid_filename(name) or db_exists(name):
            return False
        create_db_with_models(name, Day, Week)
        return True

    @staticmethod
    def get_week(group):
        for week in Week.objects.values():
            if week.group_obj.id == group.id:
                return week
        # Not found a week
        days = []
        lessons = [Day.objects[-1]] * 6
        classrooms = [Day.objects[-1]] * 6
        for i in range(1, 7):
            days.append(Day.new(
                day_order=i,
                lessons=lessons,
                group=group,
                classrooms=classrooms,
                group_obj=group)
            )
        return Week.new(days=days, group_obj=group)
