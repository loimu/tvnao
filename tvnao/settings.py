# Copyright (c) 2016 Blaze <blaze@vivaldi.net>
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
        'playlist/host':  'iptv.isp.domain',
        'playlist/url':   '/iptv_playlist.m3u',
        'player/options': '--network-timeout=60 --no-ytdl '
                          '--force-window=immediate --no-resume-playback',
        'epg/host':       'localhost:8089',
        'epg/index':      '/epg',
        'epg/url':        '/viewProgram',
        'epg/aliases':    '',
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
        self.ui.errorLabel.setVisible(False)
        self.ui.playlistHost.setText(
            self.settings.value('playlist/host', type=str))
        self.ui.playlistURL.setText(
            self.settings.value('playlist/url', type=str))
        self.ui.playerPath.setText(
            self.settings.value('player/path', type=str))
        self.ui.playerOptions.setText(
            self.settings.value('player/options', type=str))
        self.epg_host = self.settings.value('epg/host', type=str)
        self.ui.epgHost.setText(self.epg_host)
        self.ui.epgIndex.setText(self.settings.value('epg/index', type=str))
        self.ui.epgURL.setText(self.settings.value('epg/url', type=str))
        self.ui.tableAliases.horizontalHeader().setStretchLastSection(True)
        self.fill_table(self.settings.value('epg/aliases', type=str))
        self.setWindowIcon(
            QtGui.QIcon.fromTheme('configure',
                                  QtGui.QIcon(':/icons/configure.svg')))

    def fill_table(self, input):
        self.ui.tableAliases.setHorizontalHeaderLabels(['Playlist Entries',
                                                        'Guide Entries'])
        aliases = input.split('|')
        divider = ','
        if divider not in aliases[0]:
            return
        self.ui.tableAliases.setRowCount(len(aliases))
        for i, alias in enumerate(aliases):
            pair = alias.split(divider)
            if len(pair) > 1:
                self.ui.tableAliases.setItem(
                    i, 0, QtWidgets.QTableWidgetItem(pair[0]))
                self.ui.tableAliases.setItem(
                    i, 1, QtWidgets.QTableWidgetItem(pair[1]))

    @pyqtSlot(name='on_buttonBox_accepted')
    def save(self):
        self.settings.setValue('playlist/host', self.ui.playlistHost.text())
        self.settings.setValue('playlist/url', self.ui.playlistURL.text())
        self.settings.setValue('player/path', self.ui.playerPath.text())
        self.settings.setValue('player/options', self.ui.playerOptions.text())
        self.settings.setValue('epg/host', self.ui.epgHost.text())
        self.settings.setValue('epg/index', self.ui.epgIndex.text())
        self.settings.setValue('epg/url', self.ui.epgURL.text())
        aliases = ''
        counter = 0
        for i in range(0, self.ui.tableAliases.rowCount()):
            if hasattr(self.ui.tableAliases.item(i, 0), 'text') and \
                    hasattr(self.ui.tableAliases.item(i, 1), 'text'):
                playlist_name = self.ui.tableAliases.item(i, 0)\
                    .text().lower().strip(',|')
                guide_name = self.ui.tableAliases.item(i, 1)\
                    .text().lower().strip(',|')
                if len(playlist_name) > 0 and len(guide_name) > 0:
                    if counter > 0:
                        aliases += '|'
                    counter += 1
                    aliases += playlist_name + ',' + guide_name
        self.settings.setValue('epg/aliases', aliases)
        if self.epg_host != self.ui.epgHost.text():
            self.settings.setValue('epg/cache', '')

    @pyqtSlot()
    def on_aliasAddButton_released(self):
        row = self.ui.tableAliases.rowCount()
        self.ui.tableAliases.setRowCount(row + 1)
        self.ui.tableAliases.setCurrentCell(row, 0)

    @pyqtSlot()
    def on_aliasDelButton_released(self):
        self.ui.tableAliases.removeRow(self.ui.tableAliases.currentRow())

    @pyqtSlot()
    def on_defaultsButton_released(self):
        self.ui.playlistHost.setText(self.defaults['playlist/host'])
        self.ui.playlistURL.setText(self.defaults['playlist/url'])
        self.ui.playerPath.setText(Settings.player_detect())
        self.ui.playerOptions.setText(self.defaults['player/options'])
        self.ui.epgHost.setText(self.defaults['epg/host'])
        self.ui.epgIndex.setText(self.defaults['epg/index'])
        self.ui.epgURL.setText(self.defaults['epg/url'])
        self.ui.tableAliases.clear()
        self.ui.tableAliases.setRowCount(0)
        self.fill_table(self.defaults['epg/aliases'])
