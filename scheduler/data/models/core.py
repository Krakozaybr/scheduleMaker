from collections import defaultdict

from .fields import Field, IntegerField
from ..database_interaction.orm import get, insert, update_by_id, delete_by_id


def staticinit(method):
    @property
    def prop(cls):
        prop_name = f'_{cls.__name__}_{method.__name__}'
        if not hasattr(cls, prop_name):
            prop_val = method(cls)
            setattr(cls, prop_name, prop_val)
        return getattr(cls, prop_name)

    return prop


class Null:
    def __init__(self):
        self.id = -1

    def __str__(self):
        return 'Пусто'


class DBModel:
    null = Null()

    id = IntegerField(
        'id',
        primary_key=True,
        autoincrement=True,
        read_only=True,
        russian_name='Идентификатор'
    )
    _fields: list[Field]

    def __init__(self, **kwargs):
        # Flag means that the object was created by user and need to be inserted, not updated
        self.created = False

        # Initializing object fields
        for field in self.fields:
            setattr(self, field.name, field.create_holder(kwargs[field.name]))
        # Initializing objects
        self.objects[self.id] = self

        # Checking max_id
        if self.id > self.max_id:
            self.max_id = self.id
        self.__post_init__()

    def __post_init__(self):
        pass

    @classmethod
    def new(cls, **kwargs):
        kwargs['id'] = cls.max_id.value + 1
        result = cls(**kwargs)
        result.created = True
        result.save()
        return result

    def save(self):
        if self.created:
            insert(
                self.db_name,
                self.get_table_name(),
                tuple(field.name for field in self.fields),
                self.get_data()
            )
            self.created = False
        else:
            update_by_id(
                self.db_name,
                self.get_table_name(),
                self.id,
                tuple(field.name for field in self.fields if field.name != 'id'),
                self.get_data_without_id()
            )

    def delete(self):
        delete_by_id(self.db_name, self.get_table_name(), self.id)
        del self.objects[self.id]

    def __getattribute__(self, item):
        field = super().__getattribute__(item)
        if isinstance(field, Field.ObjectHolder):
            return field.value
        return field

    def __setattr__(self, key, value):
        field = None
        if hasattr(self, key):
            field = super().__getattribute__(key)
        if isinstance(field, Field.ObjectHolder):
            field.value = value
        else:
            super().__setattr__(key, value)

    @classmethod
    def get_table_name(cls) -> str:
        return cls.__name__.lower() + 's'

    @classmethod
    def to_sql(cls):
        return '\n\t' + ',\n\t'.join(map(str, cls.fields)) + '\n'

    @classmethod
    @staticinit
    def fields(cls):
        return [
            getattr(cls, i)
            for i in dir(cls)
            if i != 'fields' and isinstance(getattr(cls, i), Field)
        ]

    @classmethod
    @staticinit
    def plural_class_name(cls):
        if hasattr(cls, '_plural_class_name'):
            return getattr(cls, '_plural_class_name')
        return cls.__name__ + 's'

    @classmethod
    @staticinit
    def objects(cls):
        return defaultdict(lambda: Null())

    @classmethod
    @staticinit
    def max_id(cls):
        return Field.ObjectHolder(0)

    @classmethod
    @staticinit
    def db_name(cls):
        return Field.ObjectHolder('')

    @classmethod
    def load_objects(cls, db_name):
        cls.db_name = db_name
        for vals in get(db_name, cls.get_table_name(), [f.name for f in cls.fields]):
            cls(**{field.name: val for field, val in zip(cls.fields, vals)})

    def get_holder(self, name):
        return super().__getattribute__(name)

    def get_data(self):
        return [self.get_holder(field.name).to_sql() for field in self.fields]

    def get_data_without_id(self):
        return [self.get_holder(field.name).to_sql() for field in self.fields if field.name != 'id']
