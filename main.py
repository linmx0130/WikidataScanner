import urllib.request as ureq
import urllib.parse as uparse
import urllib.error
import json

queryApiURL ="https://query.wikidata.org/sparql?"
def getSparQL(parentClass):
    return 'SELECT ?s ?desc WHERE { ?s wdt:P171 wd:'+parentClass+'. OPTIONAL{?s rdfs:label ?desc filter (lang(?desc) = "en"). }}'

def getApiURL(parentClass):
    return queryApiURL+uparse.urlencode({'query':getSparQL(parentClass),'format': 'json'})

def getQidFromURL(url):
    buf = url.strip().split('/')
    return buf[len(buf)-1]

typeMap = {}
typeList = []
searchq = []

def getJSON(typeName):
    url = getApiURL(typeName)
    with ureq.urlopen(url) as response:
        d = response.read().decode()
        jd = json.loads(d)
    return jd

def getChildType(typeName, out, tout, scanned):
    childList =getJSON(typeName)['results']['bindings']
    for item in childList:
        qid = getQidFromURL(item['s']['value'])
        if 'desc' in item:
            name = item['desc']['value']
        else:
            name = ""
        if not qid in typeMap.keys():
            typeMap[qid] = name
            typeList.append(qid)
            searchq.append(qid)
            print(qid+" subclass_of "+typeName, file=out, flush=True)
            print(qid+": "+name, file= tout, flush =True)
    print(typeName)
    print(typeName, file = scanned, flush = True)

with open("typefile") as typefile:
    for line in typefile.readlines():
        buf = line.split(":")
        qid = buf[0]
        name = buf[1].strip()
        typeMap[qid]=name
        typeList.append(qid)
        searchq.append(qid)

with open("typegraph") as fin:
    for line in fin.readlines():
        buf = line.split(" ")
        qid = buf[2].strip()
        if qid in searchq:
            searchq.remove(qid)

with open("scanned") as fin:
    for line in fin.readlines():
        qid = line.strip()
        if qid in searchq:
            searchq.remove(qid)

fout = open("typegraph", "a")
typefile = open("typefile", "a")
scanned = open("scanned","a")
searchq.append('Q756')
while len(searchq) > 0:
    nowType = searchq[0]
    searchq.remove(nowType)
    print("Left Type = "+ str(len(searchq)))
    getChildType(nowType, fout, typefile, scanned)
fout.close()
typefile.close()
