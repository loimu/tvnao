# Copyright (c) 2016-2023 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import datetime

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings, QDate, pyqtSlot, pyqtSignal, Qt

from tvnao.settings import SettingsHelper
from tvnao.timeshift_dialog import Ui_TimeshiftDialog


class Timeshift(QtWidgets.QDialog):
    start_player = pyqtSignal(str)

    def __init__(self, parent, sh, name, channel_id, settings_helper: SettingsHelper):
        super(Timeshift, self).__init__(parent)
        self.ui = Ui_TimeshiftDialog()
        self.ui.setupUi(self)
        self.sh = sh
        self.channel_id = channel_id
        self.helper = settings_helper
        self.settings = settings_helper.get_settings()
        self.ui.listWidget.itemDoubleClicked.connect(self._activate_item)
        self.ui.hostEdit.setText(self.settings.value('timeshift/host', type=str))
        self.ui.portEdit.setText(self.settings.value('timeshift/port', type=str))
        self.ui.prevButton.released.connect(lambda: self._step(-1))
        self.ui.nextButton.released.connect(lambda: self._step(1))
        self.ui.dateEdit.dateChanged.connect(self._show_guide)
        self.ui.dateEdit.setDate(QDate().currentDate())
        self.rejected.connect(self._save_settings)
        self.setWindowTitle(name)
        self._show_guide()

    def _step(self, day):
        self.ui.dateEdit.setDate(self.ui.dateEdit.date().addDays(day))

    def _show_guide(self):
        self.ui.listWidget.clear()
        date = self.ui.dateEdit.date().toString("yyyyMMdd")
        for entry in self.sh.get_timeshift_list(date, self.channel_id):
            item = QtWidgets.QListWidgetItem(entry[1] + " " + entry[2])
            item.setData(Qt.UserRole, entry[0])
            self.ui.listWidget.addItem(item)

    def _activate_item(self):
        if self.ui.listWidget.count() < 1:
            return
        host = self.ui.hostEdit.text()
        port = self.ui.portEdit.text()
        audio_chan = self.ui.audioSpinBox.value()
        item = self.ui.listWidget.currentItem()
        data = item.data(Qt.UserRole)
        entry_time = datetime.datetime.strptime(str(data), "%Y%m%d%H%M%S")
        current_time = datetime.datetime.now()
        diff_time = int((current_time - entry_time).total_seconds())
        self.start_player.emit(f"http://{host}:{port}/{self.channel_id}/tracks-v1a{audio_chan}/timeshift_rel-{diff_time}.m3u8")

    def _save_settings(self):
        self.settings.setValue('timeshift/host', self.ui.hostEdit.text())
        self.settings.setValue('timeshift/port', self.ui.portEdit.text())
