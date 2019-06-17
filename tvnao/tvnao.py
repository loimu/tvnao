# Copyright (c) 2016-2019 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from os import sys, path
from urllib import request, error
from subprocess import Popen, DEVNULL
import datetime
import signal
import re

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThreadPool

from .tvnao_widget import Ui_Form
from .settings import Settings
from .tvnao_rc import *
from .schedule_handler import ScheduleHandler
from .guide_viewer import GuideViewer


class WorkerSignals(QtCore.QObject):
    signal_finished = pyqtSignal()
    signal_error = pyqtSignal(str)


class Worker(QtCore.QRunnable):

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
        show_hide_action = QtWidgets.QAction(self)
        self.addAction(show_hide_action)
        show_hide_action.setShortcut('Ctrl+G')
        show_hide_action.triggered.connect(self.show_hide_guide)
        watch_action = QtWidgets.QAction(self)
        self.addAction(watch_action)
        watch_action.setShortcut('Return')
        watch_action.triggered.connect(self.activate_item)
        fold_action = QtWidgets.QAction(self)
        self.addAction(fold_action)
        fold_action.setShortcut('Ctrl+F')
        fold_action.triggered.connect(self.fold_everything)
        search_focus_action = QtWidgets.QAction(self)
        self.addAction(search_focus_action)
        search_focus_action.setShortcut('Ctrl+S')
        search_focus_action.triggered.connect(self.ui.lineEditFilter.setFocus)
        clear_search_action = QtWidgets.QAction(self)
        self.addAction(clear_search_action)
        clear_search_action.setShortcut('Esc')
        clear_search_action.triggered.connect(self.ui.lineEditFilter.clear)
        copy_action = QtWidgets.QAction('Copy address', self)
        self.addAction(copy_action)
        copy_action.setShortcut('Ctrl+C')
        copy_action.setIcon(QtGui.QIcon.fromTheme('edit-copy'))
        copy_action.triggered.connect(self.copy_to_clipboard)
        refresh_action = QtWidgets.QAction('&Refresh', self)
        self.addAction(refresh_action)
        refresh_action.setShortcut('Ctrl+R')
        refresh_action.setIcon(QtGui.QIcon.fromTheme('view-refresh'))
        refresh_action.triggered.connect(self.refresh_forced)
        viewer_action = QtWidgets.QAction(self)
        self.addAction(viewer_action)
        viewer_action.setShortcut('Ctrl+V')
        viewer_action.triggered.connect(self.show_guide_viewer)
        settings_action = QtWidgets.QAction('&Settings', self)
        self.addAction(settings_action)
        settings_action.setShortcut('Ctrl+P')
        settings_action.setIcon(QtGui.QIcon.fromTheme('configure'))
        settings_action.triggered.connect(self.show_settings)
        about_action = QtWidgets.QAction('&About', self)
        about_action.setIcon(QtGui.QIcon.fromTheme('video-television'))
        about_action.triggered.connect(self.show_about)
        quit_action = QtWidgets.QAction('&Quit', self)
        self.addAction(quit_action)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.setIcon(QtGui.QIcon.fromTheme('application-exit'))
        quit_action.triggered.connect(self.quit)
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
        self.ui.buttonMenu.setIcon(QtGui.QIcon.fromTheme('video-television'))
        self.ui.buttonMenu.setMenu(menu)
        self.ui.buttonGo.setIcon(QtGui.QIcon.fromTheme('media-playback-start'))
        self.set_guide_visibility(False)
        QtWidgets.QScroller.grabGesture(
            self.ui.listWidget, QtWidgets.QScroller.TouchGesture)
        # init
        Settings.first_run()
        self.load_settings()
        self.list = list()
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
        self.list = list()
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
                    self.list.append((title.group(1), None, None))
                    item = QtWidgets.QListWidgetItem(title.group(1))
                    self.ui.listWidget.addItem(item)
            elif line.startswith('udp://') or line.startswith('http://')\
                    or line.startswith('file://'):
                self.list.append((name, line, id))
                item = QtWidgets.QListWidgetItem(name)
                item.setIcon(QtGui.QIcon.fromTheme('video-webm'))
                self.ui.listWidget.addItem(item)
        return status

    @pyqtSlot(str, name='on_lineEditFilter_textChanged')
    def filter(self, string):
        self.folded = False
        self.search_string = string
        for index, entry in enumerate(self.list):
            hidden = bool(entry[1]) and string.lower()\
                not in self.ui.listWidget.item(index).text().lower()
            self.ui.listWidget.item(index).setHidden(hidden)

    def activate_item(self):
        row = self.ui.listWidget.currentRow()
        if not len(self.list) or row < 0:
            return
        if not self.list[row][1]:
            self.folded = False
            row += 1
            while row < len(self.list) and self.list[row][1]:
                item = self.ui.listWidget.item(row)
                item.setHidden(not item.isHidden()
                               or self.search_string.lower()
                               not in item.text().lower())
                row += 1
                if item is None:
                    break
            return
        command = [self.player]
        if self.player.count('mpv'):
            command.append('--force-media-title=' +
                           self.ui.listWidget.currentItem().text())
        command += self.options.split()
        command.append(self.list[row][1])
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
            id = self.list[self.ui.listWidget.currentRow()][2]
            if not id:
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
        if self.list:
            QtWidgets.QApplication.clipboard().setText(
                self.list[self.ui.listWidget.currentRow()][1])

    def load_guide_wrapper(self):
        guide_worker = Worker(self.load_guide_archive)
        guide_worker.signals.signal_finished.connect(self.update_guide)
        self.thread_pool.start(guide_worker)

    def load_guide_archive(self):
        self.sh = ScheduleHandler(self.guide_addr)

    def fold_everything(self):
        for row, entry in enumerate(self.list):
            item = self.ui.listWidget.item(row)
            hidden = bool(entry[1]) and (
                not self.folded
                or self.search_string.lower() not in item.text().lower())
            self.ui.listWidget.item(row).setHidden(hidden)
        self.folded = not self.folded

    def show_settings(self):
        settings_dialog = Settings(self)
        settings_dialog.show()
        settings_dialog.destroyed.connect(self.load_settings)

    def show_guide_viewer(self):
        channel = self.list[self.ui.listWidget.currentRow()][0]
        gw = GuideViewer(self, self.sh, self.list, channel)
        gw.show()

    def show_about(self):
        QtWidgets.QMessageBox.about(
            self, "About tvnao",
            "<p><b>tvnao</b> v0.10.97 &copy; 2016-2019 Blaze</p>"
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
