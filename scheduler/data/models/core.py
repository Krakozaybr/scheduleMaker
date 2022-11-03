from collections import defaultdict
from typing import Callable

from ..database_interaction.orm import get


class DBModel:

    db_fields: list[str]
    #  db_field: func(x), where x - obj
    serialization_values: dict[str, Callable]
    id: int

    @staticmethod
    def get_table_name() -> str:
        ...

    @staticmethod
    def load_data(db_name, clazz, fields='*'):
        return get(db_name, clazz.get_table_name(), fields)

    def get_data(self):
        return tuple(self.serialization_values[i](self) for i in self.db_fields)


class DBModelWithManager(DBModel):

    objects = defaultdict(lambda: DBModelWithManager())

    def __post_init__(self):
        if self.objects is DBModelWithManager.objects:
            self.__class__.objects = defaultdict(lambda: None)
        self.objects[self.id] = self
