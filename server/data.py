
class Tree(object):
    """
    >>> t = Tree()
    >>> t.merge({1:2})
    >>> t
    {1: 2}
    >>> t.merge({1:4})
    >>> t
    {1: 6}
    """
    def __init__(self):
        self._dict = {}

    def merge(self, d):
        self._dict = merge(self._dict, d)

    def find(self, name):
        return self._dict.get(name)

    def __repr__(self):
        return repr(self._dict)

class Item(object):
    def __init__(self, value=None, action=None):
        self.action = action # sum, average, ...
        self.value = value


def merge(d1, d2):
    """
    >>> d1 = {1:2}
    >>> d2 = {3:4}
    >>> merge(d1, d2)
    {1: 2, 3: 4}
    >>>
    >>> d1 = {1:2,2:{21:22}}
    >>> d2 = {3:4,2:{21:23}}
    >>> merge(d1, d2)
    {1: 2, 2: {21: 45}, 3: 4}
    >>>
    >>> merge(1, {2:3})
    {2: 3, '_default': 1}
    >>>
    >>> d1 = {2:1}
    >>> d2 = {2:{21:23}}
    >>> merge(d1, d2)
    {2: {'_default': 1, 21: 23}}
    """
    
    if isinstance(d1, dict) and isinstance(d2, dict):
        for k,v in d2.iteritems():
            if k not in d1:
                d1[k] = v
            else:
                d1[k] = merge(d1[k], v)
        return d1
    elif isinstance(d1, dict):
        d1.update({'_default':d2})
        return d1
    elif isinstance(d2, dict):
        d2.update({'_default':d1})
        return d2
    else:
        return d1 + d2
    

