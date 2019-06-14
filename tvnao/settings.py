# Copyright (c) 2016-2019 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import sys
import subprocess

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QSettings, pyqtSlot

from .settings_dialog import Ui_Dialog


class Settings(QtWidgets.QDialog):
    settings = QSettings('tvnao', 'tvnao')
    defaults = {
        'playlist/addr':    'http://iptv.isp.domain/iptv_playlist.m3u',
        'player/options':   '--network-timeout=60 --no-ytdl '
                            '--force-window=immediate --no-resume-playback',
        'player/single':    False,
        'guide/addr':       'http://iptv.isp.domain/jtv.zip',
        'tvnao/configured_1': True
    }

    @staticmethod
    def first_run():
        settings = Settings.settings
        if bool(settings.value('tvnao/configured_1')):
            return
        print('adding config options...')
        for entry in Settings.defaults:
            settings.setValue(entry, Settings.defaults[entry])
        settings.setValue('player/path', Settings.player_detect())

    @staticmethod
    def player_detect():
        if 'win' in sys.platform:
            return 'mpv'
        player = subprocess.getoutput('which mpv mplayer mplayer2')\
            .split('\n')[0]
        return player if player else 'mpv'

    def __init__(self, parent):
        super(Settings, self).__init__(parent)
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
        self.settings.setValue('player/single',
                               self.ui.playerSingle.isChecked())
        self.settings.setValue('guide/addr', self.ui.guideAddr.text())
        self.destroyed.emit()

    @pyqtSlot()
    def on_defaultsButton_released(self):
        self.ui.playlistAddr.setText(self.defaults['playlist/addr'])
        self.ui.playerPath.setText(Settings.player_detect())
        self.ui.playerOptions.setText(self.defaults['player/options'])
        self.ui.playerSingle.setChecked(self.defaults['player/single'])
        self.ui.guideAddr.setText(self.defaults['guide/addr'])
