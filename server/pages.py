import time
import json # TODO: more efficient

from flask import Flask, request, render_template, url_for, redirect, Response, jsonify
from tornado import stack_context

from tree import Tree, keyin


class NotifyTable():
    def __init__(self):
        self._dict = {}

    def add(self, name, callback):
        cs = self._dict.setdefault(name, [])
        # cs.append(callback)
        cs.append(stack_context.wrap(callback))

    def remove(self, name, callback):
        cs = self._dict.get(name, None)
        if cs:
            # TODO: here wrong
            print cs, callback
            cs.remove(callback)

    @property
    def keys(self):
        return self._dict.keys()

    def fire(self, name, val):
        try:
            print 'fire', name
            cs = self._dict.pop(name)
        except:
            # TODO: log
            return
        
        for callback in cs:
            try:
                callback(val)
            except:
                continue

app = Flask(__name__)

app.debug = True
app.tree = Tree()
app.waiters = NotifyTable()


"""
/push  
  form field support json/accesslog  
  json -> merge into core tree  
  accesslog -> pipes -> tree -> merge into core tree  
  
/pull/?key-br  
/pull/?key-br,ie  
/pull/?key-br,ie,7  
  comet, repsonse in json list  
    [{br,ie,7 : 2328},  
    {br,ie,sogou,3 : 323}]  
/get/<name>
  response immediatly in json list
"""

@app.route('/push', methods=['GET', 'POST'])
def push():
    if request.method == 'POST':
        j = request.form['json'].encode('utf-8')
        d = json.loads(j)
        app.tree.merge(d)

        #
        if isinstance(d, dict):
            for key in [key for key in app.waiters.keys if keyin(key, d)]:
                fd = {}
                for ks, x in app.tree.find(key):
                    fd[','.join(ks)] = x.value
                app.waiters.fire(key, fd)
    else:
        pass
    return render_template('post.html')

@app.route('/get/<key>', methods=['GET'])
def get(key):
    d = {}
    for ks, item in app.tree.find(key):
        d[','.join(ks)] = item.value

    return jsonify(d)

@app.route('/realtime/<key>', methods=['GET'])
def realtime_view(key):
    d = {}
    for ks, item in app.tree.find(key):
        d[','.join(ks)] = item.value
    type = request.args.get('type', 'spline')
    return render_template('realtime_view.html', key=key, series=d, type=type, now=int(1000*time.time()))

@app.route('/flask')
def hello_world():
  return 'This comes from Flask ^_^'


