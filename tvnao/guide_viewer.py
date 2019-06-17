# Copyright (c) 2016-2019 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QSettings, pyqtSlot
from .guide_viewer_dialog import Ui_GuideViewerDialog


class GuideViewer(QtWidgets.QDialog):

    def __init__(self, parent, sh, channel_list, channelname):
        super(GuideViewer, self).__init__(parent)
        self.ui = Ui_GuideViewerDialog()
        self.ui.setupUi(self)
        self.sh = sh
        self.channels = []
        for item in channel_list:
            if item[2] and item[2] not in self.channels:
                self.ui.comboBox.addItem(item[0])
                self.channels.append(item[2])
        self.ui.comboBox.setCurrentText(channelname)
        self.ui.comboBox.currentIndexChanged.connect(self.show_guide)
        self.ui.prevButton.released.connect(lambda: self.step(-1))
        self.ui.nextButton.released.connect(lambda: self.step(1))
        self.ui.dateEdit.dateChanged.connect(self.show_guide)
        self.ui.dateEdit.setDate(QtCore.QDate().currentDate())

    def step(self, day):
        self.ui.dateEdit.setDate(self.ui.dateEdit.date().addDays(day))

    def show_guide(self):
        date = self.ui.dateEdit.date().toString("yyyyMMdd")
        index = self.ui.comboBox.currentIndex()
        if index < 0:
            return
        text = self.sh.get_schedule(date, self.channels[index], True)
        self.ui.textBrowser.setText(text)
