import os, glob, logging
import json
import optparse
import urllib2, urllib

import yaml

from peach.agent.modules import ganglia_c_module
from peach.agent.modules import lazy

@lazy.memoized
def cached():
    return PythonModule(), ganglia_c_module.GangliaModule()

push_count = 0

def push_once(url):
    mpy, mc = cached()

    tree = mpy.run()
    tree.update(mc.run())

    print tree
    return

    global push_count
    push_count += 1

    s = json.dumps({'foo.54': tree})
    s = urllib.urlencode({"json": s})
    f = urllib2.urlopen(url, s)
    f.read()

class PythonModule():
    def __init__(self):
        self.modules = []
        self.init()

    @staticmethod
    def modules(path=None):
        if path is None: path='modules'

        for f in glob.glob('%s/*.py' % path):
            name,_ =  os.path.splitext(f)
            arr = name.split('/')
            if arr[len(arr)-1] == '__init__':
                continue

            name = name.replace('/', '.')
            yield name

    def init(self, path=None):
        if path is None: path='modules'

        for f in glob.glob('%s/*.py' % path):
            name,_ =  os.path.splitext(f)
            name = name.replace('/', '.')
            try:
                m = __import__(name)
                if not m.metric_init:
                    sys.modules.pop(name, None)
            except:
                logging.exception('module %s load failure' % m)
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
            except:
                logging.exception('run module %r' % m)
        return tree

def mid(t, a, b):
    """
    >>> mid('abc', 'a', 'b')
    ''
    >>> mid('abcde', 'b', 'd')
    'c'
    >>> mid('abcde', 'a', 'd')
    'bc'
    >>> mid('abc', 'a', 'c')
    'b'
    >>> mid('ab', 'a', 'b')
    ''
    >>> mid('ab', 'a', 'd')
    >>> mid('ab', 'c', 'd')
    """
    ia = t.find(a)
    if -1 != ia:
        ia += len(a)
        ib = t.find(b, ia)
        if -1 != ib:
            return t[ia : ib]
    return None


def dump():
    import gc
    a = gc.get_objects()
    t = {}

    for i in a:
        n = '%r' % type(i)
        n = mid(n, '\'', '\'')
        if n in t:
            t[n] += 1
        else:
            t[n] = 1
    return {'gc': t}

def main():
    y = yaml.load(open('agent.conf', 'rb'))

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
    
    #print options, args

    if options.list_pymodules:
        for x in PythonModule.modules():
            print ' ', x

    exit()
    logging.basicConfig(level=logging.DEBUG)
    main()
