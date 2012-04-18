"""
merge 2 dict
Examples:

>>> merge({'ip1': {'cpu': 0.2}}, {'ip1': {'cpu': 0.4}})
{'ip1': {'cpu': [0.2, 0.4]}}

>>> merge({}, {1:2})
{1: 2}

>>> merge({'ip1': {'cpu': 0.2}}, a=3,b=3)
{'a': 3, 'ip1': {'cpu': 0.2}, 'b': 3}

>>> merge({'ip1': {'cpu': 0.2}}, {'ip1': {'net': 10}})
{'ip1': {'net': 10, 'cpu': 0.2}}

query dict by pattern
Examples:

>>> d = {'ip1': { 'cpu': 0.2, 'net':120 },
...     'ip2': { 'cpu': 0.3, 'net':10 },
...     'ip3': { 'cpu0': 0.3, 'cpu1':0.6 },
...     'arr': [0.3,0.6],
...     }
>>> type(d)
<type 'dict'>

>>> [x for x in query({'a': {'b': 5}}, 'a')]
[('a.b', 5)]

>>> list(query(d, 'ip1.net'))
[('ip1.net', 120)]

>>> for i in query(d, 'ip*.cpu'): print i
('ip2.cpu', 0.3)
('ip1.cpu', 0.2)

>>> for i in query(d, 'ip*.cpu*'): print i
('ip2.cpu', 0.3)
('ip3.cpu0', 0.3)
('ip3.cpu1', 0.6)
('ip1.cpu', 0.2)

>>> for i in query(d, 'ip*|list.cpu*|avg'): print i
('ip2.cpu*', 0.3)
('ip3.cpu*', 0.45)
('ip1.cpu*', 0.2)

>>> for i in query(d, '*|sum.net'): print i
('*', 130.0)

>>> for i in query(d, '*|avg.net'): print i
('*', 65.0)

>>> for i in query(d, 'ip*|avg.cpu*|avg'): print i
('ip*', 0.31666666666666665)
"""

import copy
import operator
import fnmatch
import math, decimal

_SEP = '.'

def match(s, pat):
    """
    >>> match('a', 'a*')
    True
    >>> match('ab', 'a*')
    True
    >>> match('abc', 'a*')
    True
    >>> match('ab', 'b*')
    False
    """
    return fnmatch.fnmatchcase(s, pat)

def keyin(pats, d):
    """
    >>> d = {'a': {'b': 1}}
    >>> keyin('a.b', d)
    True
    >>> keyin('a.b.c', d)
    False
    >>> keyin('a', d)
    True
    >>> keyin('b', d)
    False

    >>> keyin('a.*', d)
    True
    >>> keyin('*.b', d)
    True
    >>> keyin('*.c', d)
    False
    >>> d = {'a': {'b': {'c':'0'}}}
    >>> keyin('*.c', d)
    False
    >>> keyin('a.*.c', d)
    True
    """
    
    pat_list = pats.split(_SEP)
    _d = d
    for i, pat in enumerate(pat_list):
        if '*' in pat:
            nd = {}
            for k,v in _d.iteritems():
                if match(k, pat):
                    if isinstance(v, dict):
                        nd.update(v)
                    elif i == len(pat_list) - 1: # last one
                        return True
            if not nd: return False
            _d = nd
        else:
            try:
                if not pat in _d:
                    return False
                _d = _d[pat]
            except:
                return False
    return True

def dotexpand(d):
    """ convert a.b.c => {a: {b: c}}
    >>> dotexpand({'a.b.c' : 1})
    {'a': {'b': {'c': 1}}}
    >>> dotexpand({'a' : 1})
    {'a': 1}
    >>> dotexpand({'1.2' : 1})
    {'1': {'2': 1}}
    >>> dotexpand({'a.b.c' : {'d.e': 1}})
    {'a': {'b': {'c': {'d': {'e': 1}}}}}
    >>> dotexpand({'a.b.c' : {'m': {'d.e': 1}}})
    {'a': {'b': {'c': {'m': {'d': {'e': 1}}}}}}
    >>> dotexpand(1)
    1
    >>> dotexpand(1.2)
    1.2
    >>> dotexpand({"firefox": {'4.01': 2.0}})
    {'firefox': {'4': {'01': 2.0}}}
    >>> dotexpand({"firefox": {'4.01': 2, '4.02': 3}})
    {'firefox': {'4': {'02': 3, '01': 2}}}

    # failed: 
    >>> dotexpand({"firefox": {'4': 5, '4.01': 2, '4.02': 3}})
    {'firefox': {'4': {'02': 3, '01': 2}}}
    """
    if not isinstance(d, dict):
        return d
    
    r = {}
    for k, v in d.iteritems():
        a = k.split(_SEP)
        sr = r
        for i in a[:-1]:
            sr = sr.setdefault(i, {})
        assert isinstance(sr, dict), '%r: %s %r' % (type(sr), k,sr)
        sr.setdefault(a[-1], dotexpand(v))
    return r

