#!/usr/bin/env python

import datetime
import logging
import asyncmongo
import pymongo

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class TrendStorage:
    def __init__(self):
        #config = load(file("config.yml"))['mongo']
        #logging.info(config)
        self._db = pymongo.Connection('10.22.206.206', 27017)['peach']
        """
        self._db = asyncmongo.Client(pool_id="test",
            host='10.22.206.206', # TODO: read from conf
            port=27017,
            mincached=5,
            maxcached=15,
            maxconnections=30,
            dbname='peach'
       )
	"""

    def get(self, key, period=None):
        #result = self._db.trend.find({'key': key}, limit=1, callback=self._on_response)
        condition = {'key': key}
        if period: 
            condition['when'] = {"$gte": period['start'], "$lt": period['end']}
        result = self._db.trend.find({'key': key}, limit=10).sort("x", pymongo.ASCENDING)
        for r in result:
            yield {'key': r['key'], 'data': r['data']}

    def _on_response(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)
        "[response:%s]" % response

ts = TrendStorage()

if __name__ == "__main__":
    p_end = datetime.datetime.utcnow()
    p_start = p_end - datetime.timedelta(minutes=10)
    period={'start': p_start, 'end': p_end}
    print [t for t in ts.get('br', period)]
