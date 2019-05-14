# Copyright (c) 2016-2019 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import os
import requests
import struct
import datetime
import sqlite3
import codecs
import zipfile
from pytz import timezone
from typing import List


class ScheduleHandler:
    dbname = 'schedule.db'
    jtv_file = 'jtv.zip'
    tz = timezone('Europe/Minsk')

    def __init__(self, schedule_addr: str = "http://iptv.isp.domain/jtv.zip",
                 offset: float = 0.0):
        self.schedule_addr = schedule_addr
        self.offset = offset
        self._set_prefix()
        self.conn = sqlite3.connect(self.dbname)
        self.c = self.conn.cursor()
        refill = False
        if not os.path.getsize(self.dbname):
            self._create_database()
            if os.path.exists(self.jtv_file):
                refill = True
        if self._download_file(self.schedule_addr, self.jtv_file) or refill:
            if not refill:
                self._flush_database()
            self._add_to_database()

    def __del__(self):
        self.conn.close()

    def _set_prefix(self):
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
        print("downloading file", link)
        try:
            response = requests.head(link)
        except requests.exceptions.ConnectionError as e:
            print("Connection error:", e)
            return False
        length = int(response.headers['Content-Length'])
        modified = response.headers['Last-Modified']
        if length < 100000:
            return False
        jtv_check_file = filename.rsplit('.', maxsplit=1)[0]
        if os.path.exists(jtv_check_file):
            with open(jtv_check_file, 'r') as file:
                if file.read() == modified and os.path.exists(self.jtv_file):
                    print(filename, "is up to date")
                    return False
        with open(jtv_check_file, 'w') as file:
            file.write(modified)
        try:
            response = requests.get(link)
        except requests.exceptions.ConnectionError as e:
            print("Connection Error:", e)
            return False
        with open(filename, 'wb') as file:
            file.write(response.content)
        if os.path.getsize(filename) < length:
            print("Wrong File Size")
            os.remove(jtv_check_file)
            return False
        return True

    def _create_database(self) -> None:
        print("creating database", self.dbname)
        self.c.execute("CREATE TABLE program "
                       "(channel text, start integer, stop integer, desc text,"
                       " primary key(channel, start, stop))")
        self.conn.commit()

    def _parse_titles(self, data: bytes) -> List[str]:
        if data[0:26] != b"JTV 3.x TV Program Data\n\n\n":
            raise Exception("invalid JTV format")
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
        timestamp = filetime/10 + self.offset * 3.6e+9
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
            self.conn.commit()
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
                    unicode_name = codecs.decode(bytes(filename, 'cp437'),
                                                 'cp866')
                except ValueError:
                    unicode_name = bytes(filename, 'utf-8')
                channel_id = unicode_name[0:-4]
                if channel_id.isdigit():
                    continue
                titles = archive.read(filename)
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
        self.conn.commit()

    def get_schedule(self,
                     date: str, channel: str, full_day: bool = False) -> str:
        currtime = int(datetime.datetime.now(self.tz).strftime("%Y%m%d%H%M%S"))
        response = "<table>"
        format = lambda x: "<tr{0}><td><b>{1}:{2}</b></td>"\
                           "<td><span>{3}</span></td></tr>"\
            .format(x[0], str(x[1])[-6:-4], str(x[1])[-4:-2], x[2])
        if not full_day:
            select = (channel, currtime, )
            for r in self.c.execute("SELECT * FROM program WHERE channel = ?"
                                    " AND stop > ? LIMIT 5 ;", select):
                ins = " style='color:indigo;'" if currtime > r[1] else ""
                response += format((ins, r[1], r[3]))
        else:
            begin = str(date) + '000000'
            end = str(date) + '235900'
            select = (channel, begin, end, )
            for r in self.c.execute("SELECT * FROM program WHERE channel = ?"
                                    " AND stop > ? AND start < ? ;", select):
                if currtime > r[1] and currtime > r[2]:
                    response += format((" style='color:gray;'",
                                        r[1], r[3][:65]))
                elif currtime > r[1] and currtime < r[2]:
                    response += format((" style='color:indigo;'", r[1], r[3]))
                else:
                    response += format(("", r[1], r[3][:65]))
        if len(response) < 50:
            response += "<tr><td>n/a</td></tr>"
        response += "</table>"
        return response
