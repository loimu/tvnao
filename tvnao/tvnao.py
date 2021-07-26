# Copyright (c) 2016-2021 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from os import sys, path
from urllib import request, error
from subprocess import Popen, DEVNULL
import datetime
import signal
import re

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import (pyqtSlot, pyqtSignal,
                          QObject, QThreadPool, QRunnable, Qt)

from .tvnao_widget import Ui_Form
from .settings import Settings
from .schedule_handler import ScheduleHandler
from .guide_viewer import GuideViewer
from .tvnao_rc import *


class WorkerSignals(QObject):
    signal_finished = pyqtSignal()
    signal_error = pyqtSignal(str)


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        error_message = self.fn(*self.args, **self.kwargs)
        if error_message:
            self.signals.signal_error.emit(error_message)
        self.signals.signal_finished.emit()


class MainWindow(QtWidgets.QWidget):
    sh = None
    process = None
    search_string = ""
    folded = False

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        if not QtGui.QIcon.hasThemeIcon('video-television'):
            QtGui.QIcon.setThemeName("breeze")
        # actions setup
        clear_action = QtWidgets.QAction(self)
        clear_action.setShortcut('Esc')
        clear_action.triggered.connect(self.ui.lineEditFilter.clear)
        fold_action = QtWidgets.QAction(self)
        fold_action.setShortcut('Ctrl+F')
        fold_action.triggered.connect(self.fold_everything)
        search_action = QtWidgets.QAction(self)
        search_action.setShortcut('Ctrl+S')
        search_action.triggered.connect(self.ui.lineEditFilter.setFocus)
        self.addActions([clear_action, fold_action, search_action])
        copy_action = QtWidgets.QAction('Copy address', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.setIcon(QtGui.QIcon.fromTheme('edit-copy'))
        self.ui.listWidget.addAction(copy_action)
        copy_action.triggered.connect(self.copy_to_clipboard)
        # signal/slot setup
        self.ui.buttonGo.released.connect(self.activate_item)
        self.ui.listWidget.itemDoubleClicked.connect(self.activate_item)
        self.ui.listWidget.itemSelectionChanged.connect(self.update_guide)
        self.ui.buttonGuide.released.connect(self.show_hide_guide)
        # gui setup
        self.ui.buttonGo.setShortcut('Return')
        self.ui.buttonGuide.setShortcut('Ctrl+G')
        menu = QtWidgets.QMenu(self)
        menu.addAction(QtGui.QIcon.fromTheme('view-refresh'),
                       '&Refresh', self.refresh_forced, 'Ctrl+R')
        menu.addAction(QtGui.QIcon.fromTheme('view-calendar-list'),
                       '&Viewer', self.show_guide_viewer, 'Ctrl+V')
        menu.addAction(QtGui.QIcon.fromTheme('configure'),
                       '&Settings', self.show_settings, 'Ctrl+P')
        menu.addSeparator()
        menu.addAction(QtGui.QIcon.fromTheme('video-television'),
                       '&About', self.show_about)
        menu.addSeparator()
        menu.addAction(QtGui.QIcon.fromTheme('application-exit'),
                       '&Quit', self.quit, 'Ctrl+Q')
        for action in menu.actions():
            action.setShortcutVisibleInContextMenu(True)
        self.ui.listWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.ui.buttonMenu.setIcon(QtGui.QIcon.fromTheme('video-television'))
        self.ui.buttonMenu.setMenu(menu)
        self.ui.buttonGo.setIcon(QtGui.QIcon.fromTheme('media-playback-start'))
        self.set_guide_visibility(False)
        QtWidgets.QScroller.grabGesture(
            self.ui.listWidget, QtWidgets.QScroller.TouchGesture)
        # init
        Settings.first_run()
        self.load_settings()
        self.thread_pool = QThreadPool()

    def load_settings(self):
        self.playlist_addr = Settings.settings.value('playlist/addr', type=str)
        self.player = Settings.settings.value('player/path', type=str)
        self.options = Settings.settings.value('player/options', type=str)
        self.keep_single = Settings.settings.value('player/single', type=bool)
        self.guide_addr = Settings.settings.value('guide/addr', type=str)

    def refresh_forced(self):
        self.folded = False
        self.ui.listWidget.clear()
        self.refresh_list_wrapper()

    def refresh_list_wrapper(self):
        list_worker = Worker(self.refresh_list)
        list_worker.signals.signal_error.connect(
            lambda x: QtWidgets.QMessageBox.warning(self, "Network Error", x))
        self.thread_pool.start(list_worker)

    def refresh_list(self):
        print("getting remote playlist", self.playlist_addr)
        response, status = None, ""
        try:
            response = request.urlopen(self.playlist_addr)
        except error.URLError as e:
            status = str(e.reason)
        except ValueError as e:
            status = str(e)
        playlist = response.read().decode('utf-8') if response else ""
        playlist += self.append_local_file()
        counter = 0
        for line in playlist.splitlines():
            if line.startswith('#EXTINF'):
                counter += 1
                name = "{}. {}".format(counter, line.split(',')[1])
                match = re.match(r".*tvg-(id|name)=(.*?)(\s|,).*", line)
                id = match.group(2) if match else None
                title = re.match(r".*group-title=\"(.+?)\".*", line)
                if title:
                    item = QtWidgets.QListWidgetItem(title.group(1))
                    self.ui.listWidget.addItem(item)
            elif line.startswith('udp://') or line.startswith('http://')\
                    or line.startswith('file://'):
                item = QtWidgets.QListWidgetItem(name)
                item.setIcon(QtGui.QIcon.fromTheme('video-webm'))
                item.setData(Qt.UserRole, (line, id))
                self.ui.listWidget.addItem(item)
        return status

    @pyqtSlot(str, name='on_lineEditFilter_textChanged')
    def filter(self, string):
        self.folded = False
        self.search_string = string
        for item in self.ui.listWidget.findItems("", Qt.MatchContains):
            item.setHidden(string.lower() not in item.text().lower()
                           and bool(item.data(Qt.UserRole)))

    def activate_item(self):
        selected_item = self.ui.listWidget.currentItem()
        if not selected_item:
            return
        data = selected_item.data(Qt.UserRole)
        if not data:
            self.folded = False
            row = self.ui.listWidget.currentRow() + 1
            while row < self.ui.listWidget.count()\
                and bool(self.ui.listWidget.item(row).data(Qt.UserRole)):
                    item = self.ui.listWidget.item(row)
                    item.setHidden(not item.isHidden()
                                   or self.search_string.lower()
                                   not in item.text().lower())
                    row += 1
            return
        command = [self.player]
        if self.player.count('mpv'):
            command.append('--force-media-title=' +
                           self.ui.listWidget.currentItem().text())
        command += self.options.split()
        command.append(data[0])
        if self.keep_single and self.process:
            try:
                if 'win' in sys.platform:
                    self.process.terminate()
                else:
                    self.process.send_signal(2)
            except ProcessLookupError:
                pass
        if not (path.isfile(self.player)
                or path.isfile(self.player + '.exe')):
            QtWidgets.QMessageBox.warning(
                self, "No such player", "Please check your settings")
            return
        self.process = Popen(
            command, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
        print("running process with pid:",
              str(self.process.pid), "\n  ", str(command))

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
            data = self.ui.listWidget.currentItem().data(Qt.UserRole)
            if data:
                id = data[1]
            else:
                self.ui.guideBrowser.setText("<b>not available</b>")
                return
            date = int(datetime.date.today().strftime("%Y%m%d"))
            if self.ui.guideNextButton.isChecked():
                date += 1
            all_day = self.ui.guideNextButton.isChecked()\
                or self.ui.guideFullButton.isChecked()
            text = self.sh.get_schedule(date, id, all_day)\
                if self.sh else "loading…"
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
        contents = ""
        for file in sys.argv[1:]:
            if path.isfile(file):
                with open(file, 'r') as local_playlist:
                    contents += local_playlist.read()
        return contents

    def copy_to_clipboard(self):
        data = self.ui.listWidget.currentItem().data(Qt.UserRole)
        if bool(data):
            QtWidgets.QApplication.clipboard().setText(data[0])

    def load_guide_wrapper(self):
        self.guide_worker = Worker(self.load_guide_archive)
        self.guide_worker.signals.signal_finished.connect(self.update_guide)
        self.thread_pool.start(self.guide_worker)

    def load_guide_archive(self):
        self.sh = ScheduleHandler(self.guide_addr)

    def fold_everything(self):
        for item in self.ui.listWidget.findItems("", Qt.MatchContains):
            item.setHidden((self.search_string.lower() not in item.text().lower()
                            or not self.folded) and bool(item.data(Qt.UserRole)))
        self.folded = not self.folded

    def show_settings(self):
        settings_dialog = Settings(self)
        settings_dialog.show()
        settings_dialog.destroyed.connect(self.load_settings)

    def show_guide_viewer(self):
        item = self.ui.listWidget.currentItem()
        channel = "" if not item.data(Qt.UserRole) else item.text()
        list = [(x.text(), x.data(Qt.UserRole)[1]) for x in self.ui.listWidget\
                .findItems("", Qt.MatchContains) if bool(x.data(Qt.UserRole))]
        gv = GuideViewer(self, self.sh, list, channel)
        gv.show()
        self.guide_worker.signals.signal_finished.\
            connect(lambda: gv.reset_handler(self.sh))

    def show_about(self):
        QtWidgets.QMessageBox.about(
            self, "About tvnao",
            "<p><b>tvnao</b> v0.12.0 &copy; 2016-2021 Blaze</p>"
            "<p>&lt;blaze@vivaldi.net&gt;</p>"
            "<p><a href=\"https://bitbucket.org/blaze/tvnao\">"
            "https://bitbucket.org/blaze/tvnao</a></p>")

    def quit(self):
        self.hide()
        self.thread_pool.waitForDone()
        self.close()


def main():
    if sys.hexversion < 0x030500f0:
        print("E: python version is too old, 3.5 or higher needed")
        sys.exit(1)
    if 'linux' in sys.platform:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    app = QtWidgets.QApplication(sys.argv)
    tv_widget = MainWindow()
    tv_widget.setWindowIcon(QtGui.QIcon.fromTheme('video-television'))
    tv_widget.show()
    tv_widget.refresh_list_wrapper()
    tv_widget.load_guide_wrapper()
    sys.exit(app.exec_())
