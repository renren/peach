import os, glob, logging
import json
import urllib2, urllib

import modules.ganglia_c_module

def push_once(url):
    tree = PythonModule().run()

    gm = modules.ganglia_c_module.GangliaModule()
    tree.update(gm.run())

    s = json.dumps({'127.0.0.1': tree})
    s = urllib.urlencode({"json": s})
    f = urllib2.urlopen(url, s)
    f.read()

def register(f):
    pass


class PythonModule():
    def __init__(self):
        self.modules = []
        self.init()

    def init(self, path=None):
        if path is None:
            path='modules'
        for f in glob.glob('%s/*.py' % path):
            name,_ =  os.path.splitext(f)
            name = name.replace('/', '.')
            try:
                m = __import__(name, globals())
            except Exception,e:
                logging.debug('module %s load failure %r' % (name, e))
                continue

            _, base = name.split('.')
            self.modules.append(getattr(m, base))

    def run(self):
        tree = {}
        for m in self.modules:
            try:
                desc = m.metric_init([]) # TODO: use pyconf as params

                for d in desc:
                    name = d['name']
                    r = d['call_back'](name)
                    tree.setdefault(name, float(d['format'] % r))
            except Exception,e:
                logging.debug('run module %r failed %r' % (m,e))
        return tree

def main():
    import sys
    import time
    if len(sys.argv)>1:
        url = sys.argv[1]
    else:
        url = 'http://127.0.0.1/push'
    while True:
        start = time.time()
        push_once(url)
        time.sleep(max(1, (1 - time.time() + start)))

if __name__ == '__main__':
    # --push
    # --debug -d
    logging.basicConfig(level=logging.DEBUG)
    main()
