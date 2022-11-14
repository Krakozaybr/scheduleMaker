import json
import os.path
import shutil
import string
import random
from typing import Iterable

from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import (
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QTextBrowser,
)

import scheduler.config as config
from scheduler.view.core import PicButton, ImageDialog, ErrorDialog
from scheduler.view.structure_interaction import (
    InfoModelDialog,
    SelectOneItemListDialog,
)


class Field:
    def __init__(
        self,
        name,
        field_type,
        default=None,
        primary_key=False,
        autoincrement=False,
        read_only=False,
        russian_name="",
    ):
        self.name = name
        self.modifiers = []
        self.field_type = field_type
        self.read_only = read_only
        self.russian_name = russian_name
        self.default = default
        if not russian_name:
            self.russian_name = name
        if primary_key:
            self.modifiers.append("PRIMARY KEY")
        if autoincrement:
            self.modifiers.append("AUTOINCREMENT")
        if default is not None:
            self.modifiers.append(f"DEFAULT {default}")

    # Help method for creating tables in dbs
    def __str__(self):
        modifiers = " ".join(self.modifiers)
        if modifiers:
            return " ".join([self.name, self.field_type, modifiers])
        return " ".join([self.name, self.field_type])

    # Returns ObjectHolder instance
    def create_holder(self, *args, **kwargs):
        kwargs["parent"] = self
        return self.__class__.ObjectHolder(*args, **kwargs)

    # Returns PyQT5 widgets that describe the field and could be changed
    def get_widget_for_change(self, context, value):
        return QLabel(str(value), context), lambda: None

    # Returns PyQT5 widgets that describe the field
    def get_widget_for_info(self, context, value):
        return QLabel(str(value), context)

    def check_val(self, val):
        return bool(val)

    # Wrapper for values
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
        super().__init__(name, "INTEGER", **kwargs)

    def get_widget_for_change(self, context, value):
        if not self.read_only:
            widget = QLineEdit("0" if value is None else str(value), context)
            widget.setValidator(QRegExp("[0-9]{30}"))
            return widget, widget.text
        return super().get_widget_for_change(context, value)

    def check_val(self, val):
        return isinstance(val, int)

    class ObjectHolder(Field.ObjectHolder):
        def __init__(self, val, parent):
            if not isinstance(val, int):
                raise TypeError("Value must be int")
            super().__init__(val, parent)

        def to_sql(self):
            return self._value


class StringField(Field):
    def __init__(self, name, **kwargs):
        super().__init__(name, "TEXT", **kwargs)

    def get_widget_for_change(self, context, value):
        if not self.read_only:
            edit = QTextEdit("" if value is None else str(value), context)
            return edit, edit.toPlainText
        return super().get_widget_for_change(context, value)

    def check_val(self, val):
        return isinstance(val, str)

    def get_widget_for_info(self, context, value):
        textBrowser = QTextBrowser(context)
        textBrowser.setText(str(value))
        textBrowser.setFixedWidth(200)
        textBrowser.adjustSize()
        return textBrowser

    class ObjectHolder(Field.ObjectHolder):
        def __init__(self, val, parent):
            if not isinstance(val, str):
                raise TypeError(f"Value must be str. Not <{type(val).__name__}>")
            super().__init__(val, parent)


def generate_random_string(n=16):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))


class ImageField(StringField):
    image_size = 300

    def get_widget_for_change(self, context, value):
        if not self.read_only:
            container = QVBoxLayout(context)

            image_name = Field.ObjectHolder(value)

            img = PicButton(
                context,
                value or self.default.replace("'", "") or config.DEFAULT_TEACHER_IMG,
            )
            img.clicked.connect(lambda: self.show_img(context, image_name.value))
            img.set_max_dimension(self.image_size)

            load_btn = QPushButton("Загрузить", context)
            load_btn.clicked.connect(lambda: self.load_img(context, image_name, img))

            container.addWidget(img)
            container.addWidget(load_btn)
            return container, lambda: image_name.value
        return super().get_widget_for_change(context, value)

    def get_widget_for_info(self, context, value):
        container = QVBoxLayout(context)
        img = PicButton(context, value)
        img.clicked.connect(lambda: self.show_img(context, value))
        img.set_max_dimension(self.image_size)
        container.addWidget(img)
        return container

    @staticmethod
    def load_img(context, holder, img):
        way = QFileDialog.getOpenFileName(
            context, "Выбрать файл", "", "Файл (*.jpg);;Файл (*.png);;Файл (*.jpeg)"
        )[0]
        if way:
            name = generate_random_string()
            while os.path.exists(os.path.join(config.IMAGES_DIR, name)):
                name = generate_random_string()
            dest = (
                os.path.join(config.IMAGES_DIR, name)
                + "."
                + os.path.basename(way).split(".")[-1]
            )
            shutil.copyfile(way, dest)
            holder.value = name
            img.set_image(name)

    @staticmethod
    def show_img(context, name):
        ImageDialog.from_image_name(context, name).exec()

    def check_val(self, val):
        return isinstance(val, str)


