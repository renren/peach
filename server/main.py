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
        self._name = name
        app.waiters.connect(name, self._on_fire)

    def on_connection_close(self):
        app.waiters.disconnect(self._name, self._on_fire)

    def _on_fire(self, value):
        self.write(tornado.escape.json_encode(value))
        self.finish()

def main():
    
    settings = dict(
            debug=True,
            cookie_secret="43oETzKXQBGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            autoescape="xhtml_escape",
        )

    import api

    application = Application([
        (r"/", MainHandler),
        (r"/tornado", MainHandler),
        (r"/pull/([^/]+)", PullHandler),
        (api.GetHandler.FILTER, api.GetHandler),
        (api.PushHandler.FILTER, api.PushHandler),
        (api.TreeHandler.FILTER, api.TreeHandler),
        (r".*", FallbackHandler, dict(fallback=WSGIContainer(app))),
        ], **settings)
    try:
        application.listen(80)
    except:
        application.listen(8000)
    io = IOLoop.instance()

    #io.add_timeout(core.tick)
    
    io.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()


