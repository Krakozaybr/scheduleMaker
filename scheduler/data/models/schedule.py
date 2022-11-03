from dataclasses import dataclass
from structure import Lesson, structure_load, Group
from core import DBModel
from ..database_interaction.db_utils import get_all_schedules_db, db_exists
import scheduler.config as config
import json


@dataclass
class Day(DBModel):
    id: int
    lessons: list[Lesson]
    group: Group
    day_order: int

    db_fields = ['id', 'lessons', 'group_id', 'day_order']
    serialization_values = {
        'id': lambda self: self.id,
        'lessons': lambda self: json.dumps([i.id for i in self.lessons]),
        'group_id': lambda self: self.group.id,
        'day_order': lambda self: self.day_order,
    }

    @staticmethod
    def get_table_name() -> str:
        return config.days_table_name

    @staticmethod
    def load_days(db_name):
        data = Day.load_data(db_name, Day, fields=Day.db_fields)
        days = dict()
        for day_id, lessons_ids, group_id, day_order in data:
            lessons = []
            for lesson_id in json.loads(lessons_ids):
                lessons.append(Lesson.objects[lesson_id])
            days[day_id] = Day(day_id, lessons, Group.objects[group_id], day_order)
        return days

    def __gt__(self, other):
        return self.day_order > other.day_order

    def get_data(self):
        return


@dataclass
class Week(DBModel):
    id: int
    days: list[Day]
    group: Group

    db_fields = ['id', 'days', 'group_id']
    serialization_values = {
        'id': lambda self: self.id,
        'days': lambda self: json.dumps([i.id for i in self.days]),
        'group_id': lambda self: self.group.id
    }

    @staticmethod
    def get_table_name() -> str:
        return config.weeks_table_name

    @staticmethod
    def load_weeks(db_name, days_manager):
        data = Week.load_data(db_name, Week, fields=Week.db_fields)
        weeks = dict()
        for week_id, days_ids, group_id in data:
            days = []
            for day_id in json.loads(days_ids):
                days.append(days_manager[day_id])
            weeks[week_id] = Week(week_id, days, Group.objects[group_id])
        return weeks


@dataclass
class Schedule:
    objects = dict()  # name: Schedule
    is_main_data_loaded = False

    name: str
    weeks: dict[int, Week]
    days: dict[int, Day]

    @staticmethod
    def get_all_schedules():
        return get_all_schedules_db()

    @staticmethod
    def get_schedule(name):
        if name in Schedule.objects:
            return Schedule.objects[name]
        elif db_exists(name):
            return Schedule.load_schedule(name)
        return None

    @staticmethod
    def load_schedule(name):
        if not Schedule.is_main_data_loaded:
            structure_load()
            Schedule.is_main_data_loaded = True
        days = Day.load_days(name)
        weeks = Week.load_weeks(name, days)
        Schedule.objects[name] = Schedule(name, weeks, days)
