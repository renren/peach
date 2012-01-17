from tornado import stack_context

import tree

# 
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
            cs = self._signals.pop(signal)
        except Exception,e:
            # TODO: log
            print e
            return
        
        for callback in cs:
            try:
                callback(value)
            except Exception,e:
                # TODO: log?
                print e
                continue


# TODO: once
_tree = tree.Tree()
waiters = Dispatcher()

def update(key, d):
    _tree.merge(d)
    for key in [key for key in waiters.live_signals if tree.keyin(key, d)]:
        fd = {}
        for ks, x in _tree.find(key):
            fd[','.join(ks)] = x.value
        waiters.send(key, fd)