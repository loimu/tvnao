# Copyright (c) 2016 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import sys
import subprocess
import http.client
import urllib.parse
import datetime
import re
import signal
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QSettings, pyqtSlot

from .tvnao_widget import Ui_Form
from .settings_dialog import Ui_Dialog

class ListItem(QtWidgets.QListWidgetItem):
    address = ''

    def __init__(self):
        super(ListItem, self).__init__()

class MainWindow(QtWidgets.QWidget):
    list = []
    index = {}
    settings = QSettings('tvnao', 'tvnao')

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        if not self.settings.value('tvnao/configured', type=bool):
            self.first_run()
        self.load_settings()
        # actions setup
        quit_action = QtWidgets.QAction(self)
        self.addAction(quit_action)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(self.close)
        show_hide_action = QtWidgets.QAction(self)
        self.addAction(show_hide_action)
        show_hide_action.setShortcut('Ctrl+G')
        show_hide_action.triggered.connect(self.show_hide_guide)
        watch_action = QtWidgets.QAction(self)
        self.addAction(watch_action)
        watch_action.setShortcut('Return')
        watch_action.triggered.connect(self.run_player)
        refresh_action = QtWidgets.QAction(self)
        self.addAction(refresh_action)
        refresh_action.setText('Refresh')
        refresh_action.setShortcut('Ctrl+R')
        refresh_action.setIcon(QtGui.QIcon.fromTheme('view-refresh'))
        refresh_action.triggered.connect(self.refresh_all)
        settings_action = QtWidgets.QAction(self)
        self.addAction(settings_action)
        settings_action.setText('Settings')
        settings_action.setShortcut('Ctrl+P')
        settings_action.setIcon(QtGui.QIcon.fromTheme('configure'))
        settings_action.triggered.connect(self.show_settings)
        about_action = QtWidgets.QAction(self)
        about_action.setText('About')
        about_action.setIcon(QtGui.QIcon.fromTheme('video-television'))
        about_action.triggered.connect(self.show_about)
        # signal/slot setup
        self.ui.buttonGo.released.connect(self.run_player)
        self.ui.listWidget.itemDoubleClicked.connect(self.run_player)
        self.ui.listWidget.itemSelectionChanged.connect(self.update_guide)
        self.ui.buttonGuide.released.connect(self.show_hide_guide)
        # gui setup
        menu = QtWidgets.QMenu()
        menu.addAction(refresh_action)
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(about_action)
        self.ui.buttonMenu.setIcon(QtGui.QIcon.fromTheme('video-television'))
        self.ui.buttonMenu.setMenu(menu)
        self.ui.buttonGo.setIcon(QtGui.QIcon.fromTheme('media-playback-start'))
        self.set_guide_visibility(False)
        self.update_list_widget()
        if self.ui.listWidget.count() > 0:
            self.ui.listWidget.setCurrentRow(0)

    def player_detect(self):
        if 'win' in sys.platform:
            return 'mpv.exe'
        return subprocess.getoutput('which mpv mplayer mplayer2').split('\n')[0]

    def first_run(self):
        print('adding config options...')
        self.settings.setValue('playlist/host', 'iptv.isp.domain')
        self.settings.setValue('playlist/url', '/iptv_playlist.m3u')
        self.settings.setValue('player/path', self.player_detect())
        self.settings.setValue('player/options', '--network-timeout=60')
        self.settings.setValue('epg/host', 'www.tvguide.domain')
        self.settings.setValue('epg/url', '/engine/modules/EPG/ViewProgramForOneDay.php')
        self.settings.setValue('epg/index', '/epg')
        self.settings.setValue('epg/aliases', '')
        self.settings.setValue('tvnao/configured', True)

    def load_settings(self):
        self.playlist_host = self.settings.value('playlist/host', type=str)
        self.playlist_url = self.settings.value('playlist/url',type=str)
        self.player = self.settings.value('player/path', type=str)
        self.options = self.settings.value('player/options', type=str)
        self.epg_host = self.settings.value('epg/host', type=str)
        self.epg_url = self.settings.value('epg/url', type=str)
        self.epg_index = self.settings.value('epg/index', type=str)
        if not self.settings.value('epg/cache', type=bool):
            self.refresh_guide_index()
        cache = self.settings.value('epg/cache', type=str).split('|')
        for i, entry in enumerate(cache):
            pair = entry.split(',')
            if len(pair) > 1:
                self.index[pair[0]] = pair[1]

    def send_request_get(self, host, loc):
        conn = http.client.HTTPConnection(host, timeout=10)
        try:
            conn.request('GET', loc)
        except OSError:
            print('E: Network is unreachable. Please check your connection and try again.')
            return ''
        return conn.getresponse().read().decode('utf-8')

    def refresh_all(self):
        self.refresh_guide_index()
        self.update_list_widget()

    def refresh_list(self):
        self.list = []
        counter = 0
        print('getting remote playlist...')
        request = self.send_request_get(self.playlist_host, self.playlist_url)
        for line in request.splitlines():
            if line.startswith('#EXTINF'):
                counter += 1
                name = '%s. %s' % (counter, line.split(',')[1])
            elif line.startswith('udp://') or line.startswith('http://'):
                addr = line
                self.list.append((name, addr))

    def update_list_widget(self):
        self.refresh_list()
        self.ui.listWidget.clear()
        for entry in self.list:
            item = ListItem()
            item.setText(entry[0])
            item.address = entry[1]
            self.ui.listWidget.addItem(item)

    @pyqtSlot(str, name='on_lineEditFilter_textEdited')
    def filter(self, string):
        self.ui.listWidget.clear()
        for entry in self.list:
            if string.lower() in entry[0].lower():
                item = ListItem()
                item.setText(entry[0])
                item.address = entry[1]
                self.ui.listWidget.addItem(item)

    def run_player(self):
        command = [self.player]
        if self.options != '':
            command.append(self.options)
        command.append(self.ui.listWidget.currentItem().address)
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
        print('running new process with pid: %s\n  %s' % (str(process.pid), str(command)))

    def show_hide_guide(self):
        if self.ui.guideBrowser.isHidden():
            self.set_guide_visibility(True)
            self.update_guide()
        else:
            self.set_guide_visibility(False)

    def set_guide_visibility(self, visible):
        self.ui.guideBrowser.setVisible(visible)
        self.ui.buttonGuide.setChecked(visible)
        self.ui.guideFullButton.setVisible(visible)
        self.ui.guideNextButton.setVisible(visible)

    def get_guide_data(self, id, date, schedule):
        params = urllib.parse.urlencode({'id': id, 'date': date, 'schedule': schedule, 'start': 0})
        headers = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': 'text/html'}
        conn = http.client.HTTPConnection(self.epg_host, timeout=5)
        try:
            conn.request('POST', self.epg_url, params, headers)
        except OSError:
            return '<b>network error</b>'
        req = conn.getresponse()
        ret = re.sub('\<div.*?\</div\>|\<hr\>', '', req.read().decode('utf-8'))\
            .replace("class='before'", 'style="color:gray;"') \
            .replace("class='in'", 'style="color:indigo;"')
        return re.sub('(\d\d:\d\d)', '<b>\\1</b>', ret)

    def update_guide(self):
        if self.ui.guideBrowser.isVisible():
            if self.ui.listWidget.count() < 1:
                return
            key = re.sub('^\d{1,3}\.\s{1,2}', '', self.ui.listWidget.currentItem().text()).lower()
            if key not in self.index:
                self.ui.guideBrowser.setText('<b>not available</b>')
                return
            id = self.index[key]
            date = int(datetime.date.today().strftime("%Y%m%d"))
            if self.ui.guideNextButton.isChecked():
                date += 1
            all_day = self.ui.guideNextButton.isChecked() or self.ui.guideFullButton.isChecked()
            schedule = 'toggle_all_day' if all_day else 'toggle_now_day'
            text = self.get_guide_data(id, date, schedule)
            self.ui.guideBrowser.setText(text)
            self.ui.guideBrowser.setToolTip(text)

    @pyqtSlot()
    def on_guideFullButton_released(self):
        self.ui.guideNextButton.setChecked(False)
        self.update_guide()

    @pyqtSlot()
    def on_guideNextButton_released(self):
        self.ui.guideFullButton.setChecked(False)
        self.update_guide()

    def refresh_guide_index(self):
        print('refreshing epg index...')
        request = self.send_request_get(self.epg_host, self.epg_index)
        objects = re.finditer('id=\'(\d{1,7}?)\'.*?&nbsp;(.*?)\</td', request, flags=re.DOTALL)
        for o in objects:
            self.index[o.group(2).lower()] = o.group(1)
        aliases = self.settings.value('epg/aliases', type=str).split('|')
        for alias in aliases:
            pair = alias.split(',')
            if len(pair) > 1 and pair[1] in self.index:
                self.index[pair[0]] = self.index.pop(pair[1])
        cache = ''
        for i, entry in enumerate(self.index):
            if i != 0:
                cache += '|'
            cache += entry + ',' + self.index[entry]
        self.settings.setValue('epg/cache', cache)

    def show_settings(self):
        settings_dialog = Settings()
        settings_dialog.exec_()
        settings_dialog.destroyed.connect(self.load_settings)

    def show_about(self):
        QtWidgets.QMessageBox.about(self, 'About tvnao',
            '<p><b>tvnao</b> v0.5 &copy; 2016 Blaze</p>'
            '<p>&lt;blaze@vivaldi.net&gt;</p>'
            '<p><a href="https://bitbucket.org/blaze/tvnao">bitbucket.org/blaze/tvnao</a></p>')

class Settings(QtWidgets.QDialog):
    settings = QSettings('tvnao', 'tvnao')

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
        aliases = self.settings.value('epg/aliases', type=str).split('|')
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
            self.ui.errorLabel.setText('<b>field should not be empty</b>')
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

def main():
    if 'linux' in sys.platform:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    app = QtWidgets.QApplication(sys.argv)
    tv_widget = MainWindow()
    tv_widget.setWindowIcon(QtGui.QIcon.fromTheme('video-television'))
    tv_widget.show()
    sys.exit(app.exec_())
