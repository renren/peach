"""
agent  ---->   server   ----> DB
                /             |
               /              |
          realtime        trend web

agent.Agent.run/init
      push_once

server.routeto(url)
       start(host, port)
       main
       

"""


import os, logging

from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, RequestHandler, Application
import tornado.web

from pages import app

class MainHandler(RequestHandler):
    def get(self):
        self.write("This message comes from Tornado ^_^")

    def put(self):
        print 'put body:', len(self.request.body), type(self.request)
        f = self.request.connection.stream
        f.read_bytes(10, self._readed)
        self.write('')

    def _readed(self, data):
        print len(data)

class PullHandler(RequestHandler):
    @tornado.web.asynchronous
    def get(self, name):
        self._name = name
        app.waiters.connect(name, self._on_fire)

    def on_connection_close(self):
        app.waiters.disconnect(self._name, self._on_fire)

    def _on_fire(self, value):
        self.write(value)
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

    application = Application([
        (r"/tornado", MainHandler),
        (r"/pull/([^/]+)", PullHandler),
        (r".*", FallbackHandler, dict(fallback=WSGIContainer(app))),
        ], **settings)
    application.listen(8000)
    io = IOLoop.instance()

    #io.add_timeout(
    
    io.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()