class ForeignField(Field):
    def __init__(self, name: str, foreign_cls, **kwargs):
        super().__init__(name, "INTEGER", **kwargs)
        self.manager = foreign_cls.objects
        self.foreign_cls = foreign_cls

    def get_widget_for_change(self, context, value):
        if not self.read_only:
            layout = QVBoxLayout(context)
            label = QLabel(str(value), context)
            info_btn = QPushButton("Подробнее", context)
            edit_btn = QPushButton("Изменить", context)

            layout.addWidget(label)
            layout.addWidget(info_btn)
            layout.addWidget(edit_btn)

            holder = Field.ObjectHolder(value)

            info_btn.clicked.connect(lambda: self.show_info(context, holder))
            edit_btn.clicked.connect(lambda: self.edit_model(context, label, holder))
            return layout, lambda: holder.value
        return super().get_widget_for_change(context, value)

    def get_widget_for_info(self, context, value):
        container = QVBoxLayout()
        more_btn = QPushButton("Подробнее")
        more_btn.clicked.connect(
            lambda: self.show_info(context, Field.ObjectHolder(value))
        )

        container.addWidget(QLabel(str(value), context))
        container.addWidget(more_btn)

        return container

    def check_val(self, val):
        return isinstance(val, self.foreign_cls)

    @staticmethod
    def show_info(context, holder):
        if holder.value is None or holder.value.id < 1:
            ErrorDialog(context, "Значение неопределено").exec()
        else:
            InfoModelDialog(context, holder.value).exec()

    def edit_model(self, context, label, holder):
        dialog = SelectOneItemListDialog(context, self.foreign_cls.objects)
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

        @property
        def value(self):
            if self._value.id in self._value.__class__.objects:
                return self._value
            return self._value.__class__.objects[-1]

        @value.setter
        def value(self, val):
            self._value = val


class ListField(Field):
    def __init__(self, name: str, foreign_cls, list_item_type=Field, **kwargs):
        super().__init__(name, "TEXT", **kwargs)
        self.manager = foreign_cls.objects
        self.foreign_cls = foreign_cls
        self.list_item_type = list_item_type

    def get_widget_for_change(self, context, value):
        # It`s unused, so I decided to pass it
        if not self.read_only:
            ...
        return super().get_widget_for_change(context, value)

    def get_widget_for_info(self, context, value):
        return QLabel(value, context)

    def check_val(self, val):
        return isinstance(val, Iterable) and all(
            isinstance(i, self.foreign_cls) for i in val
        )

    class ObjectHolder(Field.ObjectHolder):
        def __init__(self, holders, parent):
            if not isinstance(holders, Iterable):
                raise TypeError(f'Value "holders" must be iterable, not {holders}')
            if isinstance(holders, str):
                holders = [
                    parent.list_item_type.ObjectHolder(parent.manager[i], self)
                    for i in json.loads(holders)
                ]
            elif all(isinstance(i, int) for i in holders):
                holders = [
                    parent.list_item_type.ObjectHolder(parent.manager[i], self)
                    for i in holders
                ]

            elif all(
                isinstance(i, parent.foreign_cls) or (hasattr(i, "id") and i.id == -1)
                for i in holders
            ):
                holders = [parent.list_item_type.ObjectHolder(i, self) for i in holders]
            elif any(not isinstance(i, parent.foreign_cls) for i in holders):
                raise TypeError(
                    f"Holders are neither list of str, int or {parent.foreign_cls.__name__}"
                )

            if not any(isinstance(i, Field.ObjectHolder) for i in holders):
                raise TypeError("ObjectHolder objects are required")

            super().__init__(holders, parent)

        def to_sql(self):
            return f'"{json.dumps([i.to_sql() for i in self.value])}"'
