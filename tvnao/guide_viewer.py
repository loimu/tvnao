# Copyright (c) 2016-2025 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QSettings, pyqtSlot

from .guide_viewer_dialog import Ui_GuideViewerDialog


class GuideViewer(QtWidgets.QDialog):

    def __init__(self, parent, sh, channel_list, channelname):
        super(GuideViewer, self).__init__(parent)
        self.ui = Ui_GuideViewerDialog()
        self.ui.setupUi(self)
        self.sh = sh
        self.channels = []
        self.ui.comboBox.addItem("Overview")
        self.channels.append(None)
        for name, id in channel_list:
            if id not in self.channels:
                self.ui.comboBox.addItem(name)
                self.channels.append(id)
        self.ui.comboBox.setCurrentText(channelname)
        self.ui.comboBox.currentIndexChanged.connect(self.show_guide)
        self.ui.prevButton.released.connect(lambda: self.step(-1))
        self.ui.nextButton.released.connect(lambda: self.step(1))
        self.ui.dateEdit.dateChanged.connect(self.show_guide)
        self.ui.dateEdit.setDate(QtCore.QDate().currentDate())
        refresh_action = QtGui.QAction(self)
        refresh_action.setShortcut('Ctrl+R')
        refresh_action.triggered.connect(self.show_guide)
        self.addAction(refresh_action)

    def reset_handler(self, sh):
        self.sh = sh
        self.show_guide()

    def step(self, day):
        self.ui.dateEdit.setDate(self.ui.dateEdit.date().addDays(day))

    def show_guide(self):
        index = self.ui.comboBox.currentIndex()
        if index > -1 and self.sh:
            if self.channels[index]:
                date = self.ui.dateEdit.date().toString("yyyyMMdd")
                text = self.sh.get_schedule(date, self.channels[index], True)
                self.ui.textBrowser.setText(text)
            else:
                channel_map = {}
                for index, channel in enumerate(self.channels):
                    channel_map[channel] = self.ui.comboBox.itemText(index)
                self.ui.textBrowser.setText(self.sh.get_overview(channel_map))
