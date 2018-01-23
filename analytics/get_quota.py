
import urllib.request
import json

url = 'https://api.geneea.com/account'

headers = {
    'content-type': 'application/json',
    'Authorization': 'user_key '
}

input = {'text': 'This is a great text, François!'}

req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req)
responseObj = json.loads(resp.read().decode('utf-8'))

print(responseObj)
