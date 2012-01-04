import httpagentparser

_os = {}
_br = {}

def add(t):
    pass #result.

def pipe(arr):
    t = httpagentparser.detect(arr[3])
    # {'os': {'name': 'Linux'},
    #   'browser': {'version': '5.0.307.11', 'name': 'Chrome'}}
    add(t)

def result():
    return [x for x in [_os, _br] if x]

def init():
    pass
    # from xx import ctx
    # ctx.init('', pipe, result)


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
