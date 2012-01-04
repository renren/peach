import sys, pprint

_br = {}

def add(d, a, v=1):
    ks = a[:-1]
    for i in ks:
        d = d.setdefault(i, {})

    try:
        d[a[-1]] += v
    except:
        d.setdefault(a[-1], v)

for i in sys.stdin:
    a = i.strip('\n').split('|')
    d = _br

    for k in a:
        if not k: continue

        v = k.split(':')
        add(d, (v[0], v[1]))

pprint.pprint(_br)


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