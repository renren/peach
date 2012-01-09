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

class PullHandler(RequestHandler):
    @tornado.web.asynchronous
    def get(self, name):
        self._name = name
        app.waiters.add(name, self._on_fire)
        #d = app.tree.find(name)
        #if d: self.write(d)

    def on_connection_close(self):
        app.waiters.remove(self._name, self._on_fire)

    def _on_fire(self, value):
        self.write(value)
        self.finish()

def main():
    settings = dict(
            debug=True,
            cookie_secret="43oETzKXQBGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            #xsrf_cookies=True,
            autoescape="xhtml_escape",
        )

    application = Application([
        (r"/tornado", MainHandler),
        (r"/pull/([^/]+)", PullHandler),
        (r".*", FallbackHandler, dict(fallback=WSGIContainer(app))),
        ], **settings)
    application.listen(8000, '127.0.0.1')
    io = IOLoop.instance()

    #io.add_timeout(
    
    io.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()


