# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tvnao/tvnao_widget.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(325, 700)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listWidget = QtWidgets.QListWidget(Form)
        self.listWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.guideBrowser = QtWidgets.QTextBrowser(Form)
        self.guideBrowser.setMaximumSize(QtCore.QSize(16777215, 150))
        self.guideBrowser.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.guideBrowser.setFrameShadow(QtWidgets.QFrame.Plain)
        self.guideBrowser.setLineWidth(1)
        self.guideBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.guideBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.guideBrowser.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.guideBrowser.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.guideBrowser.setOpenLinks(False)
        self.guideBrowser.setObjectName("guideBrowser")
        self.verticalLayout.addWidget(self.guideBrowser)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.guideFullButton = QtWidgets.QPushButton(Form)
        self.guideFullButton.setCheckable(True)
        self.guideFullButton.setObjectName("guideFullButton")
        self.horizontalLayout_2.addWidget(self.guideFullButton)
        self.guideNextButton = QtWidgets.QPushButton(Form)
        self.guideNextButton.setCheckable(True)
        self.guideNextButton.setObjectName("guideNextButton")
        self.horizontalLayout_2.addWidget(self.guideNextButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEditFilter = QtWidgets.QLineEdit(Form)
        self.lineEditFilter.setClearButtonEnabled(True)
        self.lineEditFilter.setObjectName("lineEditFilter")
        self.horizontalLayout.addWidget(self.lineEditFilter)
        self.buttonMenu = QtWidgets.QPushButton(Form)
        self.buttonMenu.setObjectName("buttonMenu")
        self.horizontalLayout.addWidget(self.buttonMenu)
        self.buttonGo = QtWidgets.QPushButton(Form)
        self.buttonGo.setObjectName("buttonGo")
        self.horizontalLayout.addWidget(self.buttonGo)
        self.buttonGuide = QtWidgets.QPushButton(Form)
        self.buttonGuide.setMaximumSize(QtCore.QSize(30, 16777215))
        self.buttonGuide.setCheckable(True)
        self.buttonGuide.setObjectName("buttonGuide")
        self.horizontalLayout.addWidget(self.buttonGuide)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "tvnao"))
        self.guideFullButton.setText(_translate("Form", "Full"))
        self.guideNextButton.setText(_translate("Form", "Tomorrow"))
        self.lineEditFilter.setPlaceholderText(_translate("Form", "Filter ..."))
        self.buttonMenu.setText(_translate("Form", "&Menu"))
        self.buttonGo.setToolTip(_translate("Form", "Play selected channel"))
        self.buttonGo.setText(_translate("Form", "&Watch"))
        self.buttonGuide.setToolTip(_translate("Form", "Show TV guide (Ctrl+G)"))
        self.buttonGuide.setText(_translate("Form", "..."))


