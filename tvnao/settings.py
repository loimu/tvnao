# Copyright (c) 2016 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import sys
import subprocess

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings, pyqtSlot

from .settings_dialog import Ui_Dialog

class Settings(QtWidgets.QDialog):
    settings = QSettings('tvnao', 'tvnao')
    defaults = {
        'playlist/host':  'iptv.isp.domain',
        'playlist/url':   '/iptv_playlist.m3u',
        'player/options': '--network-timeout=60 --no-ytdl --force-window=immediate',
        'epg/host':       'www.tvguide.domain',
        'epg/index':      '/epg',
        'epg/url':        '/engine/modules/EPG/ViewProgramForOneDay.php',
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
            return 'mpv.exe'
        return subprocess.getoutput('which mpv mplayer mplayer2').split('\n')[0]

    def __init__(self):
        super(Settings, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.playlistHost.setText(self.settings.value('playlist/host', type=str))
        self.ui.playlistURL.setText(self.settings.value('playlist/url', type=str))
        self.ui.playerPath.setText(self.settings.value('player/path', type=str))
        self.ui.playerOptions.setText(self.settings.value('player/options', type=str))
        self.ui.epgHost.setText(self.settings.value('epg/host', type=str))
        self.ui.epgIndex.setText(self.settings.value('epg/index', type=str))
        self.ui.epgURL.setText(self.settings.value('epg/url', type=str))
        self.fill_table(self.settings.value('epg/aliases', type=str))

    def fill_table(self, input):
        aliases = input.split('|')
        divider = ','
        if not divider in aliases[0]:
            return
        self.ui.tableAliases.setRowCount(len(aliases))
        for i, alias in enumerate(aliases):
            pair = alias.split(divider)
            if len(pair) > 1:
                self.ui.tableAliases.setItem(i, 0, QtWidgets.QTableWidgetItem(pair[0]))
                self.ui.tableAliases.setItem(i, 1, QtWidgets.QTableWidgetItem(pair[1]))

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
        for i in range(0, self.ui.tableAliases.rowCount()):
            if i != 0:
                aliases += '|'
            aliases += self.ui.tableAliases.item(i, 0).text().lower() + ',' + \
            self.ui.tableAliases.item(i, 1).text().lower()
        self.settings.setValue('epg/aliases', aliases)

    @pyqtSlot()
    def on_aliasAddButton_released(self):
        if self.ui.aliasPlaylist.text()=='' or self.ui.aliasGuide.text()=='':
            self.ui.errorLabel.setText('<b>fields should not be empty</b>')
            return
        row = self.ui.tableAliases.rowCount()
        self.ui.tableAliases.setRowCount(row + 1)
        self.ui.tableAliases.setItem(row, 0, QtWidgets.QTableWidgetItem(self.ui.aliasPlaylist.text()))
        self.ui.tableAliases.setItem(row, 1, QtWidgets.QTableWidgetItem(self.ui.aliasGuide.text()))
        self.ui.aliasPlaylist.clear()
        self.ui.aliasGuide.clear()
        self.ui.errorLabel.setText('')

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