def dotescape(d):
    """
    mongodb key should not contain dot, fix:

firefox: {
  '3.1':  40,
  '3.5': 100,
  '5_6': 200,
}

firefox: {
  _3_1:  40,
  _3_5: 100,
  5_6 : 200,
}

firefox.3.1 => firefox._3_1

>>> dotescape("a.b")
'_a_b'

>>> dotescape({"a.b":1})
{'_a_b': 1}

>>> dotescape({"firefox": {'4': 5, '4.01': 2, '4.02': 3}})
{'firefox': {'_4_01': 2, '_4_02': 3, '4': 5}}

>>> dotescape({"a.b": {'c.d': {'f.g': 3}}})
{'_a_b': {'_c_d': {'_f_g': 3}}}

"""
    if isinstance(d, str):
        if _SEP in d:
            return '_' + d.replace('.', '_', -1)
        else:
            return d
    elif isinstance(d, dict):
        # TODO: more efficiency implement
        r = {}
        for k, v in d.iteritems():
            if _SEP in k:
                r.setdefault(dotescape(k), dotescape(v))
            else:
                r.setdefault(k, dotescape(v))
        return r
    else:
        return d

def _loop_by(d1, d2):
    assert isinstance(d2, dict)
    for k,v2 in d2.iteritems():
        if not isinstance(v2, dict):
            yield (k in d1), d1, d2, k, v2
        else:
            v1 = d1.get(k)

            if v1 is None:
                yield False, d1, d2, k, v2
                continue
            
            for t in _loop_by(v1, v2):
                yield t

def merge(d, *args, **kwargs):
    """ merge 2 dict, return the first
    """
    if len(kwargs) ==0 and len(args) and isinstance(args[0], dict):
        kwargs = args[0]
    for keyin, d1,d2,key,v2 in _loop_by(d, kwargs):
        if keyin:
            v1 = d1[key]
            if not isinstance(v1, list):
                v1 = [v1]
            assert isinstance(v2, (int, float, long)), (key,v2,d2)
            v1.append(v2)
            d1[key] = v1
        else:
            d1[key] = copy.deepcopy(v2)
    return d

def shrink(d):
    """
    >>> d = {'br': {'hello': [4, 4, 4, 4, 4, 4, 4, 8]}}
    >>> shrink(d)
    >>> d
    {'br': {'hello': [8]}}

    >>> d = {'br': {'hello': {'world': [1,2,3]}}}
    >>> shrink(d)
    >>> d
    {'br': {'hello': {'world': [3]}}}

    >>> d = {'br': [1,2,3]}
    >>> shrink(d)
    >>> d
    {'br': [3]}
    """
    for ks, v in loop(d):
        if isinstance(v, list):
            del v[:len(v) - 1]

def add(d, *args, **kwargs):
    """ TODO: code same as merge
    """
    if len(kwargs) ==0 and len(args) and isinstance(args[0], dict):
        kwargs = args[0]
    for keyin, d1,d2,key,v2 in _loop_by(d, kwargs):
        if keyin:
            v1 = d1[key]
            assert isinstance(v2, (int, float, long)), (key,v2)
            assert isinstance(v1, (int, float, long)), (key,v1)
            v1 += v2
            d1[key] = v1
        else:
            d1[key] = copy.deepcopy(v2)
    return d

def expand(d, keys=None, sep=_SEP):
    """iterator all dict item, recursively

    >>> list(expand({'a':2}))
    [('a', 2)]
    >>> list(expand({'1':2},['a']))
    [('a.1', 2)]
    >>> list(expand({'1':2, '2':{'3':5}},['a']))
    [('a.1', 2), ('a.2.3', 5)]
    """
    if keys is None:
        keys = []

    if not isinstance(d, dict):
        yield sep.join(keys), d
    else:
        for k,v in d.iteritems():
            keys.append(k)
            for t in expand(v, keys, sep):
                yield t
            keys.pop()
        
