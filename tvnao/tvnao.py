# Copyright (c) 2016-2019 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import sys
import codecs
import requests
import subprocess
import datetime
import signal
import re
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot

from .tvnao_widget import Ui_Form
from .settings import Settings
from .tvnao_rc import *
from .schedule_handler import ScheduleHandler


class MainWindow(QtWidgets.QWidget):
    list = []
    process = None
    search_string = ''

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        # actions setup
        show_hide_action = QtWidgets.QAction(self)
        self.addAction(show_hide_action)
        show_hide_action.setShortcut('Ctrl+G')
        show_hide_action.triggered.connect(self.show_hide_guide)
        watch_action = QtWidgets.QAction(self)
        self.addAction(watch_action)
        watch_action.setShortcut('Return')
        watch_action.triggered.connect(self.activate_item)
        copy_action = QtWidgets.QAction(self)
        self.addAction(copy_action)
        copy_action.setText('Copy address')
        copy_action.setShortcut('Ctrl+C')
        copy_action.setIcon(QtGui.QIcon.fromTheme('edit-copy'))
        copy_action.triggered.connect(self.copy_to_clipboard)
        refresh_action = QtWidgets.QAction(self)
        self.addAction(refresh_action)
        refresh_action.setText('Refresh')
        refresh_action.setShortcut('Ctrl+R')
        refresh_action.setIcon(QtGui.QIcon.fromTheme(
            'view-refresh', QtGui.QIcon(':/icons/view-refresh.svg')))
        refresh_action.triggered.connect(self.refresh_all)
        settings_action = QtWidgets.QAction(self)
        self.addAction(settings_action)
        settings_action.setText('Settings')
        settings_action.setShortcut('Ctrl+P')
        settings_action.setIcon(QtGui.QIcon.fromTheme(
            'configure', QtGui.QIcon(':/icons/configure.svg')))
        settings_action.triggered.connect(self.show_settings)
        about_action = QtWidgets.QAction(self)
        about_action.setText('About')
        about_action.setIcon(QtGui.QIcon.fromTheme(
            'video-television', QtGui.QIcon(':/icons/video-television.svg')))
        about_action.triggered.connect(self.show_about)
        quit_action = QtWidgets.QAction(self)
        self.addAction(quit_action)
        quit_action.setText('Quit')
        quit_action.setShortcut('Ctrl+Q')
        quit_action.setIcon(QtGui.QIcon.fromTheme(
            'application-exit', QtGui.QIcon(':/icons/application-exit.svg')))
        quit_action.triggered.connect(self.close)
        # signal/slot setup
        self.ui.buttonGo.released.connect(self.activate_item)
        self.ui.listWidget.itemDoubleClicked.connect(self.activate_item)
        self.ui.listWidget.itemSelectionChanged.connect(self.update_guide)
        self.ui.buttonGuide.released.connect(self.show_hide_guide)
        # gui setup
        menu = QtWidgets.QMenu()
        menu.addAction(refresh_action)
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(about_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.ui.listWidget.addAction(copy_action)
        self.ui.listWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.ui.buttonMenu.setIcon(QtGui.QIcon.fromTheme(
            'video-television', QtGui.QIcon(':/icons/video-television.svg')))
        self.ui.buttonMenu.setMenu(menu)
        self.ui.buttonGo.setIcon(QtGui.QIcon.fromTheme(
            'media-playback-start',
            QtGui.QIcon(':/icons/media-playback-start.svg')))
        self.set_guide_visibility(False)
        QtWidgets.QScroller.grabGesture(
            self.ui.listWidget, QtWidgets.QScroller.TouchGesture)
        Settings.first_run()
        self.load_settings()
        self.sh = ScheduleHandler(self.guide_addr)

    def load_settings(self):
        self.playlist_addr = Settings.settings.value('playlist/addr', type=str)
        self.player = Settings.settings.value('player/path', type=str)
        self.options = Settings.settings.value('player/options', type=str)
        self.keep_single = Settings.settings.value('player/single', type=bool)
        self.guide_addr = Settings.settings.value('guide/addr', type=str)

    def refresh_all(self):
        self.update_list_widget()
        if self.ui.listWidget.count() > 0:
            self.ui.listWidget.setCurrentRow(0)

    def refresh_list(self):
        print('getting remote playlist...')
        try:
            response = requests.get(self.playlist_addr)
        except requests.exceptions.ConnectionError as e:
            print("Connection error: {}".format(e))
            QtWidgets.QMessageBox.warning(self, "Network Error", str(e))
            return
        playlist = response.content.decode('utf-8')
        playlist += self.append_local_file()
        self.list = list()
        counter = 0
        for line in playlist.splitlines():
            if line.startswith('#EXTINF'):
                counter += 1
                name = "{}. {}".format(counter, line.split(',')[1])
                match = re.match(r'.*tvg-id=(\w+).*', line)
                id = match.group(1) if match else None
                title = re.match(r'.*group-title=\"(.+)\".*', line)
                if title:
                    self.list.append((title.group(1), None, None))
            elif line.startswith('udp://') or line.startswith('http://')\
                    or line.startswith('file://'):
                addr = line
                self.list.append((name, addr, id))

    def update_list_widget(self):
        self.refresh_list()
        self.ui.listWidget.clear()
        for entry in self.list:
            item = QtWidgets.QListWidgetItem(entry[0])
            if entry[1]:
                item.setIcon(QtGui.QIcon.fromTheme('video-webm'))
            self.ui.listWidget.addItem(item)

    @pyqtSlot(str, name='on_lineEditFilter_textEdited')
    def filter(self, string):
        counter = 0
        self.search_string = string
        for entry in self.list:
            hidden = bool(entry[1]) and string.lower() not in entry[0].lower()
            self.ui.listWidget.item(counter).setHidden(hidden)
            counter += 1

    def activate_item(self):
        row = self.ui.listWidget.currentRow()
        if not len(self.list) or row < 0:
            return
        address = self.list[row][1]
        if not address:
            row += 1
            while self.list[row][1]:
                item = self.ui.listWidget.item(row)
                item.setHidden(not item.isHidden() or
                               self.search_string.lower()
                               not in item.text().lower())
                row += 1
                if item is None:
                    break
            return
        command = [self.player]
        if command[0].endswith('mpv'):
            command.append('--force-media-title=' +
                           self.ui.listWidget.currentItem().text())
        options = self.options.split()
        if options:
            command += options
        command.append(self.list[row][1])
        if self.keep_single and self.process:
            try:
                if 'win' in sys.platform:
                    self.process.terminate()
                else:
                    self.process.send_signal(2)
            except ProcessLookupError:
                pass
        try:
            self.process = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                            stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            QtWidgets.QMessageBox.warning(
                self, "No such player", "Please check your settings")
            return
        print('running process with pid: %s\n  %s' % (str(self.process.pid),
                                                      str(command)))

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

    def update_guide(self):
        if self.ui.guideBrowser.isVisible():
            if self.ui.listWidget.count() < 1:
                return
            id = self.list[self.ui.listWidget.currentRow()][2]
            if not id:
                self.ui.guideBrowser.setText('<b>not available</b>')
                return
            date = int(datetime.date.today().strftime("%Y%m%d"))
            if self.ui.guideNextButton.isChecked():
                date += 1
            all_day = self.ui.guideNextButton.isChecked() or\
                self.ui.guideFullButton.isChecked()
            text = self.sh.get_schedule(date, id, all_day)
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

    def append_local_file(self):
        if len(sys.argv) > 1:
            with codecs.open(sys.argv[1], 'r', 'utf-8') as local_playlist:
                file_contents = local_playlist.read()
            if '#EXTM3U' not in file_contents[:9]:
                print('E: contents of additional playlist are not valid')
            else:
                return file_contents.replace('#EXTM3U', '', 1)
        return ''

    def copy_to_clipboard(self):
        QtWidgets.QApplication.clipboard().setText(
            self.list[self.ui.listWidget.currentRow()][1])

    def show_settings(self):
        settings_dialog = Settings()
        settings_dialog.exec_()
        settings_dialog.destroyed.connect(self.load_settings)

    def show_about(self):
        QtWidgets.QMessageBox.about(
            self, 'About tvnao',
            '<p><b>tvnao</b> v0.8.99 &copy; 2016-2019 Blaze</p>'
            '<p>&lt;blaze@vivaldi.net&gt;</p>'
            '<p><a href="https://bitbucket.org/blaze/tvnao">'
            'https://bitbucket.org/blaze/tvnao</a></p>')


def main():
    if sys.hexversion < 0x30500f0:
        print('E: python version is too old, 3.5 or higher needed')
        sys.exit(1)
    if 'linux' in sys.platform:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    app = QtWidgets.QApplication(sys.argv)
    tv_widget = MainWindow()
    tv_widget.setWindowIcon(QtGui.QIcon.fromTheme(
        'video-television', QtGui.QIcon(':/icons/video-television.svg')))
    tv_widget.show()
    tv_widget.update_list_widget()
    sys.exit(app.exec_())
