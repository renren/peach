"""
>>> def p(v):
...    print 'callback got:', v
>>> waiters.connect('foo,bar', p)

>>> update('foo', {'foo':{'bar':3}}) #doctest: +SKIP
callback got: {'foo,bar': 3}

>>> waiters.disconnect('foo,bar', p)
>>> update({'foo':{'bar':4}}) #doctest: +SKIP
>>> _tree #doctest: +SKIP
{'foo': {'bar': [3, 4]}}
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
    """
    def __init__(self):
        self._signals = {}

    def connect(self, signal, callback):
        cs = self._signals.setdefault(signal, [])
        cs.append(callback)
        # cs.append(stack_context.wrap(callback))

    def disconnect(self, signal, callback):
        # TODO: ugly signal argument, work with callback only!
        cs = self._signals.get(signal, None)
        if cs:
            # TODO: support stack_context
            cs.remove(callback)

    def get_receivers(self):
        pass

    @property
    def live_signals(self):
        return self._signals.keys()

    def send(self, signal, value):
        try:
            # pop them is expensive
            cs = self._signals.pop(signal)
        except:
            logging.exception('send pop failed')
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
        self.to_dump_keys = set()

    def update(self, k, d):
        rd = self.setdefault(k, {})
        tree.merge(rd, d)

        self.to_dump_keys.add(k)

        s = self.state_map.setdefault(k, State())
        s.update()

    def state(self, k):
        return self.state_map.get(k, None)

    def _insert_callback(self, response, error):
        logging.debug('dump once: %r', response)
        if error:
            logging.error('dump failed: %r', error)

    def dump(self, col):
        if True:
            for k in self.to_dump_keys:
                v = self.get(k)
                if not v: continue
                col.insert({
                            'key': k, 'when':datetime.datetime.utcnow(),
                            'data': v}, callback=self._insert_callback)

        self.to_dump_keys.clear()

        # TODO: shrink self
        tree.shrink(self)

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
    lived = [key for key in waiters.live_signals if tree.keyin(key, d)]
    #print 'live', waiters.live_signals, lived, k,d.keys()
    for key in lived:
        fd = {}
        for ks, x in tree.query(d, key):
            fd[','.join(ks)] = x
        #print 'fire', key, fd
        waiters.send(key, fd)

    engine.update(k, d)

    # need dump tree?
    global _last_update, _last_dump
    now = time.time()
    if _last_dump is None or now - _last_dump > tick_interval:
        tick_later()
    _last_update = time.time()


def init():
    logging.info('core.init')
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
        init()
    
    engine.dump(db.trend)

    _last_dump = time.time()
    _tick_install = False
