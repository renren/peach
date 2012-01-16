import httpagentparser
import tree

_os = tree.Tree({'os': {}})
_br = tree.Tree({'br': {}})

def add(t):
    a = t.get('os')
    if a:
        if 'version' in a:
            d = {a['name'] : {a['version']: 1}}
        else:
            d = {a['name'] : 1}
        _os.merge({'os':d})

    a = t.get('browser')
    if a: 
        d = {a['name'] : {a['version']:1}}
        _br.merge({'br' : d})

_default_index = None

def process(arr):
    global _default_index
    if _default_index is None:
        for i, x in enumerate(arr):
            t = httpagentparser.detect(x)
            if t:
                _default_index = i
                break
    else:
        t = httpagentparser.detect(arr[_default_index])

    # {'os': {'name': 'Linux'},
    #   'browser': {'version': '5.0.307.11', 'name': 'Chrome'}}
    if t:
        add(t)

def result():
    global _os, _br
    # TODO: ugly ._dict
    x = ('os', _os._dict), ('br', _br._dict)
    _os = tree.Tree({'os': {}})
    _br = tree.Tree({'br': {}})
    return x

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
