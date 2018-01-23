import json
from multiprocessing.pool import Pool

import simhash
import numpy as np
import re
from urllib.parse import urlparse

import itertools
from collections import defaultdict, namedtuple

import dateutil.parser

import enrich


def flatten(list2d):
    return list(itertools.chain(*list2d))

def load(fn):
    with open(fn, 'r') as fin:
        for line in fin:
            yield json.loads(line)

def mapvalues(f, d):
    ret = {}
    for k, v in d.items():
        ret[k] = f(v)
    return ret

def get_root(d):
    o = urlparse(d['resource_url']).netloc
    a = re.sub(r"^.*\.([^.]*\.[^.]*)$", r"\1", o)
    return re.sub(r'\.', r'-', a)

INDEX={}

def get_index(w):
    if w not in INDEX:
        INDEX[w] = len(INDEX)
    return INDEX[w]


def tag_features(d):
    vec = []
    for t in d['geneea/tags']:
        key, score = t['text'], t['score']
        vec.append((get_index(key), score))
    return vec


def topic_features(d):
    vec = []
    for t in d['geneea/topic']:
        key, score = t['label'], t['confidence']
        vec.append((get_index(key), score))
    return vec


def entity_features(d):
    vec = []
    for t in d['geneea/entities']:
        key, instances = t['name'], t['instances']
        vec.append((get_index(key), len(instances)))
    return vec


def compute_simhash(text):
    tokens = re.split(r'\W+', text.lower(), flags=re.UNICODE)
    shingles = [''.join(shingle) for shingle in
                simhash.shingle(''.join(tokens), 4)]
    hashes = [simhash.unsigned_hash(s.encode('utf8')) for s in shingles]
    return simhash.compute(hashes)


hashing = True


def one(d):
    if hashing:
        hash = compute_simhash(d['text'])
        d['text_simhash'] = hash
    d['date_parsed'] = dateutil.parser.parse(d['date'])
    #d['tuple_features'] = topic_features(d) + entity_features(d) + tag_features(d)
    root = get_root(d)
    root = root + "_" + d['LABEL']
    d['root_url'] = root
    return d


print("STARTING")
data = []
with Pool(4) as p:
     for d in p.imap_unordered(one, load("ALL.big")):
         data.append(d)

print("ALL DATA")

data.sort(key=lambda t: t['date_parsed'])
by_hash = defaultdict(list)
by_root = defaultdict(list)
for i, d in enumerate(data):
    root = d['root_url']
    by_root[root].append(d)
    if hashing:
        by_hash.setdefault(d['text_simhash'], []).append(i)

print("ALL DATA 2")

if hashing:
    matching_hashes = simhash.find_all(by_hash.keys(), 8, 6)

print("MATCHNING")

matching_indices = {}

if hashing:
    for a, b in matching_hashes:
        for i in by_hash[a]:
            for j in by_hash[b]:
                matching_indices.setdefault(i, set()).add(j)
                matching_indices.setdefault(j, set()).add(i)


# zacinam z minimalniho i

follower = {}
following = {}

def print_trace(i, visited, offset=0):
    for old in visited:
        f = follower.setdefault(old, {})
        f[i] = f.get(i, 0) + 1

        f = following.setdefault(i, {})
        f[old] = f.get(old, 0) + 1

    assert i in matching_indices
    if False:
        off = " "*offset
        print(off, "="*5)
        print(off, i)
        print(off, data[i]['subject'])
        print(off, data[i]['resource_url'])
        print(off, data[i]['date'])

    visited |= set((i,))

    for j in matching_indices[i]:
        if j > i and j not in visited:
            print_trace(j, visited, offset + 2)

for i in sorted(matching_indices.keys()):
    visited = set()
    print_trace(i, visited)

print("ALL MATCHINGS")

def url(i):
    return data[i]['root_url']

RESULTS = {}
for source, sinks in follower.items():
    if any(sink != source for sink, _ in sinks.items()):
        RESULTS.setdefault(url(source), {})['followers'] = {
            url(sink) : score for sink, score in sinks.items()
            if url(sink) != url(source)
        }
for sink, sources in following.items():
    if any(sink != source for source, _ in sources.items()):
        RESULTS.setdefault(url(sink), {})['following'] = {
            data[source]['root_url'] : score for source, score in sources.items()
            if url(sink) != url(source)
        }

#print(json.dumps(RESULTS, indent=4))

filtered = {}
for k, v in by_root.items():
    if len(v) >= 5:
        filtered[k] = v


def get_sentiment(ds):
    return np.array([ d['geneea/sentiment']['sentiment'] for d in ds ])


def pd(d, f=None):
    data = d.items()
    if f is not None:
        data = sorted(data, key=f)
    for k, v in data:
        print("%35s : %s"%(k, v))

sentiments = mapvalues(get_sentiment, filtered)

Stats = namedtuple("Stats", ['mean', 'len', 'min', 'max'])
Stats.__str__ = lambda self : "%2.4f %3d %2.1f %2.1f"%self

def a_sentiment(a):
    ret= Stats(a.mean(), len(a), a.min(), a.max())
    return ret

sentiments_stat = mapvalues(a_sentiment, sentiments)

#pd(sentiments_stat, lambda t: t[1])

