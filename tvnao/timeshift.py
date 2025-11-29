# Copyright (c) 2016-2025 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import datetime

from PyQt6 import QtWidgets
from PyQt6.QtCore import QSettings, QDate, pyqtSlot, pyqtSignal, Qt

from tvnao.settings import SettingsHelper
from tvnao.timeshift_dialog import Ui_TimeshiftDialog


class Timeshift(QtWidgets.QDialog):
    start_player = pyqtSignal(str, str)

    def __init__(self, parent, sh, name, channel_id, settings_helper: SettingsHelper):
        super(Timeshift, self).__init__(parent)
        self.ui = Ui_TimeshiftDialog()
        self.ui.setupUi(self)
        self.sh = sh
        self.channel_id = channel_id
        self.channel_name = name
        self.helper = settings_helper
        self.settings = settings_helper.get_settings()
        self.replacements = self.settings.value('timeshift/repl', type=dict)
        self.ui.listWidget.itemDoubleClicked.connect(self._activate_item)
        self.ui.hostEdit.setText(self.settings.value('timeshift/host', type=str))
        self.ui.portEdit.setText(self.settings.value('timeshift/port', type=str))
        if channel_id in self.replacements:
            self.ui.channelEdit.setText(self.replacements[channel_id])
        else:
            self.ui.channelEdit.setText(channel_id)
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
            item = QtWidgets.QListWidgetItem(entry[2] + " " + entry[3])
            item.setData(Qt.UserRole, (entry[0], entry[1]))
            self.ui.listWidget.addItem(item)

    def _activate_item(self):
        if self.ui.listWidget.count() < 1:
            return
        host = self.ui.hostEdit.text()
        port = self.ui.portEdit.text()
        audio_chan = self.ui.audioSpinBox.value()
        channel_id = self.ui.channelEdit.text()
        if channel_id != self.channel_id:
            if not len(channel_id):
                self.replacements.pop(self.channel_id, None)
                channel_id = self.channel_id
                self.ui.channelEdit.setText(self.channel_id)
            else:
                self.replacements[self.channel_id] = channel_id
        item = self.ui.listWidget.currentItem()
        data = item.data(Qt.UserRole)
        start = datetime.datetime.strptime(str(data[0]), "%Y%m%d%H%M%S")
        stop = datetime.datetime.strptime(str(data[1]), "%Y%m%d%H%M%S")
        diff_time = int((stop - start).total_seconds())
        timestamp = int(start.replace().timestamp())
        self.start_player.emit(
            f"http://{host}:{port}/{channel_id}/mono-{timestamp}-{diff_time}.m3u8?filter=tracks:v1a{audio_chan}",
            f"{self.channel_name} -- {item.text()}")

    def _save_settings(self):
        self.settings.setValue('timeshift/host', self.ui.hostEdit.text())
        self.settings.setValue('timeshift/port', self.ui.portEdit.text())
        self.settings.setValue('timeshift/repl', self.replacements)
