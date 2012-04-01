import os, logging, re, datetime

from tornado.web import FallbackHandler, RequestHandler, Application
import tornado.web
import json
import asyncmongo

from trend_storage import ts

class GetHandler(RequestHandler):
    FILTER = r'/trend/(.*)'
    def get(self, name):
        # query name order by when
        key = name.encode('utf8')

        p_end = datetime.datetime.utcnow()
        p_start = p_end - datetime.timedelta(minutes=10)
        period={'start': p_start, 'end': p_end}

        values = [v for v in ts.get(key, period)]
        if len(values) > 0:
            self.write(json.dumps(values[0]))
        else:
            logging.info("[[_%s_]]" % values)
            self.write("{}")

    def _callback(self, name):
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
