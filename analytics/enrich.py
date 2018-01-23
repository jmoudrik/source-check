import csv
import json
import re

import subprocess

import os


DOMAINS = [
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
          ] + [
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
          ]


def request(url):
    OUTFILE = 'data/' + url
    if not os.path.exists(OUTFILE):
        out = subprocess.check_output(['curl', 'https://api.spyonweb.com/v1/domain/%s?access_token=0qVgKd2F9V6R'%url])

        with open(OUTFILE, 'wb') as fin:
            fin.write(out)

    with open(OUTFILE, 'r') as fin:
        return json.load(fin)


def tear_down(url):
    return '.'.join(url.split('.')[-2:])



def get_related():
    D={}
    for url in DOMAINS:
        #print('='*20)
        #print(url)
        #print('='*20)
        d = request(url)
        added = []
        for KEY in ['analytics', 'asdsense', 'ip']:
            try:
                this = set()
                for k, v in d['result'][KEY].items():
                    val = set([ tear_down(KKK) for KKK in v['items'].keys() ])
                    if val:
                        this |= val

                this -= set((url,))
                if this:
                    added.append((KEY, this))
            except KeyError:
                pass

        joined = set()
        added.sort(key=lambda t: len(t[1]))
        for k, s in added:
            joined |= s
        a = list(joined)
        a.sort()
        www = re.sub(r'\.', r'-', tear_down(url))
        D[www] = {'related_sites': a}
    return D


def get_od_magdy():
    d = {}

    with open('odmagdy.txt', 'r') as fin:
        data = json.load(fin)

    for row in data:
        www = row['URL']
        www = re.sub(r'\.', r'-', www)
        d[www] = {}
        if row["RU_MONTH"] != 'NA':
            d[www]['ru_month'] = int(re.sub(r',', r'', row["RU_MONTH"]))
        if row['q']:
            d[www]['8decile'] = float(row["q"])
        if row["UP_80K"] != 'NA':
            d[www]['up_80k'] = int(row['UP_80K'])
    return d

def get_od_magdy2():
    d = {}

    with open('odmagdy2.txt', 'r') as fin:
        data = json.load(fin)

    for row in data:
        www = row['Resource_URL']
        www = re.sub(r'\.', r'-', www)
        d[www] = {}
        if row["Share_median"] != 'NA':
            d[www]['share_median'] = float(row["Share_median"])
        if row["Shared_Rate"] != 'NA':
            d[www]['share_rate'] = float(row["Shared_Rate"])
    return d

def get_info():
    d = {}
    with open('general_info.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='#', quotechar='"')
        for i, row in enumerate(spamreader):
            www, year, people, house = row

            www = re.sub(r'\.', r'-', www)

            if www not in d:
                d[www] = {}
            if year:
                d[www]['established'] = year.strip()
            if people:
                d[www]['people'] = [p.strip() for p in people.split(',')]

            if house:
                d[www]['houses'] = [p.strip() for p in house.split(',')]

    return d


def get():
    DS = (get_info(), get_od_magdy(), get_related(), get_od_magdy2())

    K = set()
    for DDDD in DS:
        K |= DDDD.keys()

    d = {}
    for k in K:
        for D in DS:
            if k in D:
                if k in d:
                    d[k].update(D[k])
                else:
                    d[k] = D[k]

    return d

if __name__ == "__main__":
    pass
    #print(json.dumps(get(), indent=3))
    #print(get_od_magdy2())
