import os.path

from PIL.ImageQt import QImage
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QMainWindow, QScrollArea, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QDialog, \
    QDialogButtonBox, QFormLayout, QAbstractButton, QButtonGroup, QRadioButton, QCheckBox, QFrame, QSizePolicy, \
    QBoxLayout, QInputDialog, QComboBox
import scheduler.config as config
from scheduler.config import IMAGES_DIR


def modelize(obj, model):
    obj.model = model
    return obj


def put_in_layout(item, layout):
    if isinstance(item, QBoxLayout):
        layout.addItem(item)
    else:
        layout.addWidget(item)


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
        r = event.rect()
        # PicButton could be painted with bugs, if we do not override w, h, x and y of rect
        r.setX(0)
        r.setY(0)
        r.setWidth(self.width())
        r.setHeight(self.height())
        painter.drawPixmap(r, self.pixmap)

    def set_max_dimension(self, value):
        w, h = self.pixmap.width(), self.pixmap.height()
        k = max(w, h) / value
        w, h = int(w / k), int(h / k)
        self.setFixedSize(w, h)

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
            widget, func = field.get_widget_for_change(self, value)
            self.get_value_funcs[field.name] = func
            self.container.addRow(field.russian_name, widget)
        self.container.addWidget(self.buttonBox)
        self.setLayout(self.container)
        self.adjustSize()
        self.setFixedSize(self.size())

    def accept(self):
        super().accept()
        for field in self.model.fields:
            if not field.read_only:
                setattr(self.model, field.name, self.get_value_funcs[field.name]())
        self.model.save()
        if hasattr(self.parent(), 'update_model_info'):
            self.parent().update_model_info(self.model)


class CreateModelDialog(QDialog):
    def __init__(self, parent, cls):
        super().__init__(parent)
        self.cls = cls

        self.setWindowTitle('Создать ' + cls.__name__)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.container = QFormLayout(self)

        self.get_value_funcs = dict()

        for field in cls.fields:
            if field.name == 'id':
                continue
            widget, func = field.get_widget_for_change(self, None)
            self.get_value_funcs[field.name] = func
            self.container.addRow(field.russian_name, widget)

        self.container.addWidget(self.buttonBox)
        self.setLayout(self.container)

    def accept(self):
        kwargs = dict()
        for field in self.cls.fields:
            if not field.read_only:
                val = self.get_value_funcs[field.name]()
                if field.check_val(val):
                    kwargs[field.name] = val
                else:
                    ErrorDialog(self, 'Не все поля заполнены').exec()
                    return
        model = self.cls.new(**kwargs)
        super().accept()
        if hasattr(self.parent(), 'add_model'):
            self.parent().add_model(model)


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


class MessageDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Сообщение')
        layout = QVBoxLayout()

        content = self.get_content()
        if content:
            put_in_layout(content, layout)

        button_box = self.get_button_box()
        if button_box:
            layout.addWidget(button_box)

        self.setLayout(layout)
        self.adjustSize()
        self.setFixedSize(self.size())

    def get_content(self):
        return None

    def get_button_box(self):
        return None


class ErrorDialog(MessageDialog):
    def __init__(self, parent, text):
        self.text = text
        super().__init__(parent)
        self.setWindowTitle('Ошибка')

    def get_content(self):
        return QLabel(self.text)

    def get_button_box(self):
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        return self.buttonBox


