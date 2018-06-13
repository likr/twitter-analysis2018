#!/usr/bin/env python
import json
from optparse import OptionParser
from utils import load_tweet


def main():
    parser = OptionParser()
    parser.add_option('-o', dest='filename', default='names.json',
                      help='output filename')
    options, args = parser.parse_args()

    names = {}
    for t in load_tweet(*args):
        names[t['user']['id']] = t['user']['screen_name']

    json.dump(names, open(options.filename, 'w'))


if __name__ == '__main__':
    main()
