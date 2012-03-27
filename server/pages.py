import time
try:
    import simplejson as json
except:
    import json

from flask import Flask, request, render_template, url_for, redirect, Response, jsonify, make_response

import tree
import core
import pipeline

app = Flask(__name__)

app.debug = True
app.waiters = core.waiters

#app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='favicon.ico'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/push', methods=['GET', 'POST'])
def push():
    if request.method == 'POST':
        d = {}
        if 'json' in request.form:
            j = request.form['json'].encode('utf-8')
            d = json.loads(j)

            # TODO: k
            k = d.keys()[0]
            core.update(k, d)

        elif 'k' in request.form and 'v' in request.form:
            key = request.form['k'].encode('utf-8')
            value = request.form['v'].encode('utf-8')
            # TODO:
    
    return render_template('post.html')

@app.route('/raw', methods=['POST', 'PUT'])
def raw():
    f = request.stream
    pipeline.run(f)
    return redirect(url_for('static', filename="post.html"))

def as_dict(o):
    if issubclass(o.__class__, tree.Item):
        return o.value
    return o

@app.route('/all')
def all():
    #return jsonify(core.engine._dict)
    return Response(json.dumps(core.engine,indent=None if request.is_xhr else 2), mimetype='application/json')
    

def getmatch(key):
    d = []
    for ks, item in tree.query(core.engine, key):
        d.append((','.join(ks), item))

    d.sort(key=lambda x: x[0])
    return d

@app.route('/get/<key>', methods=['GET'])
def get(key):
    d = getmatch(key)
    #return jsonify(d)
    return Response(json.dumps(d, indent=None if request.is_xhr else 2), mimetype='application/json')

@app.route('/realtime/<key>', methods=['GET'])
def realtime_view(key):
    d = getmatch(key)
    type = request.args.get('type', 'spline')
    return render_template('realtime_view.html', key=key, series=d, type=type, now=int(1000*time.time()))

@app.route('/flask')
def hello_world():
  return 'This comes from Flask ^_^'
