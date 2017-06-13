# Copyright (c) 2016-2017 Blaze <blaze@vivaldi.net>
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
        'playlist/host':    'iptv.isp.domain',
        'playlist/url':     '/iptv_playlist.m3u',
        'player/options':   '--network-timeout=60 --no-ytdl '
                            '--force-window=immediate --no-resume-playback',
        'player/single':    False,
        'epg/host':         'localhost:8089',
        'epg/url':          '/viewProgram',
        'tvnao/configured': True
    }

    @staticmethod
    def first_run():
        settings = Settings.settings
        if bool(settings.value('tvnao/configured')):
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

    def __init__(self):
        super(Settings, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.playlistHost.setText(
            self.settings.value('playlist/host', type=str))
        self.ui.playlistURL.setText(
            self.settings.value('playlist/url', type=str))
        self.ui.playerPath.setText(
            self.settings.value('player/path', type=str))
        self.ui.playerOptions.setText(
            self.settings.value('player/options', type=str))
        self.ui.playerSingle.setChecked(
            self.settings.value('player/single', type=bool))
        self.ui.epgHost.setText(self.settings.value('epg/host', type=str))
        self.ui.epgURL.setText(self.settings.value('epg/url', type=str))
        self.setWindowIcon(
            QtGui.QIcon.fromTheme('configure',
                                  QtGui.QIcon(':/icons/configure.svg')))
        self.ui.playerButton.setIcon(
            QtGui.QIcon.fromTheme('document-open',
                                  QtGui.QIcon(':/icons/document-open.svg')))

    @pyqtSlot()
    def on_playerButton_released(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open player', '', "")[0]
        if path:
            self.ui.playerPath.setText(path)

    @pyqtSlot(name='on_buttonBox_accepted')
    def save(self):
        self.settings.setValue('playlist/host', self.ui.playlistHost.text())
        self.settings.setValue('playlist/url', self.ui.playlistURL.text())
        self.settings.setValue('player/path', self.ui.playerPath.text())
        self.settings.setValue('player/options', self.ui.playerOptions.text())
        self.settings.setValue('player/single',
                               self.ui.playerSingle.isChecked())
        self.settings.setValue('epg/host', self.ui.epgHost.text())
        self.settings.setValue('epg/url', self.ui.epgURL.text())

    @pyqtSlot()
    def on_defaultsButton_released(self):
        self.ui.playlistHost.setText(self.defaults['playlist/host'])
        self.ui.playlistURL.setText(self.defaults['playlist/url'])
        self.ui.playerPath.setText(Settings.player_detect())
        self.ui.playerOptions.setText(self.defaults['player/options'])
        self.ui.epgHost.setText(self.defaults['epg/host'])
        self.ui.epgURL.setText(self.defaults['epg/url'])
