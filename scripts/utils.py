import random
import json
from datetime import datetime, timezone, timedelta
from itertools import groupby
import MeCab


mecab = MeCab.Tagger('-d /var/lib/mecab/dic/ipadic-utf8')
mecab.parse('')
features = {
    '接頭詞',
    '名詞',
    'フィラー',
    '副詞',
    'その他',
    '接続詞',
    '動詞',
    '連体詞',
    '感動詞',
    '助詞',
    '助動詞',
    'BOS/EOS',
    '形容詞',
}


def load_tweet(*filenames):
    for filename in filenames:
        for s in open(filename):
            yield json.loads(s)


def load_names(filename):
    return {int(uid): name for uid, name
            in json.load(open(filename)).items()}


def load_clusters(filename):
    return {int(uid): int(cluster) for uid, cluster
            in json.load(open(filename)).items()}


def user_id(t):
    return t['user']['id']


def retweeted_user_id(t):
    return t['retweeted_status']['user']['id']


def group_by_user(tweets):
    tweets = list(tweets)
    tweets.sort(key=user_id)
    return groupby(tweets, user_id)


def group_by_retweeted_user(tweets):
    tweets = list(filter_retweet(tweets))
    tweets.sort(key=retweeted_user_id)
    return groupby(tweets, retweeted_user_id)


def group_by_influencer(tweets, n, min_count):
    tweets = [(ruid, list(tss))
              for ruid, tss in group_by_retweeted_user(tweets)]
    tweets.sort(key=lambda r: len(r[1]), reverse=True)
    if n is None:
        n = len(tweets)
    for ruid, tss in tweets[:n]:
        if len(tss) >= min_count:
            yield (ruid, tss)


def group_by_hour(tweets):
    def date(t):
        d = to_datetime(t['created_at'])
        return d.strftime('%Y%m%d%H')
    tweets = list(tweets)
    tweets.sort(key=date)
    return groupby(tweets, date)


def group_by_day(tweets):
    def date(t):
        d = to_datetime(t['created_at'])
        return d.strftime('%Y%m%d')
    tweets = list(tweets)
    tweets.sort(key=date)
    return groupby(tweets, date)


def count_retweet(tweets):
    return {ruid: len(list(items)) for ruid, items
            in group_by_retweeted_user(tweets)}


def find_influencers(tweets, max_influencers=None, min_count=1):
    count = count_retweet(tweets)
    influencers = [r for r in count.items() if r[1] >= min_count]
    influencers.sort(key=lambda r: r[1], reverse=True)
    n = len(influencers) if max_influencers is None else max_influencers
    return [r[0] for r in influencers[:n]]


def sampling(tweets, rate):
    return filter(lambda t: random.random() < rate, tweets)


def filter_retweet(tweets):
    return filter(lambda t: 'retweeted_status' in t, tweets)


def filter_by_datetime(tweets, start, stop):
    return filter(lambda t: start <= to_datetime(t['created_at']) <= stop,
                  tweets)


def to_datetime(s):
    t = datetime.strptime(s, '%a %b %d %H:%M:%S %z %Y')
    return t.astimezone(jst())


def ymd_to_datetime(s):
    t = datetime.strptime(s, '%Y%m%d')
    return jstdatetime(t.year, t.month, t.day)


def datetime_range(start, stop, delta):
    t = start
    while t <= stop:
        yield t
        t += delta


def jstdatetime(year, month, day):
    return datetime(year, month, day, tzinfo=jst())


def jst():
    return timezone(timedelta(hours=9))


def weeks_between(start, stop):
    d = jstdatetime(start.year, start.month, start.day)
    stop = jstdatetime(stop.year, stop.month, stop.day)
    delta = timedelta(days=7)
    while d <= stop:
        yield d
        d += delta


def months_between(start, stop):
    d = jstdatetime(start.year, start.month, 1)
    while (d.year, d.month) <= (stop.year, stop.month):
        yield d
        if d.month == 12:
            d = jstdatetime(d.year + 1, 1, 1)
        else:
            d = jstdatetime(d.year, d.month + 1, 1)


def parse(text):
    node = mecab.parseToNode(text)
    while node:
        yield [node.surface] + node.feature.split(',')
        node = node.next


def divide_text(text):
    return ' '.join(node[7] for node in parse(text)
                    if node[1] in features and node[7] != '*')
