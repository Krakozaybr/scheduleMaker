# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'schedule_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(720, 570)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_6.addWidget(self.label_3)
        self.currentScheduleLabel = QtWidgets.QLabel(Dialog)
        self.currentScheduleLabel.setObjectName("currentScheduleLabel")
        self.horizontalLayout_6.addWidget(self.currentScheduleLabel)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_6)
        self.selectScheduleBtn = QtWidgets.QPushButton(Dialog)
        self.selectScheduleBtn.setObjectName("selectScheduleBtn")
        self.horizontalLayout_5.addWidget(self.selectScheduleBtn)
        self.exportBtn = QtWidgets.QPushButton(Dialog)
        self.exportBtn.setObjectName("exportBtn")
        self.horizontalLayout_5.addWidget(self.exportBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.groupSelect = QtWidgets.QComboBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupSelect.sizePolicy().hasHeightForWidth())
        self.groupSelect.setSizePolicy(sizePolicy)
        self.groupSelect.setObjectName("groupSelect")
        self.horizontalLayout.addWidget(self.groupSelect)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.scheduleSpace = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scheduleSpace.sizePolicy().hasHeightForWidth()
        )
        self.scheduleSpace.setSizePolicy(sizePolicy)
        self.scheduleSpace.setObjectName("scheduleSpace")
        self.verticalLayout.addWidget(self.scheduleSpace)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Составить расписание"))
        self.label_3.setText(_translate("Dialog", "Текущий шаблон:"))
        self.currentScheduleLabel.setText(_translate("Dialog", "---"))
        self.selectScheduleBtn.setText(_translate("Dialog", "Выбрать шаблон"))
        self.exportBtn.setText(_translate("Dialog", "Экспорт"))
        self.label.setText(_translate("Dialog", "Класс:"))
