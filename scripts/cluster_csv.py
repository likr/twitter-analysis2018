#!/usr/bin/env python
import json
import csv
from optparse import OptionParser


def main():
    parser = OptionParser()
    parser.add_option('-o', dest='filename', help='output filename')
    parser.add_option('--names', dest='names', default='data/names.json',
                      help='names filename')
    parser.add_option('--clusters', dest='clusters',
                      default='data/clusters.json',
                      help='clusters filename')
    options, args = parser.parse_args()

    names = json.load(open(options.names))
    clusters = json.load(open(options.clusters))

    writer = csv.writer(open(options.filename, 'w'))
    for key, value in clusters.items():
        writer.writerow([names[key], value])


if __name__ == '__main__':
    main()
