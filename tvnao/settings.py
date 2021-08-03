# Copyright (c) 2016-2021 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import sys
import subprocess

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QSettings, pyqtSlot

from .settings_dialog import Ui_Dialog


class SettingsHelper():
    settings = QSettings('tvnao', 'tvnao')
    defaults = {
        'playlist/addr':    'http://iptv.isp.domain/iptv_playlist.m3u',
        'player/options':   '--network-timeout=60 --no-ytdl '
                            '--force-window=immediate --no-resume-playback',
        'player/single':    False,
        'guide/addr':       '',
        'tvnao/configured_1': True
    }

    def first_run(self):
        if bool(self.settings.value('tvnao/configured_1')):
            return
        print('adding config options...')
        for entry in self.defaults:
            self.settings.setValue(entry, self.defaults[entry])
        self.settings.setValue('player/path', self.detect_player())

    def detect_player(self):
        if 'win' in sys.platform:
            return 'mpv'
        player = subprocess.getoutput('which mpv mplayer mplayer2')\
            .split('\n')[0]
        return player if player else 'mpv'

    def get_settings(self):
        return self.settings


class SettingsDialog(QtWidgets.QDialog):

    def __init__(self,
                 parent: QtWidgets.QWidget, settings_helper: SettingsHelper):
        super(SettingsDialog, self).__init__(parent)
        self.sh = settings_helper
        self.settings = settings_helper.get_settings()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.playlistAddr.setText(
            self.settings.value('playlist/addr', type=str))
        self.ui.playerPath.setText(
            self.settings.value('player/path', type=str))
        self.ui.playerOptions.setText(
            self.settings.value('player/options', type=str))
        self.ui.playerSingle.setChecked(
            self.settings.value('player/single', type=bool))
        self.ui.guideAddr.setText(self.settings.value('guide/addr', type=str))
        self.setWindowIcon(QtGui.QIcon.fromTheme('configure'))
        self.ui.playerButton.setIcon(QtGui.QIcon.fromTheme('document-open'))

    @pyqtSlot()
    def on_playerButton_released(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open player', '', "")[0]
        if path:
            self.ui.playerPath.setText(path)

    @pyqtSlot(name='on_buttonBox_accepted')
    def save(self):
        self.settings.setValue('playlist/addr', self.ui.playlistAddr.text())
        self.settings.setValue('player/path', self.ui.playerPath.text())
        self.settings.setValue('player/options', self.ui.playerOptions.text())
        self.settings.setValue('player/single',self.ui.playerSingle.isChecked())
        self.settings.setValue('guide/addr', self.ui.guideAddr.text())
        self.destroyed.emit()

    @pyqtSlot()
    def on_defaultsButton_released(self):
        self.ui.playlistAddr.setText(self.sh.defaults['playlist/addr'])
        self.ui.playerPath.setText(self.sh.detect_player())
        self.ui.playerOptions.setText(self.sh.defaults['player/options'])
        self.ui.playerSingle.setChecked(self.sh.defaults['player/single'])
        self.ui.guideAddr.setText(self.sh.defaults['guide/addr'])
