import csv
import json
import urllib.parse
import urllib.request


import sys
import csv

csv.field_size_limit(sys.maxsize)


def request(text):
    root = 'https://api.geneea.com/s2/'
    res = {}
    for url in ['sentiment',
                'topic',
                'tags',
                'entities']:

        headers = {
            'content-type': 'application/json',
            'Authorization': 'user_key '
        }
        input = {'text': text}

        req = urllib.request.Request(root + url, headers=headers, data=json.dumps(input).encode('utf-8'))
        resp = urllib.request.urlopen(req)
        responseObj = json.loads(resp.read().decode('utf-8'))

        del responseObj['text']
        if url == "tags":
            res['geneea/' + url] = responseObj['tags']
        elif url == "sentiment":
            res['geneea/' + url] = {'sentiment': responseObj['sentiment'], 'label': responseObj['label']}
        elif url == "topic":
            res['geneea/' + url] = responseObj['labels']
        elif url == "entities":
            res['geneea/' + url] = responseObj['entities']

    return res


def fake_request(text):
    return {"geneea/sentiment": "positive"}

def is_valid_nice(url):
    for u in [
        "aktualne.cz",
"blesk.cz",
"centrum.cz",
"ceskatelevize.cz",
"ceskenoviny.cz",
"denik.cz",
"e15.cz",
"echo24.cz",
"euro.cz",
"finance.cz",
"hlidacipes.org",
"idnes.cz",
"ihned.cz",
"lidovky.cz",
"novinky.cz",
"penize.cz",
"reflex.cz",
"respekt.cz",
"sport.cz",
"tiscali.cz",
"tyden.cz",
"zive.cz"
    ]:
        if u in url:
            return True

    return False

def is_valid_fake(url):
    for u in [
'ac24.cz',
'aeronet.cz',
'bezpolitickekorektnosti.cz',
'ceskoaktualne.cz',
'cz.sputniknews.com',
'czechfreepress.cz',
'eurozpravy.cz',
'hlavnespravy.sk',
'infovojna.sk',
'instory.cz',
'literarky.cz',
'magnificat.sk',
'megazine.cz',
'novarepublika.cz',
'nwoo.org',
'parlamentnilisty.cz',
'procproto.cz',
'protiprudu.org',
'rukojmi.cz',
'slobodavockovani.sk',
'slovenskeslovo.sk',
'svetkolemnas.info',
'svobodnenoviny.eu',
'vlasteneckenoviny.cz',
'zvedavec.org'
    ]:
        if u in url:
            return True

    return False

import csv
import json

def iter_jsons():
    with open('Archive/10-2017-news-forums-discussions.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        keys = []
        for i, row in enumerate(spamreader):
            if i == 0:
                keys = [t.lower() for t in row]
                continue

            if len(keys) != len(row):
                print("%d" % i, row[0], " len(keys) != len(row)")
                continue

            d = {k: v for k, v in zip(keys, row)}

            if d['type'] != 'news':
                continue

            if is_valid_nice(d['resource_url']):
                d['LABEL'] = 'nice'
            elif is_valid_fake(d['resource_url']):
                d['LABEL'] = 'fake'

            yield d
            # ret = fake_request(d['text'])
            # request(Text)

            # print(resource)
            # print(resource_url)
            # print(url)
            # print()


from multiprocessing import Pool

def mapf(data):
    try:
        ret = request(data['text'])
        data.update(ret)
        return data
    except Exception as e:
        print("EXCEPTION", e)
        return None

def iter():
    for i, data in enumerate(iter_jsons()):
        if i < 50500:
            continue
        print(i)
        if 'LABEL' in data:
            yield data
    yield None

if __name__ == '__main__':
    with open("OUTPUT_10", 'a') as fout:
        with Pool(10) as p:
            for ret in p.imap_unordered(mapf, iter()):
                if ret is None:
                    continue
                print(ret['resource_url'])
                fout.write("%s\n"%json.dumps(ret))
