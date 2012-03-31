import os, logging, re

from tornado.web import FallbackHandler, RequestHandler, Application
import tornado.web

import core

class GetHandler(RequestHandler):
    FILTER = r'/trend/(.*)'
    @tornado.web.asynchronous
    def get(self, name):
        # query name order by when
        pass

    def _callback(self):
        # 
        pass
""""

/tree   |  /realtime/a.b
 a      |
 a.b    |
 a.b.c  |---------------------
        | /trend/a.b?period=5m
        | /trend/a.b?period=1h
/fav    | /trend/a.b?period=1w
 c.d    | /trend/a.b?period=3y
        | /trend/a.b?period=all

ip1  => { net: {}, cpu: {1, [90, 80]} }
ip1  => { net: {}, cpu: {1, [80, 82]} }



"""