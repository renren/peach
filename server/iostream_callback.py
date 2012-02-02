"""
See this post for the motivation behind this gist:

  http://rctay.tuletech.com/2010/12/tornado-presenting-a-new-paradigm-for-IOStream-read-callbacks

An example of callbacks built on this:

  https://gist.github.com/753992

"""

from tornado import web

DONE = (0, )


class Data(object):
    def __init__(self):
        self.state = None


class Callback(object):
    start_state = None
    entry_callback = None

    def __init__(self, data, entry_expr):
        self.data = data
        self.entry_expr = entry_expr

        self._entered = False

    @property
    def has_changed(self):
        return self.data.state is not self.start_state

    def enter(self):
        assert not self.has_changed

        self._entered = True
        self.entry_expr(self)
        self._entered = False

        return self.has_changed

    def __call__(self, *args, **kwargs):
        assert self.data.state is self.start_state

        self._handle(*args, **kwargs)
        if not self._entered:
            self.entry_callback()

    def _handle(self, *args, **kwargs):
        raise NotImplementedError()

    @staticmethod
    def make_entry_callback(data, callbacks, done_callback=None):
        def func():
            while data.state is not DONE:
                for callback in callbacks:
                    if data.state is callback.start_state:
                        if not callback.enter():
                            # callback did not return immediately
                            return

            # done reading chunks
            assert data.state is DONE
            if done_callback:
                done_callback(data)

        # setup callbacks
        for callback in callbacks:
            callback.entry_callback = func

        return func
