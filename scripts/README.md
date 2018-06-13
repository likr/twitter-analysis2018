# Analysis Scripts

## Requirements

* Python3
* [MeCab](https://github.com/taku910/mecab) with mecab-ipadic
* [mecab-ipadic-NEologd](https://github.com/neologd/mecab-ipadic-neologd)
* [scipy](https://www.scipy.org/)
* [scikit-learn](http://scikit-learn.org/stable/index.html)
* [gensim](https://radimrehurek.com/gensim/)
* [networkx](https://networkx.github.io/)

## Contents

* names.py - collect user id and name
* create_twitter_corpus.py - create corpus file from twitter text
* create_wikipedia_corpu.py - create corpus file from wikipedia text
* d2v_learn.py - learn Doc2Vec model from corpuses
* d2v_classification.py - classify users using learned model
* retweet_timeseries.py - aggregate daily retweets for each cluster
* influencer_graph.py - construct influencer graph
