#!/usr/bin/env python

'''
setup:
  easy_install PyYAML
  easy_install pymongo
'''

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from pymongo import Connection
from bson.code import Code
import pprint
import datetime
import sys,getopt

# load config
CONFIG = load(file('config.yml'))

MONGO_HOST =  CONFIG['mongo']['host']
MONGO_PORT =  CONFIG['mongo']['port']
MONGO_DB =  CONFIG['mongo']['db']
MONGO_COLLECTION =  CONFIG['mongo']['collection']

ROMONGO_HOST = CONFIG['romongo']['agent']['host']
ROMONGO_PORT = CONFIG['romongo']['agent']['port']

# connect to mongodb
connection = Connection(MONGO_HOST, MONGO_PORT)
db = connection[MONGO_DB]
cl = db[MONGO_COLLECTION]

# get stat result from mongodb
stat_reduce = Code("function(doc, prev) {"
"		if ( doc._core in prev.brstat.core ) {"
"			if ( doc._shell in prev.brstat.core[doc._core] ) {"
"				prev.brstat.core[doc._core][doc._shell]++;"
"			} else {"
"				prev.brstat.core[doc._core][doc._shell] = 1;"
"			}"
"		} else {"
"			prev.brstat.core[doc._core] = {};"
"			prev.brstat.core[doc._core][doc._shell] = 1;"
"		}"
"		if ( doc._shell in prev.brstat.vender ) {"
"			if ( doc._shell_ver in prev.brstat.vender[doc._shell] ) {"
"				prev.brstat.vender[doc._shell][doc._shell_ver]++;"
"			} else {"
"				prev.brstat.vender[doc._shell][doc._shell_ver] = 1;"
"			}"
"		} else {"
"			prev.brstat.vender[doc._shell] = {};"
"			prev.brstat.vender[doc._shell][doc._shell_ver] = 1;"
"		}"
"}"
)
# group(key, condition, initial, reduce, finalize=None, command=True)
now = datetime.datetime.utcnow()
last = now - datetime.timedelta(minutes=5)
result = cl.group( {"key" : "_core"},
    {'time' : {"$gte": last, "$lt": now}}, 
    {"brstat" : {"core" : {}, "vender" : {}}},
    stat_reduce
)
pprint.pprint(result)


url = "http://127.0.0.1/push"
try:
    if sys.argv:
        url = sys.argv[1]
except:
    pass

# POST to sloth server
import urllib, urllib2,json
data = { 'brstat': result[0]['brstat']}
params = urllib.urlencode({'json':json.dumps(data)})
f = urllib2.urlopen(url, params)
f.read()
