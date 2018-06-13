#!/usr/bin/env python
import json
import random
from bisect import bisect_right
from optparse import OptionParser
import networkx as nx
from networkx.readwrite import json_graph
from utils import load_tweet, load_names, load_clusters
from utils import group_by_user, group_by_influencer
from utils import sampling, filter_by_datetime
from utils import weeks_between, months_between, to_datetime, ymd_to_datetime


def main():
    parser = OptionParser()
    parser.add_option('-o', dest='filename', default='graph.gexf',
                      help='output filename')
    parser.add_option('--names', dest='names', default='data/names.json',
                      help='names filename')
    parser.add_option('--clusters', dest='clusters',
                      default='data/clusters.json',
                      help='clusters filename')
    parser.add_option('--start', dest='start', default='20110301',
                      help='start date (default=20110301)')
    parser.add_option('--stop', dest='stop', default='20130401',
                      help='stop date (default=20130401)')
    parser.add_option('--sampling', dest='sampling', type='float', default=1.0,
                      help='tweet sampling rate (default=1.0)')
    parser.add_option('--influencers', dest='n', type='int', default=None,
                      help='maximum number of influencers (default=inf)')
    parser.add_option('--mincount', dest='mincount', type='int', default=1,
                      help='minimum number of retweet (default=1)')
    parser.add_option('--mindegree', dest='mindegree', type='int', default=0,
                      help='minimum acceptable degree of nodes (default=0)')
    parser.add_option('--group', dest='group', default='month',
                      help='month or week (default=month)')
    options, args = parser.parse_args()

    names = load_names(options.names)
    clusters = load_clusters(options.clusters)
    start_date = ymd_to_datetime(options.start)
    stop_date = ymd_to_datetime(options.stop)

    tweets = load_tweet(*args)
    tweets = filter_by_datetime(tweets, start_date, stop_date)
    random.seed(0)
    tweets = sampling(tweets, options.sampling)

    if options.group == 'month':
        groups = [t.strftime('t%Y%m%d') for t
                  in months_between(start_date, stop_date)]
    else:
        groups = [t.strftime('t%Y%m%d') for t
                  in weeks_between(start_date, stop_date)]

    graph = nx.DiGraph()
    graph.graph['groups'] = groups
    for ruid, tss in group_by_influencer(tweets, options.n, options.mincount):
        for uid, ts in group_by_user(tss):
            ts = list(ts)
            labels = {d: False for d in groups}
            for t in ts:
                d = to_datetime(t['created_at']).strftime('t%Y%m%d')
                labels[groups[bisect_right(groups, d) - 1]] = True
            graph.add_edge(ruid, uid, weight=len(ts), **labels)

    for node in graph.nodes():
        if graph.degree(node, 'weight') < options.mindegree:
            graph.remove_node(node)
            continue
        graph.node[node]['label'] = names.get(node, '')
        graph.node[node]['cluster'] = clusters.get(node, -1)
        if graph.out_degree(node) == 0:
            cluster_count = {}
            for ruid in graph.predecessors(node):
                c = clusters.get(ruid, -1)
                if c not in cluster_count:
                    cluster_count[c] = 0
                cluster_count[c] += 1
            graph.node[node]['cluster'] = max(cluster_count.items(),
                                              key=lambda r: r[1])[0]
        for d in groups:
            graph.node[node][d] = False

    for d in groups:
        for u, v in graph.edges():
            if graph[u][v][d]:
                graph.node[u][d] = True
                graph.node[v][d] = True

    out_format = options.filename.split('.')[-1]
    if out_format == 'gexf':
        nx.write_gexf(graph, options.filename)
    else:
        obj = json_graph.node_link_data(graph)
        json.dump(obj, open(options.filename, 'w'))
    print('(|V|, |E|) = ({}, {})'.format(graph.number_of_nodes(),
                                         graph.number_of_edges()))


if __name__ == '__main__':
    main()
