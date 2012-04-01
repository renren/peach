import os, logging
from cStringIO import StringIO

from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, RequestHandler, Application
import tornado.web
import tornado.escape

# https://gist.github.com/1510715
# https://gist.github.com/753992
from chunked_handler import ChunkedHandler
from pages import app
import pipeline
import tree

class MainHandler(ChunkedHandler):
    def get(self):
        self.render('index.html')

    def put(self):
        if not self._handle_chunked():
            f = StringIO(self.request.body)
            logging.debug('/put %d bytes', len(self.request.body))
            self.process(f)
            self.write('')

    def _on_chunks(self, chunk):
        #super(MainHandler, self)._on_chunks(all_chunks)
        print 'chunk length', chunk.tell()
        chunk.seek(0, 0)
        self.process(chunk)
        self.write('')
        self.finish()
    
    def process(self, f):
        try:
            pipeline.run(f)
        except:
            logging.exception('put failed')

class PullHandler(RequestHandler):
    @tornado.web.asynchronous
    def get(self, name):
        name = name.encode('utf8')
        self._name = name
        app.waiters.connect(name, self._on_fire)

    def on_connection_close(self):
        app.waiters.disconnect(self._on_fire)

    def _on_fire(self, value):
        x = [i for i in tree.expand(value)]
        #print 'fire', value, x
        self.write(tornado.escape.json_encode(value))
        self.finish()

class RealtimeViewHandler(RequestHandler):
    FILTER = r'/realtime/([^/]+)'
    def get(self, name):
        name = name.encode('utf8')
        self.render('realtime.html', key='a.b')

def main():
    import api, trend

    settings = dict(
            debug=True,
            cookie_secret="43oETzKXQBGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            autoescape="xhtml_escape",
        )

    urls = [
        (r"/", MainHandler),
        (r"/tornado", MainHandler),
        (r"/pull/([^/]+)", PullHandler),
        (r"/trend/([^/]+)", trend.GetHandler),
        (api.GetHandler.FILTER, api.GetHandler),
        (api.PushHandler.FILTER, api.PushHandler),
        (api.TreeHandler.FILTER, api.TreeHandler),
        (RealtimeViewHandler.FILTER, RealtimeViewHandler),
        (r".*", FallbackHandler, dict(fallback=WSGIContainer(app))),
        ]

    application = Application(urls, **settings)
    try:
        application.listen(80, '0.0.0.0')
    except:
        application.listen(8000, '0.0.0.0')
    io = IOLoop.instance()
    io.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