def get_tags(ds):
    per_tag = {}
    for d in ds:
        sentiment = d['geneea/sentiment']['sentiment']
        for t in d['geneea/tags']:
            key, score = t['text'], t['score']
            store = per_tag.setdefault(key, {})
            store['score'] = store.get('score', 0.0) + score
            store['sentiment'] = store.get('sentiment', 0.0) + sentiment
            store['count'] = store.get('count', 0) + 1

    for v in per_tag.values():
        v['avg_score'] = v.get('score', 0.0) / v.get('count', 1.0)
        v['avg_sentiment'] = v.get('sentiment', 0.0) / v.get('count', 1.0)
    return per_tag

def get_topics(ds):
    per_tag = {}
    for d in ds:
        sentiment = d['geneea/sentiment']['sentiment']
        for t in d['geneea/topic']:
            key, score = t['label'], t['confidence']
            store = per_tag.setdefault(key, {})
            store['score'] = store.get('score', 0.0) + score
            store['sentiment'] = store.get('sentiment', 0.0) + sentiment
            store['count'] = store.get('count', 0) + 1

    for v in per_tag.values():
        v['avg_score'] = v.get('score', 0.0) / v.get('count', 1.0)
        v['avg_sentiment'] = v.get('sentiment', 0.0) / v.get('count', 1.0)
    return per_tag

def get_entities(ds):
    per_tag = {}
    for d in ds:
        sentiment = d['geneea/sentiment']['sentiment']
        for t in d['geneea/entities']:
            if t['name'].lower() == 'organizace spojených národů':
                t['name'] = 'OSN'
            if t['name'].lower() == 'česká tisková kancelář':
                t['name'] = 'ČTK'
            key, instances = t['name'], t['instances']
            if t['type'] not in ['location', 'organization', 'person']:
                continue
            store = per_tag.setdefault(key, {})
            store.setdefault('types', set()).add(t['type'])
            store['score'] = store.get('score', 0.0) + len(instances)
            store['sentiment'] = store.get('sentiment', 0.0) + sentiment
            store['count'] = store.get('count', 0) + 1

    for v in per_tag.values():
        v['avg_score'] = v.get('score', 0.0) / v.get('count', 1.0)
        v['avg_sentiment'] = v.get('sentiment', 0.0) / v.get('count', 1.0)

    return per_tag


#tags_stats = mapvalues(get_tags, filtered)
topics_stats = mapvalues(get_topics, filtered)
entity_stats = mapvalues(get_entities, filtered)

def handle_tag(txt):
    return re.sub(r'\.', r'___TECKA___', txt)

if True:
    #print(json.dumps(filtered['ac24.cz_fake'][0], indent=4))
    #print(filtered['ac24.cz_fake'][0]['text'])

    topic_global = {}
    topic_global_cnt = {}
    for k, pt in topics_stats.items():
        for tag, stats in pt.items():
            topic_global[tag] = topic_global.get(tag, 0) + stats['score']
            topic_global_cnt[tag] = topic_global_cnt.get(tag, 0) + stats['count']

    topic_avg = { k : v / topic_global_cnt[k] for k,v in topic_global.items()}

    translate = {
        'Sports' : 'Sport',
        'Culture' : 'Kultura',
        'Politics and News' : 'Politika',
        'Business' : 'Byznys'
    }
    print("TOPIC")
    for k, pt in topics_stats.items():

        vs = sorted(pt.items(), key=lambda t: -(t[1]['avg_score'] - topic_avg[t[0]]))
        printed = 0
        for tag, stats in vs:
            diff = stats['avg_score'] - topic_avg[tag]
            if stats['count'] > 5 and diff > 0 and printed < 2 and len(tag) < 20:
                printed += 1
                RESULTS.setdefault(k, {}).setdefault("topic", []).append(translate[tag])
                #print("%20s %.5f %s"%(tag, diff, stats['types']))

if True:
    #print(json.dumps(filtered['ac24.cz_fake'][0], indent=4))
    #print(filtered['ac24.cz_fake'][0]['text'])

    ent_global = {}
    for k, pt in entity_stats.items():
        for tag, stats in pt.items():
            ent_global[tag] = ent_global.get(tag, 0) + stats['count']

    ent_total = sum(ent_global.values())
    ent_avg = { k : v / ent_total for k,v in ent_global.items()}

    print("ENTITY")
    for k, pt in entity_stats.items():
        house_sum = sum(s['count'] for s in pt.values())

        if False:
            print("="*20)
            print(k)
            print("="*20)

        #vs = sorted(pt.items(), key=lambda t: -t[1]['count'])
        vs = sorted(pt.items(), key=lambda t: -(t[1]['count'] / house_sum - ent_avg[t[0]]))
        printed = 0
        for tag, stats in vs:
            diff = stats['count'] / house_sum - ent_avg[tag]
            if stats['count'] > 5 and diff > 0 and printed < 40 and len(tag) < 20:
                printed += 1
                RESULTS.setdefault(k, {}).setdefault('tags', {})[handle_tag(tag)] = diff
                #print("%20s %.5f %s"%(tag, diff, stats['types']))

if False:
    print("TAGS")
    for k, pt in tags_stats.items():
        print("="*20)
        print(k)
        print("="*20)
        vs = sorted(pt.items(), key=lambda t: -t[1]['count'])[:30]
        for tag, stats in vs:
            if stats['count'] >= 5:
                print("%20s %s"%(tag, stats['count']))

enricher = enrich.get()
for k in RESULTS.keys():
    key = k.split('_')[0]
    if key in enricher:
        RESULTS[k].update(enricher[key])
    else:
        print(k, key)

with open("dump.json", 'wb') as fout:
    fout.write(json.dumps(RESULTS, indent=4).encode('utf-8'))

with open("dump_plain.json", 'w') as fout:
    fout.write(re.sub(r"'", r'"', str(RESULTS)))
