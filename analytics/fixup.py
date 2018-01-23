import json
import re
import sys

import copy

import enrich

with open("dump.json", 'r') as fin:
    RESULTS = json.load(fin)

print(len(RESULTS))

enricher = enrich.get()
for k in copy.copy(RESULTS).keys():
    key = k.split('_')[0]
    if key not in enricher:
        del RESULTS[k]

print(len(RESULTS))

with open("dump2.json", 'wb') as fout:
    fout.write(json.dumps(RESULTS, indent=4).encode('utf-8'))

with open("dump_plain2.json", 'w') as fout:
    fout.write(re.sub(r"'", r'"', str(RESULTS)))