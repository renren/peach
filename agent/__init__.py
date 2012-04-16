from __future__ import print_function

import optparse
import sys
import time
import glob
import os.path
import logging
import json
import pprint
import urllib2, urllib

import peach.agent.iface
import yaml

def push_once(url, name, tree):
    s = json.dumps({name: tree})
    s = urllib.urlencode({"json": s})
    f = urllib2.urlopen(url, s)
    f.read()

class PythonModules():
    def __init__(self):
        self._modules = {}

    def modules(self, path=None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), 'modules')

        for f in glob.glob('%s/*.py' % path):
            name,_ =  os.path.splitext(os.path.basename(f))
            if name == '__init__':
                continue

            yield 'peach.agent.modules.%s' % name

    def load(self, module_name):
        try:
            mod = __import__(module_name, None, None, ['metric_init'])
            # print module_name, dir(mod)
        except ImportError, err:
            logging.exception('%s import failed' % module_name)
            raise

        self._modules[module_name] = mod
        return mod

    def load_all(self):
        for name in self.modules():
            self.load(name)

    def run(self):
        tree = {}
        for mod_name, mod in self._modules.iteritems():
            try:
                desc = mod.metric_init([]) # TODO: use pyconf as params

                for d in desc:
                    name = d['name']
                    r = d['call_back'](name)
                    if 'float' == d['value_type']:
                        tree.setdefault(name, float(d['format'] % r))
                    else:
                        tree.setdefault(name, int(d['format'] % r))
            except Exception:
                logging.exception('%s run failed' % mod_name)
                logging.debug(dir(mod))
        return tree

def main(args):
    logging.basicConfig(level=logging.DEBUG)

    parser = optparse.OptionParser()
    parser.add_option("-l", "--list", action="store_true", 
                      dest="list_only",
                      help="list all python modules")
    parser.add_option("-c", "--config", 
                      help="config file")
    parser.add_option("-f", "--foreground", dest="daemon", 
                      action='store_false',
                      help="run in foregroud(not daemon)")
    parser.add_option("-i", "--interval", dest="interval", 
                      type="int", default=30,
                      help="run modules once every seconds")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    parser.add_option("-n", "--name", dest="name")
    parser.add_option("-m", "--module", dest="modules", action="append",
                      help="run module once")
    parser.add_option("-s", "--server", dest="server",
                      help="server to push")

    (options, agent_args) = parser.parse_args(args)

    pm = PythonModules()

    if options.list_only:
        for x in pm.modules():
            print('\t %s' % x)
        return 0

    if options.modules:
        for mod_name in options.modules:
            try:
                pm.load(mod_name)
            except ImportError:
                print('%s load failed' % mod_name, file=sys.stderr)
    else:
        pm.load_all()

    name = options.name
    if not name:
        name = iface.uniqif()

    if options.daemon:
        createDaemon()

    url = options.server
    interval = options.interval

    while pm._modules:
        start = time.time()

        tree = pm.run()

        if url:
            push_once(url, name, tree)
        else:
            pprint.pprint(tree)
        
        time.sleep(max(interval, interval - (time.time() - start)))
