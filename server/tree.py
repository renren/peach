
class Tree(object):
    """
    >>> t = Tree({1:0})
    >>> t
    {1: 0}
    >>> t = Tree()
    >>> t
    {}
    >>> t.merge({1:2})
    >>> t
    {1: 2}
    >>> t.merge({1:4})
    >>> t
    {1: 6}
    >>> a = {'cpu': {'10.3.1.12': {'idle': {'v': 0.32},
    ...                   'sytem': {'count': 0.29},
    ...                   'user': {'count': 1,
    ...                            'marker': 'sth. wrong happened'}}},
    ...      '': 'average'}
    >>> t = Tree(a)
    >>> t.merge({'cpu': {'10.3.1.12': {'idle': {'count': 0.64}}}})
    """
    def __init__(self, d=None):
        self._dict = d and d or {}

    def merge(self, d):
        self._dict = merge(self._dict, d)

    def find(self, name):
        """
        """
        arr = name.split(',')
        d = self._dict
        for x in arr:
            d = d.get(x)
        return d

    def __repr__(self):
        return repr(self._dict)

class Item(object):
    def __init__(self, value=None, action=None):
        self.action = action # sum, average, ...
        self.value = value

def _average(a,b):
    return (a+b)/2

def _add(a,b):
    return a+b

def merge(d1, d2, action=_add):
    """
    >>> merge({1:2}, {3:4})
    {1: 2, 3: 4}
    >>> merge({1:2,2:{21:22}},      {3:4,2:{21:23}})
    {1: 2, 2: {21: 45}, 3: 4}
    >>>
    >>> merge(1, {2:3})
    {2: 3, '_default': 1}
    >>>
    >>> d1 = {2:1}
    >>> d2 = {2:{21:23}}
    >>> merge(d1, d2)
    {2: {'_default': 1, 21: 23}}


    >>> merge({'action':'average', 1:3}, {1:4})

    a,b,c 1
    a,b,c 2
    a,b,d 3
    a,b 
    a,b,sum 3
    a,b,count 2
    a,b,action average
    a,action
    """

    for k,v2 in d2.iteritems():
        if v1 not in d1:
            d1[k] = v2
        else:
            d1[k] = merge(d1[k], v)

    
    if isinstance(d1, dict) and isinstance(d2, dict):
        
        return d1
    elif isinstance(d1, dict):
        d1.update({'_default':d2})
        return d1
    elif isinstance(d2, dict):
        d2.update({'_default':d1})
        return d2
    else:
        return d1 + d2
    

