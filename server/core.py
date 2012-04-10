"""
>>> def p(v):
...    print 'callback p got:', v
>>> waiters.connect('a.b', p)
>>> waiters.live_signals
['a.b']

>>> update('a', {'b':1})
callback p got: {'a.b': 1}

>>> waiters.disconnect(p)
>>> update('a', {'b':2})

>>> engine
{'a': {'b': [1, 2]}}

>>> update('a', {'b': 3})
>>> engine
{'a': {'b': [1, 2, 3]}}
>>> list(engine.query('a.b'))
[(['a', 'b'], [1, 2, 3])]
>>> list(engine.query('a'))
[(['a', 'b'], [1, 2, 3])]

>>> update('a', {'b': 4})
>>> engine
{'a': {'b': [1, 2, 3, 4]}}
"""

import collections
import logging, time, datetime
from tornado import stack_context
from tornado.ioloop import IOLoop

import asyncmongo

import tree

"""like pydispatcher, this is more simple"""
class Dispatcher(object):
    """
    >>> def f(x): print x
    >>> d = Dispatcher()
    >>> d.connect('foo', f)
    >>> d.live_signals
    ['foo']
    >>> d.send('foo', 'bar')
    bar
    >>> d.disconnect(f)
    >>> d.live_signals
    []
    """
    def __init__(self):
        self._signals = {} # signal => [callback, ..]
        self._callbacks = {} # callback => signal

    def connect(self, signal, callback):
        cs = self._signals.setdefault(signal, [])
        cs.append(callback)
        self._callbacks.setdefault(callback, signal)
        # TODO:
        # cs.append(stack_context.wrap(callback))

    def disconnect(self, callback):
        signal = self._callbacks.pop(callback)
        if signal:
            cs = self._signals.get(signal)
            if cs:
                cs.remove(callback)

    @property
    def live_signals(self):
        return self._signals.keys()

    def send(self, signal, value):
        try:
            # pop them is expensive
            cs = self._signals.pop(signal)
        except:
            logging.warning('no listener signal %s fired' % signal)
            return
        
        for callback in cs:
            try:
                callback(value)
            except:
                logging.exception('send callback')
                continue


class State(object):
    """
    a deque for calc interval
    >>> s = State()
    >>> s.update()
    >>> s.update()
    >>> s.interval > 0
    True
    """
    def __init__(self):
        self.interval = None
        self.history = collections.deque(maxlen=10)

    def update(self):
        self.history.append(datetime.datetime.now())

        if len(self.history) >= 2:
            self.interval = self.calc()

    def calc(self):
        ret = []
        for i,x in enumerate(self.history):
            if i == 0: continue
            delta = x - self.history[i-1]
            ret.append(delta.microseconds)
        return sum(ret) / len(ret)

class Engine(dict):
    """
    >>> e = Engine()
    >>> e.update('foo', {})
    >>> e.update('foo', {})
    >>> e.update('foo', {})
    >>> e.update('foo', {})
    >>> e.state('foo').interval > 0
    True
    >>> len(e.state_map) == 1
    True
    >>> e.update('bar', {})
    >>> len(e.state_map) == 2
    True
    """
    def __init__(self):
        self.state_map = {} # key => State()
        self.update_keys = set()

    def update(self, k, d):
        rd = self.setdefault(k, {})
        tree.merge(rd, d)

        self.update_keys.add(k)

        # TODO: realy need this?
        s = self.state_map.setdefault(k, State())
        s.update()

    def query(self, keys):
        return tree.query(self, keys)

    def state(self, k):
        return self.state_map.get(k, None)

    def _insert_callback(self, response, error):
        logging.debug('dump once: %r', response)
        if error:
            logging.error('dump failed: %r', error)

    def dump(self, col):
        for k in self.update_keys:
            v = self.get(k)
            if not v: continue
            try:
                col.insert({'key': k, 'when':datetime.datetime.utcnow(),
                            'data': v}, 
                            callback=self._insert_callback)
            except Exception,e:
                logging.error('insert failed %r key:%s' % (e, k))

        # TODO: only shrink update_keys
        for k in self.update_keys:
            v = self.get(k)
            tree.shrink(v)

        # TODO: remove tool old keys
        self.clear()

        self.update_keys.clear()
        
        

# TODO: once
engine = Engine()

# TODO: move into engine? with flag
waiters = Dispatcher()

# TODO: move into engine? with flag
db = None
_last_update = None
_last_dump = None
tick_interval = 60 # 
_tick_install = False

def update(k, d):
    # notify reatime listener(s)
    assert isinstance(k, str)
    kd = {k : d}
    lives = [signal for signal in waiters.live_signals 
             if tree.keyin(signal, kd)]
    #print 'candidate keys:', lives
    for key in lives:
        print 'query', key, 'in', kd
        assert isinstance(key, str)
        ret = [x for x in tree.query(kd, key)]
        waiters.send(key, ret)

    # merge
    engine.update(k, d)

    # need dump tree?
    # TODO: move into Engine?
    global _last_update, _last_dump
    now = time.time()
    if _last_dump is None or now - _last_dump > tick_interval:
        tick_later()
    _last_update = time.time()

def init_db():
    logging.info('core.init_db')
    global db
    db = asyncmongo.Client(pool_id="test",
                           host='10.22.206.206', # TODO: read from conf
                           port=27017,
                           mincached=5,
                           maxcached=15,
                           maxconnections=30,
                           dbname='peach')

    io = IOLoop.instance()
    io.add_timeout(time.time() + tick_interval, tick)

def tick_later():
    global _tick_install
    if _tick_install:
        return
    io = IOLoop.instance()
    io.add_timeout(time.time() + tick_interval, tick)
    _tick_install = True

def tick():
    global db, _last_dump, _tick_install

    if db is None:
        init_db()
    
    engine.dump(db.trend)

    _last_dump = time.time()
    _tick_install = False
