from .fields import Field, IntegerField
from ..database_interaction.orm import get, insert, update_by_id


def staticinit(method):
    @property
    def prop(cls):
        prop_name = f'_{cls.__name__}_{method.__name__}'
        if not hasattr(cls, prop_name):
            prop_val = method(cls)
            setattr(cls, prop_name, prop_val)
        return getattr(cls, prop_name)

    return prop


class DBModel:
    id = IntegerField('id', primary_key=True, autoincrement=True)
    _fields: list[Field]

    def __init__(self, **kwargs):
        # Flag means that the object was created by user and need to be inserted, not updated
        self.created = False

        # Initializing object fields
        for field in self.fields:
            setattr(self, field.name, field.create_holder(kwargs[field.name]))
        # Initializing objects
        self.objects[self.id.value] = self

        # Checking max_id
        if self.id.value > self.max_id.value:
            self.max_id.value = self.id.value
        self.__post_init__()

    def __post_init__(self):
        pass

    @classmethod
    def new(cls, **kwargs):
        kwargs['id'] = cls.max_id.value + 1
        result = cls(**kwargs)
        result.created = True
        return result

    def save(self):
        if self.created:
            insert(
                self.db_name.value,
                self.get_table_name(),
                tuple(field.name for field in self.fields),
                self.get_data()
            )
            self.created = False
        else:
            update_by_id(
                self.db_name.value,
                self.get_table_name(),
                self.id.value,
                tuple(field.name for field in self.fields if field.name != 'id'),
                self.get_data_without_id()
            )

    @classmethod
    def get_table_name(cls) -> str:
        return cls.__name__.lower() + 's'

    @classmethod
    def to_sql(cls):
        return '\n\t' + ',\n\t'.join(map(str, [DBModel.id] + cls.fields)) + '\n'

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
    def objects(cls):
        return dict()

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
        cls.db_name.value = db_name
        for vals in get(db_name, cls.get_table_name(), [f.name for f in cls.fields]):
            cls(**{field.name: val for field, val in zip(cls.fields, vals)})

    def get_data(self):
        return [getattr(self, field.name).to_sql() for field in self.fields]

    def get_data_without_id(self):
        return [getattr(self, field.name).to_sql() for field in self.fields if field.name != 'id']