class ConfirmDialog(MessageDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Подтвердить действие')
        self.confirmed = False

    def accept(self):
        self.confirmed = True
        super().accept()

    def get_content(self):
        return QLabel('Вы уверены?')

    def get_button_box(self):
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        return self.buttonBox


class ModelHolder(QWidget):
    def __init__(self, parent, model):
        super().__init__()
        self.p = parent
        self.model = model
        self.setupUI()

    def setupUI(self):
        self.id_widget = QLabel(str(self.model.id))
        self.id_widget.setFixedWidth(50)
        self.name_widget = QLabel(str(self.model))
        self.name_widget.setFixedWidth(120)
        self.more_btn = QPushButton('Подробнее')
        self.more_btn.clicked.connect(self.show_more)
        self.container = QHBoxLayout()

        self.container.addWidget(self.id_widget)
        self.container.addWidget(self.name_widget)
        self.container.addWidget(self.more_btn)

        self.setLayout(self.container)

    def show_more(self):
        InfoModelDialog(self.p, self.model).exec()


class EditableModelHolder(ModelHolder):

    def setupUI(self):
        super().setupUI()
        self.delete_btn = PicButton(self.p, config.DELETE_IMG)
        self.delete_btn.clicked.connect(self.delete)
        self.edit_btn = PicButton(self.p, config.EDIT_IMG)
        self.edit_btn.clicked.connect(self.edit)

        self.container.addWidget(self.delete_btn)
        self.container.addWidget(self.edit_btn)

    def edit(self):
        EditModelDialog(self.p, self.model).exec()
        self.update_text()

    def delete(self):
        d = ConfirmDialog(self.p)
        d.exec()
        if d.confirmed:
            self.model.delete()
            self.p.remove_holder(self)

    def update_text(self):
        self.name_widget.setText(str(self.model))


class ChoosableModelHolder(ModelHolder):
    choose_class = None

    def __init__(self, parent, model, button_group):
        self.button_group = button_group
        super().__init__(parent, model)

    def setupUI(self):
        super().setupUI()
        self.btn = self.__class__.choose_class(self.p)
        self.button_group.addButton(self.btn)
        self.container.addWidget(self.btn)

    def is_checked(self):
        return self.btn.isChecked()


class RadioModelHolder(ChoosableModelHolder):
    choose_class = QRadioButton


class CheckboxModelHolder(ChoosableModelHolder):
    choose_class = QCheckBox


class ModelListDialog(QDialog):
    def __init__(self, parent, objects, name):
        super().__init__(parent)

        self.scroll = QScrollArea()
        self.scroll_widget = QWidget()
        self.objects_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.objects_layout)
        self.scroll.setWidget(self.scroll_widget)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.objects = objects
        self.name = name
        self.holders = dict()

    def exec(self):
        self.setupUI()
        return super().exec()

    def setupUI(self):
        self.setWindowTitle(self.name)
        self.update_objects()
        self.setFixedSize(410, 400)

        container = QVBoxLayout()
        btns = self.get_button_box()

        for item in self.get_header_widgets():
            put_in_layout(item, container)

        container.setAlignment(Qt.AlignTop)
        container.addWidget(self.scroll)

        if btns:
            container.addWidget(btns)
        self.setLayout(container)

    def update_objects(self):
        self.scroll.setParent(None)
        for i in reversed(range(self.objects_layout.count())):
            self.objects_layout.itemAt(i).widget().setParent(None)
        for obj in sorted(self.objects.values(), key=lambda x: x.id):
            put_in_layout(self.get_row(obj), self.objects_layout)  # addWidget просто
        self.scroll_widget.adjustSize()
        print(self.objects_layout.count())
        if self.layout():
            self.layout().addWidget(self.scroll)

    def get_header_widgets(self):
        return []

    def get_button_box(self):
        QBtn = QDialogButtonBox.Ok
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        return buttonBox

    def get_row(self, obj):
        return QLabel(str(obj), self)


class EditListDialog(ModelListDialog):
    def __init__(self, parent, classes):
        super().__init__(parent, classes[0].objects, 'Редактировать базы данных')

        assert len(classes) > 0

        self.classes = classes
        self.indexes = {cls.plural_class_name: i for i, cls in enumerate(classes)}
        self.current_cls = classes[0]
        self.holders = dict()

    def remove_holder(self, model_holder):
        self.layout().removeWidget(model_holder)

    def get_header_widgets(self):
        layout = QHBoxLayout()
        self.select_class = QComboBox()
        for cls in self.classes:
            self.select_class.addItem(cls.plural_class_name, cls)
        new_model_btn = QPushButton('Создать')
        new_model_btn.clicked.connect(self.create_model)
        layout.addWidget(self.select_class)
        layout.addWidget(new_model_btn)

        self.select_class.currentTextChanged.connect(self.change_objects)

        return [layout]

    def change_objects(self, ev):
        self.current_cls = self.classes[self.indexes[ev]]
        self.objects = self.current_cls.objects
        self.update_objects()

    def create_model(self):
        CreateModelDialog(self.parent(), self.current_cls).exec()

    def update_model_info(self, model):
        self.holders[model.id].update_text()

    def add_model(self, model):
        self.layout().addWidget(self.get_row(model))

    def get_row(self, obj):
        self.holders[obj.id] = EditableModelHolder(self, obj)
        return self.holders[obj.id]

    def get_button_box(self):
        return None


class InfoModelListDialog(ModelListDialog):
    def __init__(self, parent, objects, name='Список объектов'):
        super().__init__(parent, objects, name)

    def get_row(self, obj):
        self.holders[obj.id] = ModelHolder(self, obj)
        return self.holders[obj.id]


class SelectOneModelListDialog(InfoModelListDialog):
    def __init__(self, parent, objects, name='Выбрать элемент'):
        super().__init__(parent, objects, name)
        self.btn_group = QButtonGroup()
        self.selected = None

    def get_row(self, obj):
        self.holders[obj.id] = RadioModelHolder(self, obj, self.btn_group)
        return self.holders[obj.id]

    def get_button_box(self):
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        return buttonBox

    def accept(self):
        for holder in self.holders.values():
            if holder.is_checked():
                self.selected = holder.model
                break
        super().accept()

    def get_selected(self):
        return self.selected


class SelectManyModelListDialog(SelectOneModelListDialog):
    def __init__(self, parent, objects, name='Выбрать элементы'):
        super().__init__(parent, objects, name)
        self.selected = []

    def get_row(self, obj):
        self.holders[obj.id] = CheckboxModelHolder(self, obj, self.btn_group)
        return self.holders[obj.id]

    def accept(self):
        self.selected = []
        for holder in self.holders.values():
            if holder.is_checked():
                self.selected.append(holder.model)
        super().accept()
