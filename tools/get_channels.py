# Copyright (c) 2016-2017 Blaze <blaze@vivaldi.net>
# Licensed under the GNU General Public License, version 3 or later.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import argparse
import requests
import re


def save_index(epg_url):
    aliases = {}
    with open('replacements.txt', 'r') as replacements:
        content = replacements.read()
    for line in content.splitlines():
        entry = line.split(',')
        aliases[entry[1]] = entry[0]
    r = requests.get(epg_url)
    content = r.content.decode('utf-8')
    objects = re.finditer('id=\'(\d{1,7}?)\'.*?&nbsp;(.*?)\</td', content,
                          flags=re.DOTALL)
    with open('channels.txt', 'w') as channels:
        for o in objects:
            name = aliases[o.group(2)] if o.group(2) in aliases else o.group(2)
            channels.write('%s,%s\n' % (name, o.group(1)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--link', required=True,
                        help='web link to epg index page')
    args = parser.parse_args()
    save_index(args.link)

if __name__ == "__main__":
    main()
