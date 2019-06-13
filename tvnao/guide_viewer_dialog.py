# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'guide_viewer_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_GuideViewerDialog(object):
    def setupUi(self, GuideViewerDialog):
        GuideViewerDialog.setObjectName("GuideViewerDialog")
        GuideViewerDialog.resize(420, 534)
        icon = QtGui.QIcon.fromTheme("view-calendar-list")
        GuideViewerDialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(GuideViewerDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox = QtWidgets.QComboBox(GuideViewerDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setEditable(False)
        self.comboBox.setCurrentText("")
        self.comboBox.setFrame(True)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout.addWidget(self.comboBox)
        self.prevButton = QtWidgets.QPushButton(GuideViewerDialog)
        icon = QtGui.QIcon.fromTheme("go-previous")
        self.prevButton.setIcon(icon)
        self.prevButton.setObjectName("prevButton")
        self.horizontalLayout.addWidget(self.prevButton)
        self.nextButton = QtWidgets.QPushButton(GuideViewerDialog)
        icon = QtGui.QIcon.fromTheme("go-next")
        self.nextButton.setIcon(icon)
        self.nextButton.setObjectName("nextButton")
        self.horizontalLayout.addWidget(self.nextButton)
        self.dateEdit = QtWidgets.QDateEdit(GuideViewerDialog)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setObjectName("dateEdit")
        self.horizontalLayout.addWidget(self.dateEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.textBrowser = QtWidgets.QTextBrowser(GuideViewerDialog)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.buttonBox = QtWidgets.QDialogButtonBox(GuideViewerDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(GuideViewerDialog)
        self.buttonBox.clicked['QAbstractButton*'].connect(GuideViewerDialog.close)
        QtCore.QMetaObject.connectSlotsByName(GuideViewerDialog)

    def retranslateUi(self, GuideViewerDialog):
        _translate = QtCore.QCoreApplication.translate
        GuideViewerDialog.setWindowTitle(_translate("GuideViewerDialog", "Guide Viewer"))
        GuideViewerDialog.setStatusTip(_translate("GuideViewerDialog", "M"))
        self.prevButton.setText(_translate("GuideViewerDialog", "&Prev"))
        self.nextButton.setText(_translate("GuideViewerDialog", "&Next"))
        self.dateEdit.setDisplayFormat(_translate("GuideViewerDialog", "ddd d.MM.yy"))


