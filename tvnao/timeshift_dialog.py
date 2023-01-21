# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'timeshift_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TimeshiftDialog(object):
    def setupUi(self, TimeshiftDialog):
        TimeshiftDialog.setObjectName("TimeshiftDialog")
        TimeshiftDialog.resize(579, 672)
        self.gridLayout_2 = QtWidgets.QGridLayout(TimeshiftDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.audioSpinBox = QtWidgets.QSpinBox(TimeshiftDialog)
        self.audioSpinBox.setMinimum(1)
        self.audioSpinBox.setProperty("value", 1)
        self.audioSpinBox.setObjectName("audioSpinBox")
        self.gridLayout_2.addWidget(self.audioSpinBox, 2, 3, 1, 1)
        self.audioLabel = QtWidgets.QLabel(TimeshiftDialog)
        self.audioLabel.setObjectName("audioLabel")
        self.gridLayout_2.addWidget(self.audioLabel, 2, 1, 1, 2)
        self.dateEdit = QtWidgets.QDateEdit(TimeshiftDialog)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName("dateEdit")
        self.gridLayout_2.addWidget(self.dateEdit, 4, 3, 1, 1)
        self.hostLabel = QtWidgets.QLabel(TimeshiftDialog)
        self.hostLabel.setObjectName("hostLabel")
        self.gridLayout_2.addWidget(self.hostLabel, 0, 1, 1, 2)
        self.buttonBox = QtWidgets.QDialogButtonBox(TimeshiftDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 6, 2, 1, 2)
        self.prevButton = QtWidgets.QPushButton(TimeshiftDialog)
        self.prevButton.setObjectName("prevButton")
        self.gridLayout_2.addWidget(self.prevButton, 4, 1, 1, 1)
        self.listWidget = QtWidgets.QListWidget(TimeshiftDialog)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout_2.addWidget(self.listWidget, 5, 1, 1, 3)
        self.portLabel = QtWidgets.QLabel(TimeshiftDialog)
        self.portLabel.setObjectName("portLabel")
        self.gridLayout_2.addWidget(self.portLabel, 0, 3, 1, 1)
        self.nextButton = QtWidgets.QPushButton(TimeshiftDialog)
        self.nextButton.setObjectName("nextButton")
        self.gridLayout_2.addWidget(self.nextButton, 4, 2, 1, 1)
        self.hostEdit = QtWidgets.QLineEdit(TimeshiftDialog)
        self.hostEdit.setObjectName("hostEdit")
        self.gridLayout_2.addWidget(self.hostEdit, 1, 1, 1, 2)
        self.portEdit = QtWidgets.QLineEdit(TimeshiftDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.portEdit.sizePolicy().hasHeightForWidth())
        self.portEdit.setSizePolicy(sizePolicy)
        self.portEdit.setObjectName("portEdit")
        self.gridLayout_2.addWidget(self.portEdit, 1, 3, 1, 1)
        self.channelEdit = QtWidgets.QLineEdit(TimeshiftDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.channelEdit.sizePolicy().hasHeightForWidth())
        self.channelEdit.setSizePolicy(sizePolicy)
        self.channelEdit.setObjectName("channelEdit")
        self.gridLayout_2.addWidget(self.channelEdit, 3, 3, 1, 1)
        self.label = QtWidgets.QLabel(TimeshiftDialog)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 3, 1, 1, 2)

        self.retranslateUi(TimeshiftDialog)
        self.buttonBox.accepted.connect(TimeshiftDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(TimeshiftDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(TimeshiftDialog)

    def retranslateUi(self, TimeshiftDialog):
        _translate = QtCore.QCoreApplication.translate
        TimeshiftDialog.setWindowTitle(_translate("TimeshiftDialog", "Dialog"))
        self.audioLabel.setText(_translate("TimeshiftDialog", "Audio Channel:"))
        self.dateEdit.setDisplayFormat(_translate("TimeshiftDialog", "ddd d.MM.yy"))
        self.hostLabel.setText(_translate("TimeshiftDialog", "Host:"))
        self.prevButton.setText(_translate("TimeshiftDialog", "Prev"))
        self.portLabel.setText(_translate("TimeshiftDialog", "Port:"))
        self.nextButton.setText(_translate("TimeshiftDialog", "Next"))
        self.label.setText(_translate("TimeshiftDialog", "Channel ID Replacement:"))
