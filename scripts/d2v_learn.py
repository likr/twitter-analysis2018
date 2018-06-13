#!/usr/bin/env python
import csv
from optparse import OptionParser
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import LabeledSentence


csv.field_size_limit(1000000000)


def load_documents(*filenames):
    for filename in filenames:
        for tid, words in csv.reader(open(filename)):
            yield LabeledSentence(words=words.split(), tags=[tid])


def main():
    parser = OptionParser()
    parser.add_option('--model', dest='model',
                      default='twitter.model', help='model output filename')
    parser.add_option('--vocabulary-output', dest='vocabulary',
                      default='vocabulary.csv', help='model filename')
    options, args = parser.parse_args()

    documents = list(load_documents(*args))
    model = Doc2Vec(documents, workers=16)
    model.save(options.model)

    vocabulary = {}
    for doc in documents:
        for word in doc.words:
            if word not in vocabulary:
                vocabulary[word] = 0
            vocabulary[word] += 1
    vocabulary_writer = csv.writer(open(options.vocabulary, 'w'))
    items = list(vocabulary.items())
    items.sort(key=lambda v: v[1], reverse=True)
    for k, v in items:
        vocabulary_writer.writerow([k, v])


if __name__ == '__main__':
    main()
