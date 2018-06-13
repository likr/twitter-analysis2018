#!/usr/bin/env python
import csv
import json
from optparse import OptionParser
from utils import divide_text


def main():
    parser = OptionParser()
    parser.add_option('-o', '--output', dest='output',
                      default='words.csv', help='output filename')
    options, args = parser.parse_args()

    writer = csv.writer(open(options.output, 'w'))
    for filename in args:
        for row in open(filename):
            data = json.loads(row)
            writer.writerow(['wp' + data['id'], divide_text(data['text'])])


if __name__ == '__main__':
    main()
