#!/usr/bin/env python
import csv
from optparse import OptionParser
from utils import load_tweet, divide_text


def main():
    parser = OptionParser()
    parser.add_option('-o', '--output', dest='output',
                      default='words.csv', help='output filename')
    options, args = parser.parse_args()

    writer = csv.writer(open(options.output, 'w'))
    for t in load_tweet(*args):
        if 'retweeted_status' in t:
            continue
        writer.writerow([t['user']['id_str'], divide_text(t['text'])])


if __name__ == '__main__':
    main()
