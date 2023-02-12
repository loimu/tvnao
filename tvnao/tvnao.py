# Copyright (c) 2016-2023 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from os import sys, path
from urllib import request, error
from subprocess import Popen, DEVNULL
import datetime
import signal
import re
import logging

from PyQt5 import QtWidgets
from PyQt5.QtCore import (pyqtSlot, pyqtSignal,
                          QObject, QThreadPool, QRunnable, Qt)
from PyQt5.QtGui import QIcon, QPalette

from .tvnao_widget import Ui_Form
from .settings import SettingsHelper, SettingsDialog
from .schedule_handler import ScheduleHandler
from .guide_viewer import GuideViewer
from .timeshift import Timeshift
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
    search_term = ""
    folded = False
    bookmarks = []

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        logging.getLogger().setLevel(logging.DEBUG)
        if not QIcon.hasThemeIcon('video-television'):
            QIcon.setThemeName("breeze")
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
        timeshift_action = QtWidgets.QAction(self)
        timeshift_action.setShortcut('Ctrl+T')
        timeshift_action.triggered.connect(self.show_timeshift_dialog)
        self.addActions([clear_action, fold_action, search_action, timeshift_action])
        copy_action = QtWidgets.QAction('Copy address', self)
        copy_action.setShortcut('Ctrl+Shift+C')
        copy_action.setIcon(QIcon.fromTheme('edit-copy'))
        self.ui.listWidget.addAction(copy_action)
        copy_action.triggered.connect(self.copy_to_clipboard)
        bookmark_action = QtWidgets.QAction('Bookmark Current', self)
        bookmark_action.setShortcut('Ctrl+Shift+B')
        bookmark_action.setIcon(QIcon.fromTheme('bookmark-new'))
        bookmark_action.triggered.connect(self.bookmark_current)
        self.ui.listWidget.addAction(bookmark_action)
        unbookmark_action = QtWidgets.QAction('Remove from Bookmarks', self)
        unbookmark_action.setShortcut('Ctrl+Shift+R')
        unbookmark_action.setIcon(QIcon.fromTheme('bookmark-remove'))
        unbookmark_action.triggered.connect(self.bookmark_remove)
        self.ui.listWidget.addAction(unbookmark_action)
        # signal/slot setup
        self.ui.buttonGo.released.connect(self.activate_item)
        self.ui.listWidget.itemDoubleClicked.connect(self.activate_item)
        self.ui.listWidget.itemSelectionChanged.connect(self.update_guide)
        self.ui.buttonGuide.released.connect(self.show_hide_guide)
        # gui setup
        self.ui.buttonGo.setShortcut('Return')
        self.ui.buttonGuide.setShortcut('Ctrl+G')
        menu = QtWidgets.QMenu(self)
        menu.addAction(QIcon.fromTheme('view-refresh'),
                       '&Refresh', self.refresh_forced, 'Ctrl+R')
        menu.addAction(QIcon.fromTheme('view-calendar-list'),
                       '&Viewer', self.show_guide_viewer, 'Ctrl+V')
        menu.addAction(QIcon.fromTheme('configure'),
                       '&Settings', self.show_settings, 'Ctrl+P')
        self.view_bookmarks_action = menu.addAction(
            QIcon.fromTheme('bookmarks-organize'), '&Bookmarks')
        self.view_bookmarks_action.setShortcut('Ctrl+B')
        self.view_bookmarks_action.setCheckable(True)
        self.view_bookmarks_action.triggered.connect(self.view_bookmarks)
        menu.addSeparator()
        menu.addAction(QIcon.fromTheme('video-television'),
                       '&About', self.show_about)
        menu.addSeparator()
        menu.addAction(QIcon.fromTheme('application-exit'),
                       '&Quit', self.quit, 'Ctrl+Q')
        for action in menu.actions():
            action.setShortcutVisibleInContextMenu(True)
        self.ui.listWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.ui.buttonMenu.setIcon(QIcon.fromTheme('video-television'))
        self.ui.buttonMenu.setMenu(menu)
        self.ui.buttonGo.setIcon(QIcon.fromTheme('media-playback-start'))
        self.set_guide_visibility(False)
        QtWidgets.QScroller.grabGesture(
            self.ui.listWidget, QtWidgets.QScroller.TouchGesture)
        # init
        self.settings_helper = SettingsHelper()
        self.settings = self.settings_helper.get_settings()
        self.settings_helper.first_run()
        self.load_settings()
        self.thread_pool = QThreadPool()

    def show(self):
        super(MainWindow, self).show()
        self.refresh_list_wrapper()

    def load_settings(self):
        self.playlist_addr = self.settings.value('playlist/addr', type=str)
        self.player = self.settings.value('player/path', type=str)
        self.options = self.settings.value('player/options', type=str)
        self.keep_single = self.settings.value('player/single', type=bool)
        self.guide_addr = self.settings.value('guide/addr', type=str)
        self.bookmarks = self.settings.value('main/bookmarks', type=list)

    def refresh_forced(self):
        self.folded = False
        self.ui.listWidget.clear()
        self.refresh_list_wrapper()

    def refresh_list_wrapper(self):
        list_worker = Worker(self.refresh_list)
        list_worker.signals.signal_finished.connect(self.load_guide_wrapper)
        list_worker.signals.signal_error.connect(
            lambda x: QtWidgets.QMessageBox.warning(self, "Network Error", x))
        self.thread_pool.start(list_worker)

    def refresh_list(self):
        playlist, status, lists, offset, response = "", [], [], 0, None
        self.view_bookmarks_action.setChecked(False)
        if not self.playlist_addr:
            self.playlist_addr = sys.argv[1] if len(sys.argv) > 1 else ""
            offset = 1
        if not self.playlist_addr:
            return ("Please give a playlist address, either through settings "
                    "or as an application argument.")
        lists = [self.playlist_addr] +\
            (sys.argv[1 + offset:] if len(sys.argv) > 1 + offset else [])
        for list in lists:
            logging.info(f'getting remote playlist {list}')
            if not list.startswith('http'):
                list = "file://" + list
            try:
                response = request.urlopen(list)
            except error.URLError as e:
                status.append(str(e.reason))
            except ValueError as e:
                status.append(str(e))
            playlist += response.read().decode('utf-8') if response else ""
        counter = 0
        for line in playlist.splitlines():
            if line.startswith('#EXTM3U'):
                if not self.guide_addr:
                    match = re.match(r'.*url-tvg=([^\s,]*).*', line)
                    self.guide_addr = match.group(1).strip('"') if match else ""
            elif line.startswith('#EXTINF'):
                counter += 1
                name = "{}. {}".format(counter, line.split(',')[1])
                match = re.match(r'.*tvg-(?:id|name)=([^\s,]*).*', line)
                id = match.group(1).strip('"') if match else None
                title = re.match(r'.*group-title=\"?([^\",]*).*', line)
                if title:
                    item = QtWidgets.QListWidgetItem(title.group(1))
                    self.ui.listWidget.addItem(item)
            elif line.startswith('udp://') or line.startswith('http://')\
                    or line.startswith('file://'):
                item = QtWidgets.QListWidgetItem(name)
                if id in self.bookmarks:
                    item.setIcon(QIcon.fromTheme('folder-bookmark'))
                else:
                    item.setIcon(QIcon.fromTheme('video-webm'))
                item.setData(Qt.UserRole, (line, id))
                self.ui.listWidget.addItem(item)
        return ' '.join(status)

    def set_focus(self):
        row = self.ui.listWidget.currentRow()
        if row > 0:
            if not self.ui.listWidget.isRowHidden(row):
                item = self.ui.listWidget.item(row)
                self.ui.listWidget.scrollToItem(item)

    @pyqtSlot(str, name='on_lineEditFilter_textChanged')
    def filter(self, string):
        self.folded = False
        self.search_term = string
        for item in self.ui.listWidget.findItems("", Qt.MatchContains):
            data = item.data(Qt.UserRole)
            check = self.view_bookmarks_action.isChecked()
            item.setHidden(
                (not check and string.lower() not in item.text().lower()
                 and bool(data))
                or
                (check and (string.lower() not in item.text().lower()
                            or not bool(data)
                            or (bool(data) and data[1] not in self.bookmarks))))
        self.set_focus()

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
                item.setHidden(not item.isHidden() or self.search_term.lower()
                               not in item.text().lower())
                row += 1
            return
        self.play(data[0])

    @pyqtSlot(str, str)
    def play(self, url, title=None):
        command = [self.player]
        if self.player.count('mpv'):
            title = title if title else self.ui.listWidget.currentItem().text()
            command.append('--force-media-title=' + title)
        command += self.options.split()
        command.append(url)
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
        logging.debug("running process with pid:{}\n  {}".format(
            str(self.process.pid), str(command)))

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
        if not self.ui.guideBrowser.isVisible() \
                or self.ui.listWidget.count() < 1:
            return
        item = self.ui.listWidget.currentItem()
        data = item.data(Qt.UserRole) if item else None
        if data:
            date = datetime.date.today()
            if self.ui.guideNextButton.isChecked():
                date += datetime.timedelta(days=1)
            date_str = date.strftime("%Y%m%d")
            all_day = self.ui.guideNextButton.isChecked()\
                or self.ui.guideFullButton.isChecked()
            text = self.sh.get_schedule(date_str, data[1], all_day)\
                if self.sh else "loading…"
            self.ui.guideBrowser.setText(text)
            self.ui.guideBrowser.setToolTip(text)
        else:
            self.ui.guideBrowser.setText("<b>not available</b>")

    @pyqtSlot()
    def on_guideFullButton_released(self):
        self.ui.guideNextButton.setChecked(False)
        self.update_guide()

    @pyqtSlot()
    def on_guideNextButton_released(self):
        self.ui.guideFullButton.setChecked(False)
        self.update_guide()

    def copy_to_clipboard(self):
        data = self.ui.listWidget.currentItem().data(Qt.UserRole)
        if bool(data):
            QtWidgets.QApplication.clipboard().setText(data[0])

    def load_guide_wrapper(self):
        self.guide_worker = Worker(self.load_guide_archive)
        self.guide_worker.signals.signal_finished.connect(self.update_guide)
        self.thread_pool.start(self.guide_worker)

    def load_guide_archive(self):
        highlight_color = (self.palette().color(QPalette().Link)).name()
        self.sh = ScheduleHandler(self.guide_addr, highlight_color)

    def fold_everything(self):
        self.view_bookmarks_action.setChecked(False)
        for item in self.ui.listWidget.findItems("", Qt.MatchContains):
            item.setHidden((self.search_term.lower() not in item.text().lower()
                            or not self.folded) and bool(item.data(Qt.UserRole)))
        self.folded = not self.folded

    def show_settings(self):
        settings_dialog = SettingsDialog(self, self.settings_helper)
        settings_dialog.show()
        settings_dialog.destroyed.connect(self.load_settings)

    def show_guide_viewer(self):
        item = self.ui.listWidget.currentItem()
        channel = "" if not item else item.text()
        list = [(x.text(), x.data(Qt.UserRole)[1]) for x in self.ui.listWidget
                .findItems("", Qt.MatchContains) if bool(x.data(Qt.UserRole))]
        gv = GuideViewer(self, self.sh, list, channel)
        gv.show()
        self.guide_worker.signals.signal_finished.\
            connect(lambda: gv.reset_handler(self.sh))

    def show_timeshift_dialog(self):
        if self.ui.listWidget.count() < 1:
            return
        item = self.ui.listWidget.currentItem()
        data = item.data(Qt.UserRole) if item else None
        if data:
            title = self.ui.listWidget.currentItem().text()
            td = Timeshift(self, self.sh, title, data[1], self.settings_helper)
            td.show()
            td.start_player.connect(self.play)

    def bookmark_current(self):
        if self.ui.listWidget.count() < 1:
            return
        item = self.ui.listWidget.currentItem()
        data = item.data(Qt.UserRole)
        if data and data[1] not in self.bookmarks:
            self.bookmarks.append(data[1])
            item.setIcon(QIcon.fromTheme('folder-bookmark'))

    def bookmark_remove(self):
        if self.ui.listWidget.count() < 1:
            return
        item = self.ui.listWidget.currentItem()
        data = item.data(Qt.UserRole)
        if data and data[1] in self.bookmarks:
            self.bookmarks.remove(data[1])
            item.setIcon(QIcon.fromTheme('video-webm'))

    def view_bookmarks(self, check):
        for item in self.ui.listWidget.findItems("", Qt.MatchContains):
            data = item.data(Qt.UserRole)
            item.setHidden(
                (not check and self.search_term.lower() not in item.text().lower()
                 and bool(data))
                or
                (check and (self.search_term.lower() not in item.text().lower()
                            or not bool(data)
                            or (bool(data) and data[1] not in self.bookmarks))))
        self.set_focus()

    def show_about(self):
        QtWidgets.QMessageBox.about(
            self, "About tvnao",
            "<p><b>tvnao</b> v0.12.2 &copy; 2016-2023 Blaze</p>"
            "<p>&lt;blaze@vivaldi.net&gt;</p>"
            "<p><a href=\"https://launchpad.net/tvnao\">"
            "https://launchpad.net/tvnao</a></p>")

    def quit(self):
        self.settings.setValue('main/bookmarks', self.bookmarks)
        self.hide()
        self.thread_pool.waitForDone()
        self.close()


def main():
    if sys.hexversion < 0x030600f0:
        logging.error("E: python version is too old, 3.6 or higher needed")
        sys.exit(1)
    if 'linux' in sys.platform:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    app = QtWidgets.QApplication(sys.argv)
    tv_widget = MainWindow()
    tv_widget.setWindowIcon(QIcon.fromTheme('video-television'))
    tv_widget.show()
    sys.exit(app.exec_())
