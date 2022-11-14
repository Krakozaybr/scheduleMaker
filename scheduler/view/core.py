import os.path

from PIL.ImageQt import QImage
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QDialog,
    QDialogButtonBox,
    QAbstractButton,
    QBoxLayout,
)

from scheduler.config import IMAGES_DIR


def put_in_layout(item, layout):
    if isinstance(item, QBoxLayout):
        layout.addItem(item)
    else:
        layout.addWidget(item)


class ImageDialog(QDialog):
    def __init__(self, parent, pixmap):
        super().__init__(parent)
        self.setWindowTitle("Изображение")
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
        if k:
            w, h = int(w / k), int(h / k)
        self.setFixedSize(w, h)

    def sizeHint(self):
        return self.pixmap.size()

    def set_image(self, image_name):
        image = QImage(os.path.join(IMAGES_DIR, image_name))
        self.pixmap = QPixmap.fromImage(image)
        self.repaint()


class MessageDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Сообщение")
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
        self.setWindowTitle("Ошибка")

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
        self.setWindowTitle("Подтвердить действие")
        self.confirmed = False

    def accept(self):
        self.confirmed = True
        super().accept()

    def get_content(self):
        return QLabel("Вы уверены?")

    def get_button_box(self):
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        return self.buttonBox
