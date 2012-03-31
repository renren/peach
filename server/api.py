import os, logging, re

from tornado.web import FallbackHandler, RequestHandler, Application
import tornado.web
import tornado.escape

import core

class TreeHandler(RequestHandler):
    FILTER = r'/tree/(.*)'
    #@tornado.web.asynchronous
    def get(self, name):
        name = name.encode('utf8')
        if name:
            d = core.engine.get(name)
        else:
            d = core.engine
        if d:
            # TODO: sort keys
            self.write(tornado.escape.json_encode(d.keys()))
        self.write('')

class GetHandler(RequestHandler):
    FILTER = r'/api/get/(.*)'
    #@tornado.web.asynchronous
    def get(self, name):
        name = name.encode('utf8')
        #name = name.replace('.', ',')
        x = core.engine.query(name)
        if not x:
            raise HTTPError(400)
        a = [i for i in x]
        print 'query:', a
        self.write('%r' % a)

    def on_connection_close(self):
        pass

def tonumber(x):
    try:
        i = int(x)
        if str(i) == str(x):
            return i
    except:
        pass
    return float(x)

class PushHandler(RequestHandler):
    FILTER = r'/api/push/(.*)$'
    def get(self, name):
        """ 
        GET /api/push/a.b.c=1
        update(a, {b: {c: 1}})
        """
        name = name.encode('utf8')
        arr = name.split('=')
        if len(arr) != 2:
            raise HTTPError(400)
        self._push(arr[0], arr[1])
        self.write('')

    def post(self, name):
        name = name.encode('utf8')
        pass
        # body => dict
        # self._push(name, self.body)

    def _push(self, key, value):
        value = tonumber(value)

        a = key.split('.')
        d = {}
        sd = d
        # print 'make dict from', a[1:len(a)-1]
        for x in a[1:len(a)-1]:
            sd = sd.setdefault(x, {})
        sd.setdefault(a[len(a) - 1], value)
        # print 'push:', a[0], d
        core.update(a[0], d)