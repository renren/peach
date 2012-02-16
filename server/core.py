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

import logging
from tornado import stack_context
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

