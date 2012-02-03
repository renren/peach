import httpagentparser
import vendor
import tree

can_register = True

_os = tree.Tree({'os': {}, 'default_action':'add'})
_br = tree.Tree({'br': {}, 'default_action':'add'})
_vd = tree.Tree({'br': {}, 'default_action':'add'})

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

    a = t.get('vendor')
    if a: 
        d = {a['name'] : {a['version']:1}}
        _vd.merge({'vendor' : d})

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
    global _os, _br, _vd
    # TODO: ugly ._dict
    x = ('os', _os._dict), ('br', _br._dict), ('vendor', _vd._dict)
    _os = tree.Tree({'os': {}, 'default_action':'add'})
    _br = tree.Tree({'br': {}, 'default_action':'add'})
    _vd = tree.Tree({'br': {}, 'default_action':'add'})
    return x

def init():
    pass
    # from xx import ctx
    # ctx.init('', pipe, result)


"""
TODO: use more generic data
Browscap: http://drupal.org/project/browscap
http://browsers.garykeith.com/stream.asp?PHP_BrowsCapINI
http://browsers.garykeith.com/stream.asp?BrowsCapXML

wurfl: http://wurfl.sourceforge.net/
http://wurfl.sourceforge.net/wurfl_download.php


{os: 
    {win: {6: 100},{7:400}},
    {linux: 100},
}

{br:
    {firefox: {7:20}, {9:40}},
    {ie: {6:30}, {7:40}},
}
"""
