"""
Core of the entire system. Tree always initialize from a `dict`.
"""

class Tree(object):
    """
    >>> Tree({1:0})
    {1: <Item('0')>}
    >>> Tree()
    {}

    >>> a = {'cpu': {'10.3.1.12': {'idle':  0.32,
    ...                   'sytem': 0.29,
    ...                   'user': 1,
    ...                   'marker': 'sth. wrong happened'}},
    ...      'default_action': 'average'}
    >>> Tree(a)
    {'cpu': {'10.3.1.12': {'idle': <Item('0.32')>, 'sytem': <Item('0.29')>, 'user': <Item('1')>}}}

    >>> t = Tree(a)
    >>> for ks, v in t.find('cpu,,user'): print ks, v
    ['cpu', '10.3.1.12', 'user'] <Item('1')>
    """
    def __init__(self, d=None):
        if d is None:
            self._dict = {}
        else:
            action_name = d.get('default_action', 'add')
            action = _action_from_name(action_name)
            self._dict = evolve(d, action)

    def merge(self, d):
        self._dict = merge(self._dict, d)

    def find(self, name):
        # right, same as right
        name= name.rstrip(',')

        for ks, x in find_pattern(self._dict, name):
            yield ks, x

    def __repr__(self):
        return repr(self._dict)

class Item(object):
    def __init__(self, value=None, action=None):
        self.value = value
        self.action = action # sum, average, ...

    def __repr__(self):
        return "<Item(%r)>" % repr(self.value)

    def __add__(self, b):
        return Item(self.action(self.value, b.value), self.action)

def _average(a,b):
    return (a+b)/2

def _add(a,b):
    return a+b

def _action_from_name(name):
    m = {'add': _add,
        'average': _average}
    return m[name]

def evolve(d, default_action=_add):
    """
    Convert a normal dict to Tree like dict with memeber as Item.

    >>> evolve({1:2})
    {1: <Item('2')>}
    >>> evolve({1: Item(2)})
    {1: <Item('2')>}

    >>> d = evolve({1: {2: 3}}, _add)
    >>> d[1][2].action == _add
    True
    """
    rd = {}
    for k,v in d.iteritems():
        if isinstance(v, Item):
            rd[k] = v
        elif isinstance(v, (int, long, float)):
            #print default_action
            rd[k] = Item(v, default_action)
        elif isinstance(v, dict):
            rd[k] = evolve(v, default_action)
    return rd

def merge(d1, d2):
    """
    >>> merge({1: Item(1,_add)}, {3: Item(1,_add)})
    {1: <Item('1')>, 3: <Item('1')>}
    >>> merge({1: Item(1,_add)}, {1: 2})
    {1: <Item('3')>}
    >>> merge({1: Item(1,_add)}, {1: 2})
    {1: <Item('3')>}

    >>> merge({1: {2:Item(3, _add)}}, {1:{2:4}})
    {1: {2: <Item('7')>}}

    >>> merge({1: {2:Item(3, _add)}}, {1:4})
    {1: {'count': <Item('4')>, 2: <Item('3')>}}

    >>> merge({1:Item(4, _add)}, {1: {2: {3:5}}})
    {1: {'count': <Item('4')>, 2: {3: <Item('5')>}}}
 
    """
    d2 = evolve(d2)
    for k,v2 in d2.iteritems():
        if k not in d1:
            d1[k] = v2
        else:
            v1 = d1[k]
            if isinstance(v1, Item) and isinstance(v2, Item):
                d1[k] = v1 + v2
            elif isinstance(v1, dict) and isinstance(v2, dict):
                d1[k] = merge(v1, v2)
            elif isinstance(v1, dict) and isinstance(v2, Item):
                v1['count'] = v2
            elif isinstance(v1, Item) and isinstance(v2, dict):
                v2.update({'count':v1})
                d1[k] = v2
            else:
                assert False, 'merge unespected type k: %r v1: %r v2: %r' % (k, v1, v2)
    return d1

def keyin(key, d):
    arr = key.split(',')
    for a in arr:
        if a in d:
            d = d[a]
        else:
            return False
    return True

def match(a, b):
    """
    >>> match([], [])
    True
    >>> match([1], [1])
    True
    >>> match([1], [''])
    True

    >>> match(['1','2'], ['1'])
    True
    >>> match(['1','2'], [''])
    True

    >>> match(['1','2'], ['3'])
    False
    >>> match(['1'], ['3'])
    False
    >>> match(['1','2'], ['','1'])
    False

    >>> match(['1','2'], ['','2'])
    True
    >>> match(['1','2','3'], ['','2'])
    True

    >>> match(['1'], ['', '', '6'])
    False
    """

    if len(b) > len(a):
        return False

    for i, xa in enumerate(a):
        if i < len(b):
            xb = b[i]
            if xb and xb != xa:
                return False
        else:
            break

    return True

def find_pattern(d, pattern):
    """
    Find all matched Items.

    >>> d = {'1': Item(1, _add), '2': Item(2, _add), '3': {'4':{'6':Item(6, _add)}, '5':Item(5, _add)}}
    >>> [x for ks,x in find_pattern(d, '')]
    [<Item('1')>, <Item('5')>, <Item('6')>, <Item('2')>]
    >>> [x for ks,x in find_pattern(d, '1,2')]
    []
    >>> [x for ks,x in find_pattern(d, '3,4')]
    [<Item('6')>]
    
    >>> [x for ks,x in find_pattern(d, '3')]
    [<Item('5')>, <Item('6')>]

    >>> [x for ks,x in find_pattern(d, ',3')]
    []
    >>> [x for ks,x in find_pattern(d, ',4')]
    [<Item('6')>]

    >>> [x for ks,x in find_pattern(d, ',,6')]
    [<Item('6')>]
    """

    arr = pattern.split(',')

    # deep first traversal
    def dfs(d, ks):
        for k, v in d.iteritems():
            deep_ks = ks + [k]
            if isinstance(v, dict):
                for x in dfs(v, deep_ks):
                    yield x
            elif isinstance(v, (Item, int, long, float)):
                yield (v, deep_ks)
            else:
                assert False, 'dfs unespected type k: %r v: %r' % (k, v)

    for v, ks in dfs(d, []):
        if match(ks, arr):
            yield ks, v
