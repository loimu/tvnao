# Copyright (c) 2016-2017 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from http.server import HTTPServer, BaseHTTPRequestHandler
from os import curdir, sep
from urllib.parse import parse_qs
from pytz import timezone
import sqlite3
import codecs
import datetime
import argparse

# get hh:mm formatted string
ftime = lambda x: str(x)[-6:-4] + ':' + str(x)[-4:-2]
# get formatted output
formt = lambda x: '<tr><td{0}>{1}</td><td{0}><span>{2}</span></td></tr>'\
    .format(x[0], ftime(x[1]), x[2])
# get timezone
timezone = timezone('Europe/Minsk')

conn = sqlite3.connect('schedule.db')
c = conn.cursor()


class customHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/epg":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response = '<table>'
            for r in c.execute('SELECT * FROM channels ;'):
                response += '<tr><td id=\'%s\' >&nbsp;%s</td></tr>'\
                    % (r[0], r[1], )
            response += '</table>'
            self.wfile.write(bytes(response, 'utf-8'))
        return

    def do_POST(self):
        if self.path == "/viewProgram":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            length = int(self.headers['Content-Length'])
            fields = parse_qs(codecs.decode(self.rfile.read(length)), 'utf-8')
            channel = fields['id'][0]
            date = fields['date'][0]
            today = datetime.datetime.now(timezone).strftime("%Y%m%d")
            currtime = today + datetime.datetime.now(timezone)\
                .strftime("%H%M%S")
            response = '<div class=\'title\'>&nbsp;&nbsp;0</div><hr><table>'
            if 'toggle_now_day' in fields['schedule'] and today == date:
                select = (channel, currtime, )
                for r in c.execute('''SELECT * FROM programme WHERE channel = ?
                                    AND stop > ? LIMIT 5 ;''', select):
                    ins = ' class=\'in\'' if currtime > str(r[1]) else ''
                    response += formt((ins, r[1], r[3]))
            if 'toggle_all_day' in fields['schedule'] or today != date:
                begin = date + '000000'
                end = date + '235900'
                select = (channel, begin, end, )
                for r in c.execute('''SELECT * FROM programme WHERE channel = ?
                                AND stop > ? AND start < ? ;''', select):
                    if currtime > str(r[1]) and currtime > str(r[2]):
                        response += formt((' class=\'before\'', r[1], r[3]))
                    elif currtime > str(r[1]) and currtime < str(r[2]):
                        response += formt((' class=\'in\'', r[1], r[3]))
                    else:
                        response += formt(('', r[1], r[3]))
            if len(response) < 50:
                response += '<tr><td>n/a</td></tr>'
            response += '</table><hr>'
            self.wfile.write(bytes(response, 'utf-8'))
        return


def run(host, port):
    server_address = (host, port)
    print('listening on %s:%s' % server_address)
    httpd = HTTPServer(server_address, customHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        conn.close()
        print('\nexiting')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--host', default='localhost')
    parser.add_argument('-p', '--port', default=8089, type=int)
    args = parser.parse_args()
    run(args.host, args.port)

if __name__ == "__main__":
    main()
