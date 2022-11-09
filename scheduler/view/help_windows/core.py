import os.path

from PIL.ImageQt import QImage
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QMainWindow, QScrollArea, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QDialog, \
    QDialogButtonBox, QFormLayout, QAbstractButton, QButtonGroup, QRadioButton, QCheckBox

from scheduler.config import IMAGES_DIR


def modelize(obj, model):
    obj.model = model
    return obj


class ImageDialog(QDialog):
    def __init__(self, parent, pixmap):
        super().__init__(parent)
        self.setWindowTitle('Изображение')
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        layout = QVBoxLayout(self)
        label = QLabel(self)
        label.setPixmap(pixmap)
        layout.addWidget(label)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    @staticmethod
    def from_image_name(parent, name):
        image = QImage(os.path.join(IMAGES_DIR, name))
        return ImageDialog(parent, QPixmap.fromImage(image))


class PicButton(QAbstractButton):
    def __init__(self, parent, image_name):
        super(PicButton, self).__init__(parent)
        self.parent_view = parent
        self.set_image(image_name)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()

    def set_image(self, image_name):
        image = QImage(os.path.join(IMAGES_DIR, image_name))
        self.pixmap = QPixmap.fromImage(image)
        self.repaint()


class EditModelDialog(QDialog):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle('Изменить ' + str(model))
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.container = QFormLayout(self)

        self.get_value_funcs = dict()

        for field in model.fields:
            name = field.name
            value = getattr(model, name)
            widget, func = field.get_widget_for_edit(self, value)
            self.get_value_funcs[field.name] = func
            self.container.addRow(field.russian_name, widget)
        self.container.addWidget(self.buttonBox)
        self.setLayout(self.container)

    def accept(self):
        super().accept()
        for field in self.model.fields:
            if not field.read_only:
                setattr(self.model, field.name, self.get_value_funcs[field.name]())
        self.model.save()
        if hasattr(self.parent(), 'updateModelInfo'):
            self.parent().updateModelInfo(self.model)


class InfoModelDialog(QDialog):
    def __init__(self, parent, model):
        super().__init__(parent)

        self.setWindowTitle('Информация о ' + str(model))
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.container = QFormLayout(self)
        for field in model.fields:
            name = field.name
            value = getattr(model, name)
            widget = field.get_widget_for_info(self, value)
            self.container.addRow(field.russian_name, widget)
        self.container.addWidget(self.buttonBox)
        self.setLayout(self.container)


def get_model_holder(context, model, editable):
    def show_more():
        if editable:
            EditModelDialog(context, model).exec()
        else:
            InfoModelDialog(context, model).exec()

    id_widget = modelize(QLabel(str(model.id), context), model)
    id_widget.setFixedWidth(50)
    name_widget = modelize(QLabel(str(model), context), model)
    name_widget.setFixedWidth(120)
    more_btn = modelize(QPushButton('Подробнее', context), model)
    more_btn.clicked.connect(show_more)
    container = QHBoxLayout(context)

    container.addWidget(id_widget)
    container.addWidget(name_widget)
    container.addWidget(more_btn)

    return container, lambda: name_widget.setText(str(model))


class EditModelListWindow(QMainWindow):
    def __init__(self, objects, name):
        super().__init__()
        self.objects = objects
        self.funcs_for_update = dict()
        self.name = name
        self.setupUI()

    def updateModelInfo(self, model):
        self.funcs_for_update[model.id]()

    def setupUI(self):
        self.setWindowTitle(self.name)
        self.setFixedSize(300, 300)
        self.container = QVBoxLayout(self)
        central_widget = QWidget()
        scroll = QScrollArea(self)

        for obj in sorted(self.objects.values(), key=lambda x: x.id):
            self.container.addItem(self.get_row(obj))

        self.container.setAlignment(Qt.AlignTop)

        central_widget.setLayout(self.container)

        scroll.setWidget(central_widget)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setCentralWidget(scroll)

    def get_row(self, obj):
        item, func = get_model_holder(self, obj, True)
        self.funcs_for_update[obj.id] = func
        return item


class ModelListDialog(QDialog):
    def __init__(self, parent, objects):
        super().__init__(parent)
        self.objects = objects

    def exec(self):
        self.setupUI()
        return super().exec()

    def setupUI(self):
        self.setWindowTitle('Список объектов')
        self.setFixedSize(300, 300)
        container = QVBoxLayout(self)
        central_widget = QWidget()
        scroll = QScrollArea(self)

        for obj in sorted(self.objects.values(), key=lambda x: x.id):
            container.addItem(self.get_row(obj))

        container.setAlignment(Qt.AlignTop)

        central_widget.setLayout(container)

        scroll.setWidget(central_widget)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        layout.addWidget(self.get_button_box())
        self.setLayout(layout)

    def get_button_box(self):
        QBtn = QDialogButtonBox.Ok
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        return buttonBox

    def get_row(self, obj):
        return QLabel(str(obj), self)


class InfoModelListDialog(ModelListDialog):
    def __init__(self, parent, objects):
        super().__init__(parent, objects)

    def get_row(self, obj):
        return get_model_holder(self, obj, False)


class SelectOneModelListDialog(InfoModelListDialog):
    def __init__(self, parent, objects):
        super().__init__(parent, objects)
        self.btn_group = QButtonGroup(self)
        self.selected = None

    def get_row(self, obj):
        layout = QHBoxLayout(self)
        layout.addItem(super().get_row(obj))
        button = modelize(QRadioButton(self), obj)
        self.btn_group.addButton(button)
        layout.addWidget(button)
        return layout

    def get_button_box(self):
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        return buttonBox

    def accept(self):
        for btn in self.btn_group.buttons():
            if btn.isChecked():
                self.selected = btn.model
                break
        super().accept()

    def get_selected(self):
        return self.selected


class SelectManyModelListDialog(SelectOneModelListDialog):
    def get_row(self, obj):
        layout = QHBoxLayout(self)
        layout.addItem(super().get_row(obj))
        button = modelize(QCheckBox(self), obj)
        self.btn_group.addButton(button)
        layout.addWidget(button)
        return layout

    def accept(self):
        self.selected = []
        for btn in self.btn_group.buttons():
            if btn.isChecked():
                self.selected.append(btn.model)
        super().accept()
