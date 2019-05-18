# Copyright (c) 2016-2019 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import argparse
from pytz import timezone

from schedule_handler import ScheduleHandler

sh = None
tz = timezone('Europe/Minsk')


class customHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/viewProgram":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            length = int(self.headers['Content-Length'])
            fields = parse_qs(self.rfile.read(length).decode('utf-8'))
            channel = fields['id'][0]
            date = fields['date'][0]
            full_day = 'toggle_all_day' in fields['schedule']
            response = sh.get_schedule(date, channel, full_day)
            self.wfile.write(bytes(response, 'utf-8'))
        return


def run(host, port):
    server_address = (host, port)
    print("listening on %s:%s" % server_address)
    httpd = HTTPServer(server_address, customHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nexiting")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--host', default='localhost')
    parser.add_argument('-p', '--port', default=8089, type=int)
    parser.add_argument('-u', '--url', required=True, help="jtv file source")
    args = parser.parse_args()
    global sh
    sh = ScheduleHandler(args.url, tz=tz)
    run(args.host, args.port)


if __name__ == "__main__":
    main()
