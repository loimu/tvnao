# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tvnao/settings_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 492)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.playlistHost = QtWidgets.QLineEdit(self.groupBox)
        self.playlistHost.setObjectName("playlistHost")
        self.horizontalLayout.addWidget(self.playlistHost)
        self.playlistURL = QtWidgets.QLineEdit(self.groupBox)
        self.playlistURL.setObjectName("playlistURL")
        self.horizontalLayout.addWidget(self.playlistURL)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.playerPath = QtWidgets.QLineEdit(self.groupBox_2)
        self.playerPath.setObjectName("playerPath")
        self.horizontalLayout_5.addWidget(self.playerPath)
        self.playerOptions = QtWidgets.QLineEdit(self.groupBox_2)
        self.playerOptions.setObjectName("playerOptions")
        self.horizontalLayout_5.addWidget(self.playerOptions)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_6.addWidget(self.label_5)
        self.label_6 = QtWidgets.QLabel(self.groupBox_3)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_6.addWidget(self.label_6)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.epgHost = QtWidgets.QLineEdit(self.groupBox_3)
        self.epgHost.setObjectName("epgHost")
        self.horizontalLayout_7.addWidget(self.epgHost)
        self.epgIndex = QtWidgets.QLineEdit(self.groupBox_3)
        self.epgIndex.setObjectName("epgIndex")
        self.horizontalLayout_7.addWidget(self.epgIndex)
        self.verticalLayout_4.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_7 = QtWidgets.QLabel(self.groupBox_3)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_8.addWidget(self.label_7)
        self.epgURL = QtWidgets.QLineEdit(self.groupBox_3)
        self.epgURL.setObjectName("epgURL")
        self.horizontalLayout_8.addWidget(self.epgURL)
        self.verticalLayout_4.addLayout(self.horizontalLayout_8)
        self.label_8 = QtWidgets.QLabel(self.groupBox_3)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_4.addWidget(self.label_8)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.aliasPlaylist = QtWidgets.QLineEdit(self.groupBox_3)
        self.aliasPlaylist.setObjectName("aliasPlaylist")
        self.horizontalLayout_9.addWidget(self.aliasPlaylist)
        self.aliasGuide = QtWidgets.QLineEdit(self.groupBox_3)
        self.aliasGuide.setObjectName("aliasGuide")
        self.horizontalLayout_9.addWidget(self.aliasGuide)
        self.verticalLayout_4.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.tableAliases = QtWidgets.QTableWidget(self.groupBox_3)
        self.tableAliases.setTabKeyNavigation(False)
        self.tableAliases.setProperty("showDropIndicator", False)
        self.tableAliases.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableAliases.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableAliases.setColumnCount(2)
        self.tableAliases.setObjectName("tableAliases")
        self.tableAliases.setRowCount(0)
        self.tableAliases.horizontalHeader().setVisible(False)
        self.tableAliases.horizontalHeader().setCascadingSectionResizes(True)
        self.tableAliases.horizontalHeader().setDefaultSectionSize(130)
        self.tableAliases.horizontalHeader().setStretchLastSection(True)
        self.tableAliases.verticalHeader().setVisible(False)
        self.horizontalLayout_10.addWidget(self.tableAliases)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.aliasAddButton = QtWidgets.QPushButton(self.groupBox_3)
        self.aliasAddButton.setObjectName("aliasAddButton")
        self.verticalLayout_5.addWidget(self.aliasAddButton)
        self.aliasDelButton = QtWidgets.QPushButton(self.groupBox_3)
        self.aliasDelButton.setObjectName("aliasDelButton")
        self.verticalLayout_5.addWidget(self.aliasDelButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.horizontalLayout_10.addLayout(self.verticalLayout_5)
        self.verticalLayout_4.addLayout(self.horizontalLayout_10)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.errorLabel = QtWidgets.QLabel(Dialog)
        self.errorLabel.setText("")
        self.errorLabel.setObjectName("errorLabel")
        self.horizontalLayout_4.addWidget(self.errorLabel)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout_4.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "tvnao - settings"))
        self.groupBox.setTitle(_translate("Dialog", "Playlist"))
        self.label.setText(_translate("Dialog", "Playlist host:"))
        self.label_2.setText(_translate("Dialog", "Playlist URL:"))
        self.groupBox_2.setTitle(_translate("Dialog", "Player"))
        self.label_3.setText(_translate("Dialog", "Player:"))
        self.label_4.setText(_translate("Dialog", "Player options:"))
        self.groupBox_3.setTitle(_translate("Dialog", "Program Guide"))
        self.label_5.setText(_translate("Dialog", "EPG host:"))
        self.label_6.setText(_translate("Dialog", "EPG web page:"))
        self.label_7.setText(_translate("Dialog", "EPG URL:"))
        self.label_8.setText(_translate("Dialog", "Aliases:"))
        self.aliasPlaylist.setToolTip(_translate("Dialog", "channel name from playlist"))
        self.aliasPlaylist.setPlaceholderText(_translate("Dialog", "playlist"))
        self.aliasGuide.setToolTip(_translate("Dialog", "channel name from TV guide"))
        self.aliasGuide.setPlaceholderText(_translate("Dialog", "TV guide"))
        self.aliasAddButton.setToolTip(_translate("Dialog", "Connect channel name in playlist to a name in TV guide"))
        self.aliasAddButton.setText(_translate("Dialog", "Add"))
        self.aliasDelButton.setText(_translate("Dialog", "Delete"))

