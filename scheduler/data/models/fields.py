import json
from typing import Iterable


class Field:
    def __init__(self,
                 name,
                 field_type,
                 default=None,
                 primary_key=False,
                 autoincrement=False):
        self.name = name
        self.modifiers = []
        self.field_type = field_type
        self.default = default
        if primary_key:
            self.modifiers.append('PRIMARY KEY')
        if autoincrement:
            self.modifiers.append('AUTOINCREMENT')

    def __str__(self):
        modifiers = ' '.join(self.modifiers)
        if modifiers:
            return ' '.join([self.name, self.field_type, modifiers])
        return ' '.join([self.name, self.field_type])

    def create_holder(self, *args, **kwargs):
        kwargs['parent'] = self
        return self.__class__.ObjectHolder(*args, **kwargs)

    class ObjectHolder:
        def __init__(self, obj, parent=None):
            self._value = obj
            self._parent = parent

        def __getattr__(self, item):
            return getattr(self._value, item)

        def to_sql(self):
            return str(self._value)

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, val):
            self._value = val

        def __str__(self):
            return str(self._value)


class IntegerField(Field):
    def __init__(self, name, **kwargs):
        super().__init__(name, 'INTEGER', **kwargs)

    class ObjectHolder(Field.ObjectHolder):
        def __init__(self, val, parent):
            if not isinstance(val, int):
                raise TypeError('Value must be int')
            super().__init__(val, parent)

        def to_sql(self):
            return self._value


class StringField(Field):
    def __init__(self, name, **kwargs):
        super().__init__(name, 'TEXT', **kwargs)

    class ObjectHolder(Field.ObjectHolder):
        def __init__(self, val, parent):
            if not isinstance(val, str):
                raise TypeError(f'Value must be str. Not <{type(val).__name__}>')
            super().__init__(val, parent)


class ForeignField(Field):
    def __init__(self, name: str, foreign_cls, **kwargs):
        super().__init__(name, 'INTEGER', **kwargs)
        self.manager = foreign_cls.objects
        self.foreign_cls = foreign_cls

    class ObjectHolder(Field.ObjectHolder):
        def __init__(self, foreign_obj_id, parent):
            super().__init__(parent.manager[int(foreign_obj_id)], parent)

        def to_sql(self):
            return self._value.id.value


class ListField(Field):
    def __init__(self, name: str, foreign_cls, list_item_type=Field, **kwargs):
        super().__init__(name, 'TEXT', **kwargs)
        self.manager = foreign_cls.objects
        self.foreign_cls = foreign_cls
        self.list_item_type = list_item_type

    class ObjectHolder(Field.ObjectHolder):
        def __init__(self, holders_ids_str, parent):
            holders_ids = json.loads(holders_ids_str)
            holders = [parent.list_item_type(parent.manager.get(i)) for i in holders_ids]
            if not isinstance(holders, Iterable):
                raise TypeError('Value "holders" must be iterable')
            if not any(isinstance(i, Field.ObjectHolder) for i in holders):
                raise TypeError('ObjectHolder objects are required')
            super().__init__(holders, parent)

        def to_sql(self):
            return f'"{json.dumps([i.to_sql() for i in self.holders])}"'
