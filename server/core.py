"""
>>> def p(v):
...    print 'callback got:', v
>>> waiters.connect('foo,bar', p)

>>> update({'foo':{'bar':3}})
callback got: {'foo,bar': 3}

>>> waiters.disconnect('foo,bar', p)
>>> update({'foo':{'bar':4}})
>>> _tree
{'foo': {'bar': [3, 4]}}
"""

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


# TODO: once
_tree = {}
waiters = Dispatcher()

db = None
_last_update = None
_last_dump = None
dump_interval = 10
_tick_install = False

def update(d):
    lived = [key for key in waiters.live_signals if tree.keyin(key, d)]
    #print 'live', waiters.live_signals, lived
    for key in lived:
        fd = {}
        for ks, x in tree.query(d, key):
            fd[','.join(ks)] = x
        #print 'fire', key, fd
        waiters.send(key, fd)

    # update
    #print 'update:', d
    tree.merge(_tree, d)

    # need dump tree?
    global _last_update, _last_dump
    now = time.time()
    if _last_dump is None or now - _last_dump > dump_interval:
        tick_later()
    _last_update = time.time()

def init():
    logging.info('core.init')
    global db
    db = asyncmongo.Client(pool_id="test",
                           host='10.22.206.206',
                           port=27017,
                           mincached=5,
                           maxcached=15,
                           maxconnections=30,
                           dbname='test')

    io = IOLoop.instance()
    io.add_timeout(time.time() + dump_interval, tick)

def _on_tick(response, error):
    logging.debug('tick once: %r', response)
    if error:
        logging.error('tick failed: %r', error)

def tick_later():
    global _tick_install
    if _tick_install:
        return
    io = IOLoop.instance()
    io.add_timeout(time.time() + dump_interval, tick)
    _tick_install = True

def tick():
    global db, _last_dump, _tick_install

    if db is None:
        init()
    
    db.test.insert({'tree':_tree,
        'when':datetime.datetime.utcnow()
        }, callback=_on_tick)

    _last_dump = time.time()
    _tick_install = False
