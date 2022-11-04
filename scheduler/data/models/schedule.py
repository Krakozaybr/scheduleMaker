from .structure import Lesson, structure_load, Group
from .core import DBModel
from scheduler.config import MAIN_DB_NAME
from ..database_interaction.db_utils import get_dbs, db_exists, create_db_with_models
from .fields import *


class Day(DBModel):
    lessons = ListField('lessons', Lesson, list_item_type=ForeignField)
    group = ForeignField('group_id', Group)
    day_order = IntegerField('day_order')

    def __gt__(self, other):
        return self.day_order > other.day_order


class Week(DBModel):
    days_ids = ListField('days', Day, list_item_type=ForeignField)
    group = ForeignField('group_id', Group)


class Schedule:
    is_main_data_loaded = False

    def __init__(self, name):
        if not Schedule.is_main_data_loaded:
            structure_load()
            Schedule.is_main_data_loaded = True
        if not db_exists(name):
            create_db_with_models(name, Day, Week)
        # Day.objects.clear()
        # Week.objects.clear()
        Day.load_objects(name)
        Week.load_objects(name)

    @staticmethod
    def get_all_schedules():
        return list(i for i in get_dbs() if i != MAIN_DB_NAME)
