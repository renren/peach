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
        x = core.engine.query(name)
        if not x:
            raise tornado.web.HTTPError(400)
        a = [i for i in x]
        # print 'query:', a
        self.write(tornado.escape.json_encode(a))

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
        GET /api/push/a.b.c=1,a.d=2
        update(a, {b: {c: 1}})
        """
        name = name.encode('utf8')
        arr = name.split(',')
        d = {}
        for a in arr:
            pair = a.split('=')
            if len(pair) != 2:
                continue
            d.setdefault(pair[0], tonumber(pair[1]))
            #self._push(pair[0], pair[1])
        core.update(d)
        self.write('')

    def post(self, name):
        name = name.encode('utf8')
        pass
        # body => dict
        # self._push(name, self.body)
