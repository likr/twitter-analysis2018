#!/usr/bin/env python
import csv
from datetime import timedelta
from optparse import OptionParser
from utils import load_tweet, load_clusters
from utils import group_by_influencer, group_by_hour
from utils import filter_by_datetime
from utils import datetime_range, ymd_to_datetime


def main():
    parser = OptionParser()
    parser.add_option('-o', dest='filename', default='retweet_timeseries.csv',
                      help='output filename')
    parser.add_option('--clusters', dest='clusters',
                      default='data/clusters.json',
                      help='clusters filename')
    parser.add_option('--start', dest='start', default='20110301',
                      help='start date (default=20110301)')
    parser.add_option('--stop', dest='stop', default='20130401',
                      help='stop date (default=20130401)')
    parser.add_option('--influencers', dest='n', type='int', default=None,
                      help='maximum number of influencers (default=inf)')
    parser.add_option('--mincount', dest='mincount', type='int', default=1,
                      help='minimum number of retweet (default=1)')
    options, args = parser.parse_args()

    start_date = ymd_to_datetime(options.start)
    stop_date = ymd_to_datetime(options.stop)
    cluster_map = load_clusters(options.clusters)
    clusters = list(set(cluster_map.values()))
    days = [d.strftime('%Y%m%d%H') for d
            in datetime_range(start_date, stop_date, timedelta(hours=1))]

    count = {}
    for c in clusters:
        count[c] = {}
        for d in days:
            count[c][d] = 0

    tweets = load_tweet(*args)
    tweets = filter_by_datetime(tweets, start_date, stop_date)
    for ruid, tss in group_by_influencer(tweets, options.n, options.mincount):
        if ruid in cluster_map:
            cluster = cluster_map[ruid]
            for day, ts in group_by_hour(tss):
                count[cluster][day] += len(list(ts))

    writer = csv.writer(open(options.filename, 'w'))
    writer.writerow(['date'] + clusters)
    for d in days:
        writer.writerow([d] + [count[c][d] for c in clusters])


if __name__ == '__main__':
    main()
