# Copyright (c) 2016-2019 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import os
import struct
import datetime
import sqlite3
import zipfile
from urllib import request, error
from typing import List
import encodings.idna


class ScheduleHandler:
    dbname = 'schedule.db'
    jtv_file = 'jtv.zip'
    db = None

    def __init__(self, schedule_addr: str,
                 offset: float = 0.0,
                 tz: datetime.tzinfo = None):
        self.schedule_addr = schedule_addr
        self.offset = offset
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
            print(prefix)
        if 'linux' in os.sys.platform:
            prefix = os.path.expanduser(r"~/.cache/tvnao/")
        if prefix and not os.path.exists(prefix):
            os.makedirs(prefix)
        self.dbname = prefix + self.dbname
        self.jtv_file = prefix + self.jtv_file

    def _download_file(self, link: str, filename: str) -> bool:
        if not link:
            return False
        print("downloading file", link)
        try:
            response = request.urlopen(link)
        except error.URLError as e:
            print("Connection error:", str(e.reason))
            return False
        except ValueError as e:
            print("Connection error:", str(e))
            return False
        headers = dict(response.getheaders())
        if headers['Content-Type'] != 'application/zip':
            return False
        modified = headers['Last-Modified']
        jtv_check_file = filename.rsplit('.', maxsplit=1)[0]
        if os.path.exists(jtv_check_file):
            with open(jtv_check_file, 'r') as file:
                if file.read() == modified and os.path.exists(self.jtv_file):
                    print(filename, "is up to date")
                    return False
        with open(jtv_check_file, 'w') as file:
            file.write(modified)
        with open(filename, 'wb') as file:
            file.write(response.read())
        if os.path.getsize(filename) < int(headers['Content-Length']):
            print("Wrong File Size")
            os.remove(jtv_check_file)
            return False
        return True

    def _create_database(self) -> None:
        print("creating database", self.dbname)
        self.c.execute("CREATE TABLE program "
                       "(channel text, start integer, stop integer, desc text,"
                       " primary key(channel, start, stop))")
        self.db.commit()

    def _parse_titles(self, data: bytes) -> List[str]:
        data = data[26:]
        titles = []
        while len(data) > 0:
            title_length = int(struct.unpack('<H', data[0:2])[0])
            data = data[2:]
            title = data[0:title_length].decode('cp1251')
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
        print("flushing database", self.dbname)
        try:
            self.c.execute("DELETE FROM program")
            self.db.commit()
        except sqlite3.Error as e:
            print("Database Error:", e)
            os.remove(self.dbname)
            return
        self.c.execute("VACUUM")

    def _add_to_database(self) -> None:
        print("writing into database", self.dbname)
        archive = zipfile.ZipFile(self.jtv_file, 'r')
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
                if titles[0:26] != b"JTV 3.x TV Program Data\n\n\n":
                    print("invalid JTV format")
                    continue
                channel_titles = self._parse_titles(titles)
                schedules = archive.read(filename[0:-4] + ".ndx")
                channel_schedules = self._parse_schedule(schedules)
                i = 0
                for curr_title in channel_titles:
                    if i < len(channel_schedules) - 1:
                        time_format = "%Y%m%d%H%M%S"
                        entry = (channel_id,
                                 channel_schedules[i].strftime(time_format),
                                 channel_schedules[i+1].strftime(time_format),
                                 curr_title,
                                 )
                        self.c.execute("INSERT INTO program VALUES (?,?,?,?)",
                                       entry)
                        i += 1
        archive.close()
        self.db.commit()

    def get_schedule(self,
                     date: str, channel: str, full_day: bool = False) -> str:
        currtime = int(datetime.datetime.now(self.tz).strftime("%Y%m%d%H%M%S"))
        format = lambda x: "<tr{0}><td><b>{1}:{2}</b></td>"\
                           "<td><span>{3}</span></td></tr>"\
            .format(x[0], str(x[1])[-6:-4], str(x[1])[-4:-2], x[2])
        text = ""
        if not full_day:
            select = (channel, currtime)
            for r in self.c.execute("SELECT * FROM program WHERE channel = ?"
                                    " AND stop > ? LIMIT 5 ;", select):
                style = " style='color:indigo;'" if currtime > r[1] else ""
                text += format((style, r[1], r[3]))
        else:
            select = (channel, str(date)+'000000', str(date)+'235900')
            for r in self.c.execute("SELECT * FROM program WHERE channel = ?"
                                    " AND stop > ? AND start < ? ;", select):
                if currtime > r[1] and currtime > r[2]:
                    text += format((" style='color:gray;'", r[1], r[3][:60]))
                elif currtime > r[1] and currtime < r[2]:
                    text += format((" style='color:indigo;'", r[1], r[3]))
                else:
                    text += format(("", r[1], r[3][:60]))
        return "<table>{}</table>".format(
            text if text else "<tr><td>n/a</td></tr>")
