import json
import os.path
import shutil
from typing import Iterable
from scheduler.config import IMAGES_DIR
from scheduler.view.help_windows.core import PicButton, ImageDialog, InfoModelDialog, SelectOneModelListDialog
from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QLabel, QLineEdit, QTextEdit, QVBoxLayout, QPushButton, QFileDialog


class Field:
    def __init__(self,
                 name,
                 field_type,
                 default=None,
                 primary_key=False,
                 autoincrement=False,
                 read_only=False,
                 russian_name=''):
        self.name = name
        self.modifiers = []
        self.field_type = field_type
        self.read_only = read_only
        self.russian_name = russian_name
        if not russian_name:
            self.russian_name = name
        if primary_key:
            self.modifiers.append('PRIMARY KEY')
        if autoincrement:
            self.modifiers.append('AUTOINCREMENT')
        if default is not None:
            self.modifiers.append(f'DEFAULT {default}')

    def __str__(self):
        modifiers = ' '.join(self.modifiers)
        if modifiers:
            return ' '.join([self.name, self.field_type, modifiers])
        return ' '.join([self.name, self.field_type])

    def create_holder(self, *args, **kwargs):
        kwargs['parent'] = self
        return self.__class__.ObjectHolder(*args, **kwargs)

    def get_widget_for_edit(self, context, value):
        return QLabel(str(value), context), lambda: None

    def get_widget_for_info(self, context, value):
        return QLabel(str(value), context)

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

    def get_widget_for_edit(self, context, value):
        if not self.read_only:
            widget = QLineEdit(str(value), context)
            widget.setValidator(QRegExp("[0-9]{30}"))
            return widget, widget.text
        return super().get_widget_for_edit(context, value)

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

    def get_widget_for_edit(self, context, value):
        if not self.read_only:
            edit = QTextEdit(str(value), context)
            return edit, edit.toPlainText
        return super().get_widget_for_edit(context, value)

    class ObjectHolder(Field.ObjectHolder):
        def __init__(self, val, parent):
            if not isinstance(val, str):
                raise TypeError(f'Value must be str. Not <{type(val).__name__}>')
            super().__init__(val, parent)


class ImageField(StringField):

    image_size = 300

    def get_widget_for_edit(self, context, value):
        if not self.read_only:
            container = QVBoxLayout(context)
            img = PicButton(context, value)
            img.clicked.connect(lambda: self.show_img(context, label.text()))
            w, h = img.pixmap.width(), img.pixmap.height()
            k = max(w, h) / ImageField.image_size
            w, h = int(w / k), int(h / k)
            img.setFixedSize(w, h)
            label = QLabel(value, context)

            load_btn = QPushButton('Загрузить', context)
            load_btn.clicked.connect(lambda: self.load_img(context, label, img))

            container.addWidget(label)
            container.addWidget(img)
            container.addWidget(load_btn)
            return container, label.text
        return super().get_widget_for_edit(context, value)

    def get_widget_for_info(self, context, value):
        container = QVBoxLayout(context)
        img = PicButton(context, value)
        img.clicked.connect(lambda: self.show_img(context, label.text()))
        label = QLabel(value, context)
        container.addWidget(label)
        container.addWidget(img)
        return container

    @staticmethod
    def load_img(context, label, img):
        way = QFileDialog.getOpenFileName(
            context, 'Выбрать файл', '', 'Файл (*.jpg);;Файл (*.png);;Файл (*.jpeg)'
        )[0]
        name = os.path.basename(way)
        dest = os.path.join(IMAGES_DIR, name)
        shutil.copyfile(way, dest)
        label.setText(name)
        img.set_image(name)

    @staticmethod
    def show_img(context, name):
        ImageDialog.from_image_name(context, name).exec()


class ForeignField(Field):
    def __init__(self, name: str, foreign_cls, **kwargs):
        super().__init__(name, 'INTEGER', **kwargs)
        self.manager = foreign_cls.objects
        self.foreign_cls = foreign_cls

    def get_widget_for_edit(self, context, value):
        if not self.read_only:
            layout = QVBoxLayout(context)
            label = QLabel(str(value), context)
            info_btn = QPushButton('Подробнее', context)
            edit_btn = QPushButton('Изменить', context)

            layout.addWidget(label)
            layout.addWidget(info_btn)
            layout.addWidget(edit_btn)

            holder = Field.ObjectHolder(value)

            info_btn.clicked.connect(lambda: self.show_info(context, holder))
            edit_btn.clicked.connect(lambda: self.edit_model(context, label, holder))
            return layout, lambda: holder.value
        return super().get_widget_for_edit(context, value)

    @staticmethod
    def show_info(context, holder):
        InfoModelDialog(context, holder.value).exec()

    @staticmethod
    def edit_model(context, label, holder):
        dialog = SelectOneModelListDialog(context, holder.value.__class__.objects)
        dialog.exec()
        selected = dialog.get_selected()
        if selected:
            label.setText(str(selected))
            holder.value = selected

    class ObjectHolder(Field.ObjectHolder):
        def __init__(self, foreign_obj, parent):
            if isinstance(foreign_obj, int):
                super().__init__(parent.manager[int(foreign_obj)], parent)
            else:
                super().__init__(foreign_obj, parent)

        def to_sql(self):
            return self._value.id


class ListField(Field):
    def __init__(self, name: str, foreign_cls, list_item_type=Field, **kwargs):
        super().__init__(name, 'TEXT', **kwargs)
        self.manager = foreign_cls.objects
        self.foreign_cls = foreign_cls
        self.list_item_type = list_item_type

    def get_widget_for_edit(self, context, value):
        # It`s unused, so I decided to pass it
        if not self.read_only:
            ...
        return super().get_widget_for_edit(context, value)

    def get_widget_for_info(self, context, value):
        return QLabel(value, context)

    class ObjectHolder(Field.ObjectHolder):
        def __init__(self, holders, parent):
            if not isinstance(holders, Iterable):
                raise TypeError('Value "holders" must be iterable')

            if isinstance(holders, str):
                holders = [parent.list_item_type(parent.manager.get(i) for i in json.loads(holders))]
            elif all(isinstance(i, int) for i in holders):
                holders = [parent.list_item_type(parent.manager.get(i)) for i in holders]
            elif any(not isinstance(i, parent.foreign_cls) for i in holders):
                raise TypeError(f'Holders are neither list of str, int or {parent.foreign_cls.__name__}')

            if not any(isinstance(i, Field.ObjectHolder) for i in holders):
                raise TypeError('ObjectHolder objects are required')

            super().__init__(holders, parent)

        def to_sql(self):
            return f'"{json.dumps([i.to_sql() for i in self.holders])}"'
