#!/usr/bin/env python
import csv
import json
from optparse import OptionParser
from scipy.spatial.distance import pdist
from scipy.cluster import hierarchy
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from gensim.models.doc2vec import Doc2Vec
import matplotlib
from utils import load_names

matplotlib.use('Agg')


ignore_ids = {
    '81015518',
    '86217842',
    '242156036',
    '269125621',
    '275807989',
}


def main():
    from matplotlib import pyplot as plt

    parser = OptionParser()
    parser.add_option('--model', dest='model',
                      default='twitter.model', help='model filename')
    parser.add_option('--names', dest='names', default='data/names.json',
                      help='names filename')
    options = parser.parse_args()[0]

    names = load_names(options.names)
    model = Doc2Vec.load(options.model)

    print(len(list(model.docvecs)))

    influencers = [str(uid) for uid in json.load(open('influencers.json'))]
    influencers = [uid for uid in influencers
                   if uid in model.docvecs and uid not in ignore_ids]
    print(len(influencers))
    vectors = [model.docvecs[uid] for uid in influencers]
    tsne = TSNE()
    tsne.fit(vectors)
    print(tsne.kl_divergence_)
    positions = tsne.fit_transform(vectors)

    vectors_writer = csv.writer(open('vectors.csv', 'w'))
    positions_writer = csv.writer(open('positions.csv', 'w'))
    positions_writer.writerow(['name', 'id', 'x', 'y'])
    for uid, vector, position in zip(influencers, vectors, positions):
        name = names.get(int(uid), '')
        vectors_writer.writerow([name, uid] + list(vector))
        positions_writer.writerow([name, uid] + list(position))

    X = [[float(v) for v in row[2:]] for row in vectors]
    print(X[0])
    y = pdist(X)
    Z = hierarchy.linkage(y)
    print(hierarchy.fcluster(Z, 1))
    plt.xlabel('sample index')
    plt.ylabel('distance')
    hierarchy.dendrogram(Z)
    plt.savefig('hoge.pdf')

    for k in range(2, 31):
        kmeans = KMeans(n_clusters=k, n_init=1000, max_iter=1000).fit(X)
        print('{}\t{}'.format(k, kmeans.inertia_))

    k = 7
    kmeans = KMeans(n_clusters=k, n_init=10000, max_iter=1000).fit(X)
    writer = csv.writer(open('cluster.csv', 'w'))
    writer.writerow(['name', 'id', 'label', 'x']
                    + ['y{}'.format(i) for i in range(k)])
    for uid, l, row in zip(influencers, kmeans.labels_, positions):
        name = names.get(int(uid), '')
        x, y = row
        cols = ['' for _ in range(k)]
        cols[l] = y
        writer.writerow([name, uid] + [l, x] + cols)

    clusters = {uid: int(l) for uid, l in zip(influencers, kmeans.labels_)}
    print(clusters)
    json.dump(clusters, open('clusters.json', 'w'))


if __name__ == '__main__':
    main()
