from flask import Flask, request, render_template, url_for, redirect, Response

from tornado import stack_context

from data import Tree
import json

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

    def fire(self, name, val):
        try:
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

@app.route('/push', methods=['GET', 'POST'])
def push():
    if request.method == 'POST':
        j = request.form['json'].encode('utf-8')
        # print 'got', type(j), j
        d = json.loads(j)
        app.tree.merge(d)
        if isinstance(d, dict):
            for k, v in d.iteritems():
                app.waiters.fire(k, d)
    else:
        pass
    return render_template('post.html')

@app.route('/flask')
def hello_world():
  return 'This comes from Flask ^_^'
