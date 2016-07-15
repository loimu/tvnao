# Copyright (c) 2016 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import sys
import zipfile
import struct
import argparse
import datetime
import sqlite3
import codecs
import requests
import os.path

def parse_titles(data):
    if data[0:26] != b'JTV 3.x TV Program Data\n\n\n':
        raise Exception('invalid JTV format')
    data = data[26:]
    titles = []
    while len(data) > 0:
        title_length = int(struct.unpack('<H', data[0:2])[0])
        data = data[2:]
        title = data[0:title_length].decode('cp1251')
        data = data[title_length:]
        titles.append(title)
    return titles

def filetime_to_datetime(time):
    filetime = struct.unpack("<Q", time)[0]
    timestamp = filetime/10
    return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=timestamp)

def parse_schedule(data):
    schedules = []
    records_num = struct.unpack('<H', data[0:2])[0]
    data = data[2:]
    i = 0
    while i < records_num:
        i = i + 1
        record = data[0:12]
        data = data[12:]
        schedules.append(filetime_to_datetime(record[2:-2]))
    return schedules

def download_file(link, filename):
    print('downloading file ' + filename)
    r = requests.get(link)
    with open(filename, "wb") as file:
        file.write(r.content)

def create_database(dbname):
    print('creating database ' + dbname)
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute('''CREATE TABLE channels
             (id integer not null primary key, name text)''')
    c.execute('''CREATE TABLE programme
             (channel integer, start integer, stop integer, desc text,
             primary key(channel, start, stop))''')
    conn.commit()
    conn.close()

def read_replacements(fname):
    result = {}
    if os.path.isfile(fname):
        repl_file = codecs.open(fname, 'r', 'utf-8')
        lines = repl_file.read().splitlines()
        repl_file.close()
        for line in lines:
            entry = line.split(',')
            if len(entry) > 1:
                result[entry[0]] = entry[1]
    return result

def add_to_database(dbname, jtv_filename):
    print('writing into database ' + dbname)
    replacements = read_replacements('replacement.txt')
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    archive = zipfile.ZipFile(jtv_filename, 'r')
    channel_id = 0
    for filename in archive.namelist():
        if filename.endswith('.pdt'):
            try:
                unicode_name = codecs.decode(bytes(filename, 'cp437'), 'cp866')
            except ValueError:
                unicode_name = bytes(filename, 'utf-8')
            channel_name = unicode_name[0:-4].replace('_', ' ')
            if channel_name in replacements:
                channel_name = replacements[channel_name]
            channel_id += 1
            channel = (channel_id, channel_name, )
            c.execute('INSERT INTO channels VALUES (?,?)', channel)
    channel_id = 0
    for filename in archive.namelist():
        if filename.endswith('.pdt'):
            channel_id += 1
            titles = archive.read(filename)
            channel_titles = parse_titles(titles)
            schedules = archive.read(filename[0:-4] + ".ndx")
            channel_schedules = parse_schedule(schedules)
            i = 0
            for curr_title in channel_titles:
                if i < len(channel_schedules) - 1:
                    time_format = '%Y%m%d%H%M%S'
                    programme = (channel_id,
                                 channel_schedules[i].strftime(time_format),
                                 channel_schedules[i+1].strftime(time_format),
                                 curr_title,
                                 )
                    c.execute('INSERT INTO programme VALUES (?,?,?,?)', programme)
                    i += 1
    archive.close()
    conn.commit()
    conn.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--link', required=True)
    args = parser.parse_args()
    filename = 'jtv.zip'
    dbname = 'schedule.db'
    download_file(args.link, filename)
    create_database(dbname)
    add_to_database(dbname, filename)

if __name__ == "__main__":
    main()
