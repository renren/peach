import sys, pprint
import time
import json, urllib2, urllib

_br = {}

def push(d):
    url = 'http://127.0.0.1:8000/push'
    s = json.dumps(d)
    s = urllib.urlencode({"json": s})
    f = urllib2.urlopen(url, s)
    f.read()

def add(d, a, v=1):
    ks = a[:-1]
    for i in ks:
        d = d.setdefault(i, {})

    try:
        d[a[-1]] += v
    except:
        d.setdefault(a[-1], v)

last = 0

for i in sys.stdin:
    a = i.strip('\n').split('|')
    d = _br

    for k in a:
        if not k: continue

        v = k.split(':')
        add(d, (v[0], v[1]))
    last += 1
    if last > 1000:
        time.sleep(3)
        last = 1
        push({'br':_br})
        pprint.pprint(_br)
        _br = {}

# 


"""
Browscap: http://drupal.org/project/browscap
wurfl: http://wurfl.sourceforge.net/

{os: 
    {win: {6: 100},{7:400}},
    {linux: 100},
}

{br:
    {firefox: {7:20}, {9:40}},
    {ie: {6:30}, {7:40}},
}
"""