def loop(d):
    """recursively iterate item of dict
    ([keys], value)
    """
    assert isinstance(d, dict)
    for k,v in d.iteritems():
        if not isinstance(v, dict):
            yield [k], v
        else:
            for t in loop(v):
                ks = [k]
                ks.extend(t[0])
                yield ks, t[1]

def proc_by_name(name, iter):
    return sum(iter)

def _avg(iter):
    a = sum(iter)
    c = decimal.Decimal(str(a)) / len(iter)
    return float(c)

def _query(d, pats):
    if isinstance(pats, str):  pats = [pats]
    if not isinstance(pats, (list, tuple)): 
        assert False, ('unexpected type', type(pats))
        
    last_i = len(pats) - 1

    if not isinstance(d, dict):
        return

    sub_dict = d
    for i, (pat, action) in enumerate(pats):
        if '*' in pat or '?' in pat:
            ret = []
            def gather(t1, t2): 
                ret.append((t1,t2))
            for k,v in sub_dict.iteritems():
                if match(k, pat):
                    if last_i == i and not isinstance(v, dict):
                        # yield [k], v
                        gather([k,], v)
                    for t in _query(v, pats[i+1:]):
                        ks = [k,t[0]]
                        gather(ks, t[1])
            if ret:
                if action is not None and action != 'list':
                    get1 = operator.itemgetter(1)
                    try:
                        a = math.fsum(map(get1, ret))
                    except:
                        assert False, (action, ret)

                    if action == 'avg':
                        #print 'avg:', ret, a, '/', len(ret)
                        a = decimal.Decimal(str(a)) / len(ret)
                        a = float(a)
                    assert isinstance(pat, str)
                    # print 'yield2', pat
                    yield pat, a
                else:
                    for k, v in ret:
                        assert isinstance(k, list)
                        # print 'yield2', _SEP.join(k)
                        yield _SEP.join(k), v
        else:
            sub_dict = sub_dict.get(pat)
            if sub_dict is None: return

            if not isinstance(sub_dict, dict):
                assert isinstance(pat, str)
                # print 'yield3', pat
                yield pat, sub_dict
                return
            else:
                if last_i == i:
                    y = loop(sub_dict)
                    # reduce [(['b'], 5)] => [('b', 5)]
                    y = [(_SEP.join(x[0]), x[1]) for x in y]
                    
                else:
                    y = _query(sub_dict, pats[i+1:])
                    # assert [], [x for x in y]

                for t in y:
                    assert isinstance(pat, str), type(pat)
                    assert isinstance(t[0], str), t
                    ks = [pat, t[0]]
                    assert isinstance(ks, list)
                    # print 'yield4', _SEP.join(ks)
                    yield _SEP.join(ks), t[1]
        return

def query(d, s):
    assert isinstance(d, dict), (type(d),d)
    pat_action_list = []
    for i in s.split(_SEP):
        if '|' in i:
            pat, action = i.split('|')
        else:
            pat, action = i, None
        pat_action_list.append((pat, action))

    for t in _query(d, pat_action_list):
        yield t

if __name__ == '__main__':
    import pprint
    d = {'ip1': { 'cpu': 0.2, 'net':120 }, \
         'ip2': { 'cpu': 0.3, 'net':10 }, \
         'ip3': { 'cpu0': 0.3, 'cpu1':0.6 }, \
         'foo': 3, \
         'arr': [10,9,8], \
         'a' : {'b' : {'c' : {'d':42}}} \
        }
    pprint.pprint(d)
    print 'loop(d)'
    for i in loop(d): print i

    cases = [
             '*.net',
             '*|sum,net',
             'ip1.cpu',
             'ip2.cpu',
             'ip1.net',
             'ip1',
             'a',
             'ip*.cpu',
             '*1.net*',
             '?p?.net*',
             'ip*.net*',
             'ip*.cpu*',
             'ip*|list.cpu*|avg',
        ]

    for c in cases:
        print c, ' ' * 4, list(query(d, c))

    assert 7 == proc_by_name('', [1,2,4])    
    assert 0.45 == _avg([0.3,0.6])
