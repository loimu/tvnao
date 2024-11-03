# Copyright (c) 2016-2023 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import os
import struct
import datetime
import sqlite3
import zipfile
import logging
from urllib import request, error
from typing import List
import encodings.idna


class ScheduleHandler:
    dbname = 'schedule.db'
    jtv_file = 'jtv.zip'
    db = None

    def __init__(self, schedule_addr: str,
                 highlight_color: str = 'indigo',
                 offset: float = 0.0,
                 cached_days_num: int = 5,
                 tz: datetime.tzinfo = None):
        if cached_days_num < 0:
            raise ValueError("The number of cached days shouldn't be negative")
        self.schedule_addr = schedule_addr
        self.highlight_color = highlight_color
        self.offset = offset
        self.cached_days_num = cached_days_num
        self.tz = tz
        self._set_prefix()
        self.db = sqlite3.connect(self.dbname, check_same_thread=False)
        self.c = self.db.cursor()
        refill = False
        if not os.path.getsize(self.dbname):
            self._create_database()
            refill = os.path.exists(self.jtv_file)
        dirty_flag = os.path.exists(self.dbname + "-journal")
        if self._download_file(self.schedule_addr, self.jtv_file)\
                or refill or dirty_flag:
            if dirty_flag or not refill:
                self._flush_database()
            self._add_to_database()

    def __del__(self):
        self.db.close()

    def _set_prefix(self) -> None:
        prefix = ""
        if 'win' in os.sys.platform:
            prefix = os.path.expandvars("%LOCALAPPDATA%\\tvnao\\")
        if 'linux' in os.sys.platform:
            prefix = os.path.expanduser(r"~/.cache/tvnao/")
        if prefix and not os.path.exists(prefix):
            os.makedirs(prefix)
        self.dbname = prefix + self.dbname
        self.jtv_file = prefix + self.jtv_file

    def _download_file(self, link: str, filename: str) -> bool:
        if not link:
            return False
        logging.info(f'downloading file {link}')
        try:
            response = request.urlopen(link)
        except error.URLError as e:
            logging.error("Connection error: {}".format(str(e.reason)))
            return False
        except ValueError as e:
            logging.error("Connection error: {}".format(str(e)))
            return False
        headers = dict(response.getheaders())
        if headers['Content-Type'] != 'application/zip':
            return False
        modified = headers['Last-Modified']
        jtv_check_file = filename.rsplit('.', maxsplit=1)[0]
        if os.path.exists(jtv_check_file):
            with open(jtv_check_file, 'r') as file:
                if file.read() == modified and os.path.exists(self.jtv_file):
                    logging.info(f'{filename} is up to date')
                    return False
        with open(jtv_check_file, 'w') as file:
            file.write(modified)
        with open(filename, 'wb') as file:
            file.write(response.read())
        if os.path.getsize(filename) < int(headers['Content-Length']):
            logging.error("Wrong file size")
            os.remove(jtv_check_file)
            return False
        return True

    def _create_database(self) -> None:
        logging.info(f'creating database {self.dbname}')
        self.c.execute("CREATE TABLE program "
                       "(channel text, start integer, stop integer, desc text,"
                       " primary key(channel, stop))")
        self.db.commit()

    def _parse_titles(self, data: bytes) -> List[str]:
        data = data[26:]
        titles = []
        while len(data) > 0:
            title_length = int(struct.unpack('<H', data[:2])[0])
            data = data[2:]
            try:
                title = data[:title_length].decode('utf-8')
            except UnicodeDecodeError:
                return titles
            data = data[title_length:]
            titles.append(title)
        return titles

    def _filetime_to_datetime(self, time: bytes) -> datetime.datetime:
        filetime = struct.unpack('<Q', time)[0]
        timestamp = filetime/10 + self.offset*3.6e9
        return datetime.datetime(1601, 1, 1)\
            + datetime.timedelta(microseconds=timestamp)

    def _parse_schedule(self, data: bytes) -> List[datetime.datetime]:
        schedules = []
        records_num = struct.unpack('<H', data[0:2])[0]
        data = data[2:]
        i = 0
        while i < records_num:
            i = i + 1
            record = data[0:12]
            data = data[12:]
            schedules.append(self._filetime_to_datetime(record[2:-2]))
        return schedules

    def _flush_database(self) -> None:
        """
            Flushes records omitting the records from cached days
        """
        logging.info(f'flushing database {self.dbname}')
        today = datetime.date.today()
        past_date = (today - datetime.timedelta(days=self.cached_days_num)).strftime("%Y%m%d000000")
        prev_date = (today - datetime.timedelta(days=1)).strftime("%Y%m%d235900")
        try:
            self.c.execute("DELETE FROM program WHERE start < ? OR start > ?",
                           (past_date, prev_date))
            self.db.commit()
        except sqlite3.Error as e:
            logging.error(f'Database error: {e}')
            os.remove(self.dbname)
            return
        self.c.execute("VACUUM")

    def _add_to_database(self) -> None:
        logging.info(f'writing into database {self.dbname}')
        archive = zipfile.ZipFile(self.jtv_file, 'r')
        today = int(datetime.date.today().strftime("%Y%m%d000000"))
        for filename in archive.namelist():
            if filename.endswith(".pdt"):
                try:
                    unicode_name = bytes(filename, 'cp437').decode('cp866')
                except ValueError:
                    unicode_name = bytes(filename, 'utf-8')
                channel_id = unicode_name[0:-4]
                if channel_id.isdigit():
                    continue
                titles = archive.read(filename)
                if titles[0:26] != b'JTV 3.x TV Program Data\n\n\n':
                    logging.warn("invalid JTV format")
                    continue
                channel_titles = self._parse_titles(titles)
                schedules = archive.read(filename[0:-4] + ".ndx")
                channel_schedules = self._parse_schedule(schedules)
                i = 0
                for entry in channel_titles:
                    if i < len(channel_schedules) - 1:
                        time_format = "%Y%m%d%H%M%S"
                        start = channel_schedules[i].strftime(time_format)
                        stop = channel_schedules[i+1].strftime(time_format)
                        i += 1
                        if int(start) >= today:
                            try:
                                self.c.execute(
                                    "INSERT INTO program VALUES (?,?,?,?)",
                                    (channel_id, start, stop, entry))
                            except sqlite3.IntegrityError:
                                pass
        archive.close()
        self.db.commit()
        logging.info(f'database {self.dbname} is ready')

    def _cut(self, text):
        return text if len(text) < 65 else text[:text.rfind('.', 0, 65)]

    def _get_current_time(self):
        return int(datetime.datetime.now(self.tz).strftime("%Y%m%d%H%M%S"))

    def get_schedule(self,
                     date: str, channel: str, full_day: bool = False) -> str:
        text = ""
        curr_color = self.highlight_color
        curr_time = self._get_current_time()
        format = lambda x, y, z: \
            "<tr{}><td><b>{}:{}</b></td><td><span>{}</span></td></tr>"\
            .format(x, str(y)[-6:-4], str(y)[-4:-2], z)
        if not full_day:
            for (start, note) in self.c.execute(
                    "SELECT start, desc FROM program "
                    "WHERE channel = ? AND stop > ? LIMIT 5;",
                    (channel, curr_time)):
                style = f" style='color:{curr_color};'" if curr_time > start else ""
                text += format(style, start, note)
        else:
            for (start, stop, note) in self.c.execute(
                    "SELECT start, stop, desc FROM program "
                    "WHERE channel = ? AND stop > ? AND start < ?;",
                    (channel, date + '000000', date + '235900')):
                if curr_time > start and curr_time > stop:
                    text += format(" style='color:grey;'", start, self._cut(note))
                elif curr_time > start and curr_time < stop:
                    text += format(f" style='color:{curr_color};'", start, note)
                else:
                    text += format("", start, self._cut(note))
        return "<table>{}</table>".format(
            text if text else "<tr><td>n/a</td></tr>")

    def get_overview(self, channel_map: dict) -> str:
        text = ""
        curr_time = self._get_current_time()
        format = lambda w, x, y, z: \
            "<tr><td>{}</td><td><b>{}:{}..{}:{}</b></td>"\
            "<td><span>{}</span></td></tr>\r\n"\
            .format(
                w, str(x)[-6:-4], str(x)[-4:-2], str(y)[-6:-4], str(y)[-4:-2], z)
        for (channel, start, stop, note) in self.c.execute(
                "SELECT channel, start, stop, desc FROM program "
                "WHERE start < ? AND stop > ? ORDER BY start DESC, stop ASC;",
                (curr_time + 1000, curr_time)):
            if channel in channel_map:
                text += format(channel_map[channel], start, stop, self._cut(note))
        return "<table>\r\n{}</table>".format(text)

    def get_timeshift_list(self, date: str, channel: str):
        curr_time = self._get_current_time()
        for (start, stop, note) in self.c.execute(
            "SELECT start, stop, desc FROM program "
            "WHERE channel = ? AND stop > ? AND (start < ? AND start < ?);",
                (channel, date + '000000', date + '235900', curr_time)):
            yield (start, stop,
                   "{}:{}".format(str(start)[-6:-4], str(start)[-4:-2]),
                   self._cut(note)
                   )

    def get_current_program(self, channel: str):
        note = ""
        curr_time = self._get_current_time()
        for (note,) in self.c.execute(
                "SELECT desc FROM program "
                "WHERE channel = ? AND stop > ? LIMIT 1;",
                (channel, curr_time)):
            pass
        return " -- " + self._cut(note) if len(note) else note
